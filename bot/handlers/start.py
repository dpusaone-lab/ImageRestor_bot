import logging
import os

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import FSInputFile, Message

from keyboards import main_kb
from services.user_db import UserDB

logger = logging.getLogger(__name__)
router = Router()

EXAMPLE_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "example.jpg")

_WELCOME_TEXT = (
    "🎉 <b>Добро пожаловать в Upscale Bot!</b>\n\n"
    "📸 <b>Фото → 4K:</b> Отправьте фото — бот улучшит его качество с помощью Gemini AI.\n\n"
    "📁 Для лучшего результата присылайте фото <b>как файл</b> (документ) — "
    "Telegram не будет его сжимать."
)


@router.message(CommandStart())
async def cmd_start(message: Message, user_db: UserDB) -> None:
    await user_db.register_user(message.from_user.id, message.from_user.username)
    logger.info("User %d started the bot", message.from_user.id)
    await message.answer(_WELCOME_TEXT, reply_markup=main_kb)


@router.message(F.text == "🏠 Меню")
async def btn_menu(message: Message) -> None:
    await message.answer(_WELCOME_TEXT, reply_markup=main_kb)


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
        "ℹ️ <b>Об этом боте</b>\n\n"
        "Этот бот улучшает качество ваших фотографий до 4K с помощью Gemini AI.\n\n"
        "Просто отправьте фото — бот обработает его и вернёт результат в высоком разрешении.\n\n"
        "Автор: @dpusaone"
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
