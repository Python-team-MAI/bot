from aiogram import types
from aiogram.fsm.context import FSMContext
import time
from api.cache.redis import redis_client

RATE_LIMIT_SECONDS = 5

async def is_rate_limited(user_id: int) -> bool:
    key = f"question:rate_limit:{user_id}"
    now = int(time.time())
    last = await redis_client.get(key)

    if last is not None and (now - int(last)) < RATE_LIMIT_SECONDS:
        return True


    await redis_client.set(key, now, ex=RATE_LIMIT_SECONDS)
    return False

def rate_limit(limit_seconds: int = 5):
    def decorator(func):
        async def wrapper(message: types.Message, *args, **kwargs):
            if await is_rate_limited(message.from_user.id):
                await message.answer("⏳ Подождите немного перед повторной отправкой.")
                return
            return await func(message, *args, **kwargs)
        return wrapper
    return decorator