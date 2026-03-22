import asyncio
import logging
from io import BytesIO

from aiogram import Bot, Router
from aiogram.types import BufferedInputFile, Message

from services.replicate_api import ReplicateService, ReplicateUpscaleError

logger = logging.getLogger(__name__)
router = Router()

_SUPPORTED_MIME = {"image/jpeg", "image/png", "image/webp"}


@router.message()
async def handle_photo(message: Message, bot: Bot, replicate: ReplicateService) -> None:
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

    status_msg = await message.answer("⏳ Улучшаю фото...")

    try:
        file = await bot.get_file(file_id)
        buf = BytesIO()
        await bot.download_file(file.file_path, destination=buf)
        image_bytes = buf.getvalue()

        result_bytes = await asyncio.wait_for(replicate.process(image_bytes), timeout=120)

        output = BufferedInputFile(result_bytes, filename="upscaled.png")
        await message.answer_document(output, caption="✅ Готово!" + quality_note)
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
        await status_msg.delete()
