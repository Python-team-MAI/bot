from __future__ import annotations
from typing import TYPE_CHECKING
from bot.core.config import settings

from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

if TYPE_CHECKING:
    from aiogram import Bot

users_commands: dict[str, dict[str, str]] = {
    "en": {
        "start": "help info",
        "contacts": "developer contact details",
        "menu": "main menu with earning schemes",
        "support": "support contacts",
    },
    "uk": {
        "start": "help info",
        "contacts": "developer contact details",
        "menu": "main menu with earning schemes",
        "support": "support contacts",
    },
    "ru": {
        "start": "Помощь",
        "contacts": "контакты разработчика",
        "menu": "главное меню",
        "support": "поддержка",
    },
}

admins_commands: dict[str, dict[str, str]] = {
    "en": {
        "start": "help info",
        "menu": "main menu with earning schemes",
        "support": "support contacts",
    },
    "uk": {
        "start": "help info",
        "menu": "main menu with earning schemes",
        "support": "support contacts",
    },
    "ru": {
        "start": "help info",
        "menu": "main menu with earning schemes",
        "support": "support contacts",
    },
}


async def fset_default_commands(bot: Bot) -> None:
    await remove_default_commands(bot)

    for language_code, commands in users_commands.items():
        await bot.set_my_commands(
            [BotCommand(command=command, description=description) for command, description in commands.items()],
            scope=BotCommandScopeDefault(),
            language_code=language_code,
        )


        for admin in settings.ADMIN_IDS.split(","):
            await bot.set_my_commands(
                [
                    BotCommand(command=command, description=description)
                        for command, description in admins_commands[language_code].items()
                    ],
                    scope=BotCommandScopeChat(chat_id=int(admin)),
                )


async def remove_default_commands(bot: Bot) -> None:
    await bot.delete_my_commands(scope=BotCommandScopeDefault())
