import logging
import os

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from keyboards import main_kb
from services.user_db import UserDB

logger = logging.getLogger(__name__)
router = Router()

EXAMPLE_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "example.jpg")
PREVIEW_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "preview.jpg")

_WELCOME_TEXT = (
    "Привет! Это Imagerestore AI 📸\n\n"
    "Я помогу восстановить ваши старые снимки, убрать шумы и улучшить "
    "качество фото за считанные секунды.\n\n"
    "Пришлите мне фотографию, которую нужно оживить!\n\n"
    "‼️ <b>Важно:</b> фото обрабатывается около 1 минуты. "
    "Пожалуйста, не отправляйте новое, пока я не закончу с текущим. ‼️"
)

_send_photo_kb = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text="📸 Отправить фото", callback_data="prompt_send_photo")
]])


@router.message(CommandStart())
async def cmd_start(message: Message, user_db: UserDB) -> None:
    await user_db.register_user(message.from_user.id, message.from_user.username)
    logger.info("User %d started the bot", message.from_user.id)
    if os.path.exists(PREVIEW_PATH):
        await message.answer_photo(FSInputFile(PREVIEW_PATH))
    await message.answer(_WELCOME_TEXT, reply_markup=main_kb)


@router.message(F.text == "🏠 Меню")
async def btn_menu(message: Message) -> None:
    await message.answer("🚧 В разработке")


@router.callback_query(F.data == "prompt_send_photo")
async def cb_send_photo(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        "Пришлите фото, и я приступлю к магии! ✨\n\n"
        "⏳ Обработка занимает около 1 минуты. Пожалуйста, не отправляйте "
        "следующее фото, пока я не закончу с текущим."
    )


@router.message(F.text == "💳 Баланс")
async def btn_balance(message: Message, user_db: UserDB, free_limit: int) -> None:
    count = await user_db.get_generation_count(message.from_user.id)
    free_left = max(0, free_limit - count)
    await message.answer(
        f"💳 <b>Баланс</b>\n\n"
        f"Использовано генераций: {count}\n"
        f"Бесплатных осталось: {free_left}"
    )


@router.message(Command("about"))
@router.message(F.text == "👨‍💻 О разработчике")
async def cmd_about(message: Message) -> None:
    await message.answer(
        "ℹ️ <b>Об Imagerestore AI</b>\n\n"
        "Этот бот использует передовые алгоритмы Gemini AI для глубокого анализа и восстановления каждого пикселя.\n\n"
        "<b>Возможности:</b>\n"
        "• Увеличение разрешения до 4K (Ultra HD).\n"
        "• Устранение цифрового шума и «зернистости».\n"
        "• Восстановление чёткости лиц и мелких деталей.\n"
        "• Улучшение цветопередачи.\n\n"
        "<b>Как это работает?</b>\n"
        "Отправьте фото как документ или изображение. Нейросеть проанализирует структуру кадра и восстановит детали, сохраняя естественность.\n\n"
        "👨‍💻 Разработчик: @dpusaone\n"
        "📢 Новости проекта: t.me/singularitytomorrow\n\n"
        "Версия бота: 1.0 (Stable)"
    )


@router.message(Command("example"))
@router.message(F.text == "🖼 Примеры")
async def cmd_example(message: Message) -> None:
    if os.path.exists(EXAMPLE_PATH):
        await message.answer_photo(
            FSInputFile(EXAMPLE_PATH),
            caption="Пример обработки: слева оригинал, справа результат"
        )
    else:
        await message.answer("Пример скоро появится!")
