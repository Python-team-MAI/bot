from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, ReactionTypeEmoji
from aiogram_dialog import DialogManager
from aiogram_dialog.api.exceptions import NoContextError
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from bot.dialogs.main_menu.states import MainMenu
from bot.core.config import settings
from bot.service.messages import messages_repo, Message
from bot.service.users import users_repo, UserFilter
import logging
from bot.cache.redis import redis_client, set_redis_value
from bot.core.loader import bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from bot.keyboards.inline_menu import main_menu_kb
from sqlalchemy.ext.asyncio import AsyncSession
import aiohttp
from aiohttp.web import Request
logger = logging.getLogger(__name__)


async def process_question(message: Message, state: FSMContext, session: AsyncSession):
    """Общая функция обработки вопроса независимо от источника текста"""
    try:
        user = await users_repo.find_one_or_none(session=session, filters=UserFilter(tg_id=str(message.from_user.id)))
        question = await messages_repo.add(
            session=session,
            values=Message(user_id=user.id, text=message.text, type="user")
        )
        access_token = await users_repo.get_access_token(tg_id=str(message.from_user.id), session=session)
        headers = {
            "Authorization": f"Bearer {access_token}",
            # Content-Type установится автоматически как multipart/form-data
        }
        wait_message = await message.answer("Генерируем ответ....")
        async with aiohttp.ClientSession() as client_session:
            async with client_session.post(settings.ML_SERVER_URL, headers=headers, json={
                "message": message.text
                        }) as response:
                answer = await response.text()
        if answer == "invalid token error. Not enough segments":
            access_token, refresh_token = await users_repo.refresh_token(user.refresh_token)

            await users_repo.update(session=session, filters=UserFilter(id=user.id), values=UserFilter(access_token=access_token, refresh_token=refresh_token))
            headers = {
                "Authorization": f"Bearer {access_token}",
                # Content-Type установится автоматически как multipart/form-data
            }
            wait_message = await message.answer("Генерируем ответ....")
            async with aiohttp.ClientSession() as client_session:
                async with client_session.post(settings.ML_SERVER_URL, headers=headers, json={
                    "message": message.text
                            }) as response:
                    answer = await response.text()

        await wait_message.delete()
        logger.debug(f"Ans: {answer}")
        if answer:
            await message.reply(
                answer["ans"],
                allowed_reactions=[
                    ReactionTypeEmoji(emoji="👍"),
                    ReactionTypeEmoji(emoji="👎")
                ]
            )
            await messages_repo.add(
                session=session,
                values=Message(user_id=message.from_user.id, text=answer, type="assistant")
            )
        else:
            await message.answer("Произошла ошибка при получении ответа. Попробуйте позже.")
            

        
    except Exception as e:
        logger.error(f"Ошибка при обработке вопроса: {e}")
        await message.answer("Произошла ошибка при обработке вашего вопроса. Пожалуйста, попробуйте еще раз.")



async def on_reaction_added(message: Message, reaction: str):
    """Обработка добавления реакции"""
    is_helpful = reaction == "👍"
    # await users_service.update_reaction_stats(
    #     user_id=message.from_user.id,
    #     is_helpful=is_helpful
    # )

async def on_reaction_removed(message: Message, reaction: str):
    """Обработка удаления реакции"""
    is_helpful = reaction == "👍"
    # await users_service.update_reaction_stats(
    #     user_id=message.from_user.id,
    #     is_helpful=not is_helpful, 
    #     remove=True  
    # )


async def on_support(user_id: int, message: Message):
    user_key = f"support:user:{user_id}"
    admin_ids = settings.ADMIN_IDS.split(",")
    logger.info(f"admin_ids: {admin_ids}")
    logger.info(f"user_id: {user_id}")
    if await redis_client.exists(user_key):
        await message.answer("У вас уже открыт чат поддержки. Ожидайте оператора.")
        return
    if str(user_id) in admin_ids:
        await message.answer("Вы являетесь администратором.")
        return
    await set_redis_value(user_key, "waiting")
    await message.answer("Запрос в службу поддержки отправлен. Ожидайте оператора.")

    kb = InlineKeyboardBuilder()
    kb.button(text="Взять чат", callback_data=f"take_{user_id}")
    markup = kb.as_markup()
    for admin_id in settings.ADMIN_IDS.split(","):
        await bot.send_message(
            int(admin_id),
            f"Пользователь <a href=\"tg://user?id={user_id}\">{message.from_user.full_name}</a> запрашивает поддержку.",
            reply_markup=markup,
            parse_mode="HTML"
        )

