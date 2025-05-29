from __future__ import annotations
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware

from bot.core.session_manager import session_manager

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import TelegramObject


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with session_manager.get_session() as session:
            data["session"] = session
            return await handler(event, data)
