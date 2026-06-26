from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.notification import NotificationRepository
from app.schemas.notification import NotificationRead

router = APIRouter()


@router.get("", response_model=list[NotificationRead])
def list_notifications(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list:
    return NotificationRepository(db).list_recent(limit=limit)
