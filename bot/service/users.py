from bot.core.base.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from bot.core.base.base_repository import BaseRepository
from bot.utils.setup_logging import setup_logging

logger = setup_logging(__name__)


class UserOrm(Base):
    tg_id: Mapped[str] = mapped_column(nullable=False)
    access_token: Mapped[str] = mapped_column(nullable=False)
    refresh_token: Mapped[str] = mapped_column(nullable=False)


class User(BaseModel):
    tg_id: str

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



class UsersRepo(BaseRepository):
    model = UserOrm

    async def save_tokens(self, tg_id, access_token, refresh_token, session):
        logger.debug("Save tokens")
        pass

users_repo: UsersRepo = UsersRepo()