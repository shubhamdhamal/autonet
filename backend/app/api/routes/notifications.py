from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.repositories.notification import NotificationRepository
from app.schemas.notification import NotificationRead, TelegramStatus
from app.services.notifications.dispatcher import NotificationDispatcher

router = APIRouter()


@router.get("", response_model=list[NotificationRead])
def list_notifications(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list:
    return NotificationRepository(db).list_recent(limit=limit)


@router.get("/telegram/status", response_model=TelegramStatus)
def telegram_status() -> TelegramStatus:
    configured = bool(
        settings.telegram_enabled and settings.telegram_bot_token and settings.telegram_chat_id
    )
    return TelegramStatus(
        enabled=settings.telegram_enabled,
        configured=configured,
        chat_id=settings.telegram_chat_id or None,
    )


@router.post("/telegram/test")
def test_telegram(db: Session = Depends(get_db)) -> dict[str, str]:
    dispatcher = NotificationDispatcher(db)
    if not dispatcher.telegram.is_configured():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram is not enabled or missing TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID",
        )
    if dispatcher.send_test_telegram():
        return {"status": "ok", "message": "Test Telegram message sent"}
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Failed to send Telegram message. Check bot token, chat ID, and server logs.",
    )
