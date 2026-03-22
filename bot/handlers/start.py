import logging
import os

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import FSInputFile, Message

logger = logging.getLogger(__name__)
router = Router()

EXAMPLE_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "example.jpg")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    logger.info("User %d started the bot", message.from_user.id)
    await message.answer(
        "Привет! Отправь мне фотографию, и я улучшу её качество до 4K с помощью Gemini AI.\n\n"
        "Просто пришли фото — я сделаю всё остальное."
    )


@router.message(Command("about"))
async def cmd_about(message: Message) -> None:
    await message.answer(
        "Об этом боте\n\n"
        "Этот бот улучшает качество ваших фотографий до 4K с помощью Gemini.\n\n"
        "Просто отправьте фото — бот обработает его и вернёт результат в высоком разрешении.\n\n"
        "Автор: @dpusaone"
    )


@router.message(Command("example"))
async def cmd_example(message: Message) -> None:
    if os.path.exists(EXAMPLE_PATH):
        await message.answer_photo(
            FSInputFile(EXAMPLE_PATH),
            caption="Пример обработки: слева оригинал, справа результат"
        )
    else:
        await message.answer("Пример скоро появится!")
