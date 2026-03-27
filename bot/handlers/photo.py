import asyncio
import logging
from io import BytesIO

from aiogram import Bot, F, Router
from aiogram.types import BufferedInputFile, InlineKeyboardButton, InlineKeyboardMarkup, Message

from services.replicate_api import ReplicateService, ReplicateUpscaleError
from services.user_db import UserDB

logger = logging.getLogger(__name__)
router = Router()

_SUPPORTED_MIME = {"image/jpeg", "image/png", "image/webp"}


def _progress_bar(filled: int, total: int = 10) -> str:
    filled = min(filled, total)
    return "█" * filled + "░" * (total - filled)


async def _animate_progress(msg) -> None:
    for filled in range(1, 10):  # заполняем до 90% за ~63 сек
        await asyncio.sleep(7)
        bar = _progress_bar(filled)
        pct = filled * 10
        try:
            await msg.edit_text(f"⏳ Улучшаю фото...\n{bar} {pct}%")
        except Exception:
            return


@router.message(F.photo | F.document)
async def handle_photo(message: Message, bot: Bot, replicate: ReplicateService, user_db: UserDB, admin_id: int | None) -> None:
    # Prioritize document (uncompressed) over photo (Telegram compresses photos)
    if message.document:
        doc = message.document
        if doc.mime_type not in _SUPPORTED_MIME:
            await message.answer("Поддерживаются только JPEG, PNG и WebP.")
            return
        if doc.file_size and doc.file_size > 20 * 1024 * 1024:
            await message.answer("Файл слишком большой. Максимальный размер — 20 МБ.")
            return
        file_id = doc.file_id
        quality_note = ""
    elif message.photo:
        photo_obj = message.photo[-1]
        if photo_obj.file_size and photo_obj.file_size > 20 * 1024 * 1024:
            await message.answer("Файл слишком большой. Максимальный размер — 20 МБ.")
            return
        file_id = photo_obj.file_id
        quality_note = "\n\nДля лучшего результата отправляйте фото как файл (документ) — так Telegram не сжимает изображение."
    else:
        await message.answer("Пожалуйста, отправьте фотографию или изображение как файл.")
        return

    await user_db.register_user(message.from_user.id, message.from_user.username)

    is_admin = admin_id is not None and message.from_user.id == admin_id
    if not is_admin and not await user_db.has_free_generations_left(message.from_user.id):
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="💳 Пополнить баланс", callback_data="topup_balance")
        ]])
        await message.answer(
            "❌ Бесплатные генерации закончились.\nПополните баланс, чтобы продолжить.",
            reply_markup=kb,
        )
        return

    status_msg = await message.answer("⏳ Улучшаю фото...\n░░░░░░░░░░ 0%")
    progress_task = asyncio.create_task(_animate_progress(status_msg))

    try:
        file = await bot.get_file(file_id)
        buf = BytesIO()
        await bot.download_file(file.file_path, destination=buf)
        image_bytes = buf.getvalue()

        result_bytes = await asyncio.wait_for(replicate.process(image_bytes), timeout=120)

        output = BufferedInputFile(result_bytes, filename="upscaled.png")
        await message.answer_document(output, caption="✅ Готово!" + quality_note)
        await user_db.increment_generations(message.from_user.id)
        logger.info("Sent result to user %d (%d bytes)", message.from_user.id, len(result_bytes))

    except ReplicateUpscaleError as e:
        logger.error("Upscale failed for user %d: %s", message.from_user.id, e)
        await message.answer("❌ Не удалось обработать фото. Попробуйте позже.")
    except asyncio.TimeoutError:
        await message.answer("⏰ Обработка заняла слишком много времени. Попробуйте позже.")
    except Exception as e:
        logger.exception("Error processing photo for user %d: %s", message.from_user.id, e)
        await message.answer("❌ Произошла ошибка при обработке фото. Попробуйте ещё раз.")
    finally:
        progress_task.cancel()
        await status_msg.delete()
