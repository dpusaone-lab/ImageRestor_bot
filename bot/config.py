from dataclasses import dataclass
from dotenv import load_dotenv
import os


@dataclass
class Config:
    bot_token: str
    replicate_api_token: str
    fixed_prompt: str
    free_limit: int
    db_path: str
    admin_id: int | None


def load_config() -> Config:
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    replicate_api_token = os.getenv("REPLICATE_API_TOKEN")
    fixed_prompt = os.getenv("FIXED_PROMPT", "")
    free_limit = int(os.getenv("FREE_GENERATION_LIMIT", "1"))
    db_path = os.getenv("DB_PATH", "bot.db")
    admin_id_raw = os.getenv("ADMIN_ID")
    admin_id = int(admin_id_raw) if admin_id_raw else None

    if not bot_token:
        raise ValueError("BOT_TOKEN is not set")
    if not replicate_api_token:
        raise ValueError("REPLICATE_API_TOKEN is not set")

    return Config(
        bot_token=bot_token,
        replicate_api_token=replicate_api_token,
        fixed_prompt=fixed_prompt,
        free_limit=free_limit,
        db_path=db_path,
        admin_id=admin_id,
    )
