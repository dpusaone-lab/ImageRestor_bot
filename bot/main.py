import asyncio
import logging
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from config import load_config
from handlers import photo, start, payments
from middlewares.throttle import ThrottleMiddleware
from services.replicate_api import ReplicateService
from services.user_db import UserDB

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler("bot.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


async def main() -> None:
    config = load_config()

    proxy_session = AiohttpSession(proxy="socks5://72.195.34.42:4145")
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        session=proxy_session,
    )
    dp = Dispatcher()

    user_db = UserDB(db_path=config.db_path, free_limit=config.free_limit)
    await user_db.setup()

    dp["replicate"] = ReplicateService(api_token=config.replicate_api_token, prompt=config.fixed_prompt)
    dp["user_db"] = user_db
    dp["free_limit"] = config.free_limit
    dp["admin_id"] = config.admin_id

    photo.router.message.middleware(ThrottleMiddleware())

    dp.include_router(start.router)
    dp.include_router(payments.router)
    dp.include_router(photo.router)

    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
    ])

    logger.info("Starting bot (Replicate API)")
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await user_db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
