from __future__ import annotations
import asyncio
from bot.utils.setup_logging import setup_logging
from bot.service.users import users_repo
from bot.core.config import settings
from bot.core.session_manager import session_manager
from bot.core.loader import app, bot, dp
from bot.handlers import get_handlers_router
from bot.keyboards.default_commands import remove_default_commands
from bot.middlewares import register_middlewares
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp.web import AppRunner, TCPSite, Request, Response, Application, run_app
from sqlalchemy.ext.asyncio import AsyncSession


@session_manager.connection(commit=True)

async def handle_auth(request: Request, session: AsyncSession):
    data = await request.post()
    tg_id = data.get("telegram_id")
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    if not all([tg_id, access_token, refresh_token]):
        return Response(status=400, text="Missing fields")
    
    logger.debug(f"Successfully get data: {data}")
    # Сохраняем токены в БД/Redis
    await users_repo.save_tokens(tg_id, access_token, refresh_token, session=session)

    # Уведомляем пользователя
    await bot.send_message(tg_id, "✅ Успешный вход в систему!")
    hello_text = ""
    if first_name:
        hello_text = hello_text + first_name + " "

        if last_name:
            hello_text += last_name
        await bot.send_message(tg_id, f"Здравствуйте, {hello_text}")
    return Response(status=200, text="OK")

logger = setup_logging()


async def on_startup() -> None:
    logger.info("bot starting...")

    register_middlewares(dp)
    logger.info("register_middlewares")
    dp.include_router(get_handlers_router())
    logger.info("include_router")
    bot_info = await bot.get_me()

    logger.info(f"Name     - {bot_info.full_name}")
    logger.info(f"Username - @{bot_info.username}")
    logger.info(f"ID       - {bot_info.id}")

    states: dict[bool | None, str] = {
        True: "Enabled",
        False: "Disabled",
        None: "Unknown (This's not a bot)",
    }

    logger.info(f"Groups Mode  - {states[bot_info.can_join_groups]}")
    logger.info(f"Privacy Mode - {states[not bot_info.can_read_all_group_messages]}")
    logger.info(f"Inline Mode  - {states[bot_info.supports_inline_queries]}")

    logger.info("bot started")


async def on_shutdown() -> None:
    logger.info("bot stopping...")

    await remove_default_commands(bot)

    await dp.storage.close()
    await dp.fsm.storage.close()

    await bot.delete_webhook()
    await bot.session.close()

    logger.info("bot stopped")


async def setup_webhook() -> None:

    # await bot.set_webhook(
    #     settings.webhook_url,
    #     allowed_updates=dp.resolve_used_update_types(),
    #     secret_token=settings.WEBHOOK_SECRET
    # )

    # webhook_requests_handler = SimpleRequestHandler(
    #     dispatcher=dp,
    #     bot=bot,
    #     secret_token=settings.WEBHOOK_SECRET
    # )
    # webhook_requests_handler.register(app, path=settings.WEBHOOK_PATH)
    # setup_application(app, dp, bot=bot)

    # runner = AppRunner(app)
    # await runner.setup()
    # site = TCPSite(runner, host=settings.WEBHOOK_HOST, port=settings.WEBHOOK_PORT)
    # await site.start()
    # logger.debug("Setup webhook succesfully")
    # await asyncio.Event().wait()
    app = Application()

    # Настраиваем обработчик запросов для работы с вебхуком
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,  # Передаем диспетчер
        bot=bot  # Передаем объект бота
    )
    # Регистрируем обработчик запросов на определенном пути
    webhook_requests_handler.register(app, path=settings.WEBHOOK_PATH)

    # Настраиваем приложение и связываем его с диспетчером и ботом
    setup_application(app, dp, bot=bot)

    # Запускаем веб-сервер на указанном хосте и порте
    run_app(app, host=settings.WEBHOOK_HOST, port=settings.WEBHOOK_PORT)


async def main() -> None:

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    if settings.USE_WEBHOOK:
        await bot.delete_webhook()
        await setup_webhook()
    else:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def stop_polling():
    """Останавливает поллинг и закрывает все соединения"""
    logger.info("Остановка бота...")
    
    # Останавливаем поллинг
    await dp.stop_polling()
    
    # Закрываем соединения с Redis
    if hasattr(dp, 'storage') and dp.storage:
        await dp.storage.close()
        await dp.storage.wait_closed()
    
    # Закрываем сессию бота
    if hasattr(bot, 'session') and bot.session:
        await bot.session.close()
    
    logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())