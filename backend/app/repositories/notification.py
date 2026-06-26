from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def list_recent(self, limit: int = 50) -> list[Notification]:
        return list(
            self.db.scalars(
                select(Notification).order_by(desc(Notification.created_at)).limit(limit)
            ).all()
        )
