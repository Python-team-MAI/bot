from aiogram import Router, types
from aiogram.filters import CommandStart
from bot.dialogs.main_menu.states import MainMenu
from aiogram_dialog import DialogManager, StartMode
from bot.keyboards.inline_menu import main_menu_kb, support_kb
from aiogram.fsm.context import FSMContext

router = Router(name="start")


@router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext) -> None:
    # Удаляем клавиатуру, если она есть
    if message.reply_markup:
        await message.edit_reply_markup(reply_markup=None)
    await message.answer(
        "👋 Добро пожаловать в чат-бот поддержки!\n\n"
            "Я помогу вам найти ответы на ваши вопросы. Вы можете:\n"
            "• Задать свой вопрос (просто напишите боту)\n"
            "• Обратиться в поддержку для связи с оператором\n\n"
            "После получения ответа вы можете оценить его качество, "
            "поставив реакцию 👍 или 👎",
        reply_markup=main_menu_kb()
    )
    