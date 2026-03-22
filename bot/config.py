from dataclasses import dataclass
from dotenv import load_dotenv
import os


@dataclass
class Config:
    bot_token: str
    replicate_api_token: str
    fixed_prompt: str


def load_config() -> Config:
    load_dotenv()
    bot_token = os.getenv("BOT_TOKEN")
    replicate_api_token = os.getenv("REPLICATE_API_TOKEN")
    fixed_prompt = os.getenv("FIXED_PROMPT", "")

    if not bot_token:
        raise ValueError("BOT_TOKEN is not set")
    if not replicate_api_token:
        raise ValueError("REPLICATE_API_TOKEN is not set")

    return Config(
        bot_token=bot_token,
        replicate_api_token=replicate_api_token,
        fixed_prompt=fixed_prompt,
    )
