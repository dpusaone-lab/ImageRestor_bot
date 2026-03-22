import asyncio
import logging
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import load_config
from handlers import photo, start
from middlewares.throttle import ThrottleMiddleware
from services.replicate_api import ReplicateService

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

    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    dp["replicate"] = ReplicateService(api_token=config.replicate_api_token, prompt=config.fixed_prompt)

    photo.router.message.middleware(ThrottleMiddleware())

    dp.include_router(start.router)
    dp.include_router(photo.router)

    logger.info("Starting bot (Replicate API)")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
