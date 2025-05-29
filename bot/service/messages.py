from bot.core.base.base_model import Base
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from bot.core.base.base_repository import BaseRepository
from bot.core.base.base_service import BaseService


class MessageOrm(Base):

    __tablename__ = "messages"
    text: Mapped[str] = mapped_column(nullable=False)
    user_id: Mapped[str] = mapped_column(nullable=False)
    rating: Mapped[int] = mapped_column(default=0)  # -1 or 0 or 1
    type: Mapped[str] = mapped_column(nullable=False) 
    

class Message(BaseModel):
    text: str
    user_id: str
    rating: int = 0 
    type: str

class MessageView(Message):
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    updated_at: datetime
    id: int 


class MessageRepo(BaseRepository):
    model = MessageOrm

messages_repo: MessageRepo = MessageRepo()

