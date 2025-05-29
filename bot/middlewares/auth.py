from __future__ import annotations
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import logging

from bot.service.users import users_repo, User, UserView, UserFilter
from bot.utils.command import find_command_argument
from bot.core.config import settings

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from aiogram.types import TelegramObject
    from sqlalchemy.ext.asyncio import AsyncSession



logger = logging.getLogger(__name__)

from aiogram.types import Update, Message

class AuthMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: TelegramObject, data: dict[str, Any]):
        # Проверяем, что event — это Update с message
        if isinstance(event, Update) and event.message:
            message: Message = event.message
            session: AsyncSession = data.get("session")
            
            if not session:
                return await handler(event, data)

            from_user = message.from_user
            if not from_user:
                return await handler(event, data)

            logger.debug(f"Telegram id: {from_user.id}")
            user = await users_repo.find_one_or_none(
                session=session,
                filters=UserFilter(tg_id=str(from_user.id))
            )
            if user:
                return await handler(event, data)

            logger.info(f"Registering new user | user_id: {from_user.id} | message: {message.text}")

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔐 Войти", url=f"{settings.MAIN_SERVER_DOMAIN}/ru/auth/tg-auth?tg_id={message.from_user.id}")]
            ])
            await message.answer("Чтобы авторизоваться, нажми кнопку ниже:", reply_markup=keyboard)

        


