from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    channel: str
    title: str
    message: str
    created_at: datetime


class TelegramStatus(BaseModel):
    enabled: bool
    configured: bool
    chat_id: str | None = None
