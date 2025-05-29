from aiogram import Router, types, F
from aiogram.filters import Command
from bot.cache.redis import redis_client, set_redis_value
from bot.core.loader import bot
from aiogram_dialog import DialogManager
from bot.dialogs.main_menu.states import MainMenu
from aiogram.fsm.context import FSMContext
from bot.handlers.on_click.main_menu import on_support
import logging
from bot.core.config import settings
from aiogram.filters import StateFilter 
from bot.keyboards.inline_menu import support_kb, main_menu_kb
logger = logging.getLogger(__name__)

router = Router(name="support")


@router.message(Command("support"))
async def cmd_support(message: types.Message, state: FSMContext):
    await state.set_state(MainMenu.start_support)
    await on_support(message.from_user.id, message)


@router.message(Command("close"))
async def close_chat(message: types.Message, state: FSMContext):
    operator_id = message.from_user.id
    op_key = f"support:operator:{operator_id}"
    if not await redis_client.exists(op_key):
        await message.reply("У вас нет активного чата.")
        return
    user_id = int(await redis_client.get(op_key))
    await redis_client.delete(op_key)
    await redis_client.delete(f"support:user:{user_id}")
    await bot.send_message(user_id, "Чат поддержки закрыт оператором.")
    await message.reply("Вы закрыли чат.")
    await message.answer(
        "Главное меню",
        reply_markup=main_menu_kb()
    )
    await state.set_state(MainMenu.main_menu)

  
