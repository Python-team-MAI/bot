from bot.core.base.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from bot.core.base.base_repository import BaseRepository
from bot.utils.setup_logging import setup_logging
from bot.cache.redis import set_redis_value, redis_client

logger = setup_logging(__name__)


class UserOrm(Base):
    tg_id: Mapped[str] = mapped_column(nullable=False)
    access_token: Mapped[str] = mapped_column(nullable=False)
    refresh_token: Mapped[str] = mapped_column(nullable=False)


class User(BaseModel):
    tg_id: str
    access_token: str 
    refresh_token: str

class UserView(User):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime

class UserFilter(BaseModel):
    id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    tg_id: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None


class UsersRepo(BaseRepository):
    model = UserOrm

    __tablename__ = "users"

    async def save_tokens(self, tg_id, access_token, refresh_token, session):
        if not await self.update(session=session, filters=UserFilter(tg_id=tg_id), values=UserFilter(access_token=access_token, refresh_token=refresh_token)):
            user = await self.find_one_or_none(session=session, filters=UserFilter(tg_id=tg_id))
            await self.add(session=session, values=User(tg_id=tg_id, access_token=access_token, refresh_token=refresh_token))
        await set_redis_value(key=f"tg_id:{tg_id}", value=access_token)
        
        logger.debug("Save tokens")

    async def get_access_token(self, tg_id, session):
        try:
            token = await redis_client.get(name=f"tg_id:{tg_id}")
            logger.debug(f"Token: {token}")
            if not token:
                user = await self.find_one_or_none(session=session, filters=UserFilter(tg_id=tg_id))
                token = user.access_token
                logger.debug(f"Token: {token}")
                await set_redis_value(key=f"tg_id:{tg_id}", value=token)
            return token
        except Exception as e:
            logger.error(f"Error: {e}")
            return None
        

users_repo: UsersRepo = UsersRepo()