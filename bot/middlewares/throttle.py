import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message

logger = logging.getLogger(__name__)


class ThrottleMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.processing_users: set[int] = set()

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id if event.from_user else None
        if user_id is None:
            return await handler(event, data)

        if user_id in self.processing_users:
            logger.info("Throttling user %d", user_id)
            await event.answer("Подождите, ваше предыдущее фото ещё обрабатывается...")
            return

        self.processing_users.add(user_id)
        try:
            return await handler(event, data)
        finally:
            self.processing_users.discard(user_id)
