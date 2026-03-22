import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    logger.info("User %d started the bot", message.from_user.id)
    await message.answer(
        "Привет! Отправь мне фотографию, и я улучшу её качество до 4K с помощью Gemini AI.\n\n"
        "Просто пришли фото — я сделаю всё остальное."
    )
