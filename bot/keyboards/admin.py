from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.dialogs.main_menu.states import MainMenu


def main_menu_kb() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Добавить админа", callback_data="add_admin")
    kb.button(text="Удалить админа", callback_data="remove_admin")
    kb.button(text="Кластеризация всех вопросов", callback_data="cluster_all_questions")
    return kb.adjust(2, 1, 1, 1).as_markup()