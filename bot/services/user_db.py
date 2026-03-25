import logging

import aiosqlite

logger = logging.getLogger(__name__)

_CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    user_id      INTEGER PRIMARY KEY,
    username     TEXT,
    registered_at DATETIME NOT NULL DEFAULT (datetime('now'))
)
"""

_CREATE_GENERATIONS = """
CREATE TABLE IF NOT EXISTS generations (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(user_id),
    created_at DATETIME NOT NULL DEFAULT (datetime('now'))
)
"""


class UserDB:
    def __init__(self, db_path: str, free_limit: int) -> None:
        self._db_path = db_path
        self._free_limit = free_limit
        self._db: aiosqlite.Connection | None = None

    async def setup(self) -> None:
        self._db = await aiosqlite.connect(self._db_path)
        await self._db.execute("PRAGMA foreign_keys = ON")
        await self._db.execute(_CREATE_USERS)
        await self._db.execute(_CREATE_GENERATIONS)
        await self._db.commit()
        logger.info("UserDB ready at %s (free_limit=%d)", self._db_path, self._free_limit)

    async def close(self) -> None:
        if self._db:
            await self._db.close()
            self._db = None

    async def register_user(self, user_id: int, username: str | None) -> None:
        await self._db.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username),
        )
        await self._db.commit()

    async def get_generation_count(self, user_id: int) -> int:
        async with self._db.execute(
            "SELECT COUNT(*) FROM generations WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

    async def increment_generations(self, user_id: int) -> None:
        await self._db.execute(
            "INSERT INTO generations (user_id) VALUES (?)", (user_id,)
        )
        await self._db.commit()

    async def has_free_generations_left(self, user_id: int) -> bool:
        count = await self.get_generation_count(user_id)
        return count < self._free_limit
