from aiogram import Router, types, F
from aiogram.filters import Command
from bot.dialogs.main_menu.states import MainMenu
from aiogram_dialog import DialogManager, StartMode
from bot.handlers.on_click.main_menu import process_question, on_support
from aiogram.fsm.context import FSMContext
from bot.keyboards.inline_menu import main_menu_kb, support_kb
from sqlalchemy.ext.asyncio import AsyncSession
from bot.core.loader import bot
import logging
logger = logging.getLogger(__name__)

router = Router(name="menu")



@router.message()
async def handle_question_message(message: types.Message, state: FSMContext, session: AsyncSession):
    """Обработчик обычных текстовых сообщений в состоянии start_question"""
    await state.set_state(MainMenu.waiting_answer)
    await process_question(message, state, message.text, session)



