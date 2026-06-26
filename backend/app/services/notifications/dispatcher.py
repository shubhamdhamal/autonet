import logging

from sqlalchemy.orm import Session

from app.models.device import Device
from app.models.incident import Incident
from app.models.notification import Notification
from app.repositories.notification import NotificationRepository
from app.services.notifications.formatter import (
    format_incident_console,
    format_incident_plain_summary,
    format_incident_telegram_html,
)
from app.services.notifications.telegram import TelegramNotifier
from app.services.simulation import ProbeResult

logger = logging.getLogger(__name__)


class NotificationDispatcher:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.notification_repo = NotificationRepository(db)
        self.telegram = TelegramNotifier()

    def notify_incident_created(
        self,
        incident: Incident,
        device: Device,
        result: ProbeResult,
    ) -> None:
        console_message = format_incident_console(incident, device, result)
        print(console_message)
        logger.info("Incident created: %s for device %s", incident.incident_number, device.name)

        summary = format_incident_plain_summary(incident, device)
        self.notification_repo.create(
            Notification(
                channel="console",
                title=f"New Incident {incident.incident_number}",
                message=summary,
            )
        )

        if self.telegram.is_configured():
            telegram_message = format_incident_telegram_html(incident, device, result)
            sent = self.telegram.send_message(telegram_message)
            self.notification_repo.create(
                Notification(
                    channel="telegram",
                    title=f"New Incident {incident.incident_number}",
                    message=summary if sent else f"FAILED: {summary}",
                )
            )
        else:
            logger.info("Telegram notifications not configured; skipping")

    def send_test_telegram(self) -> bool:
        if not self.telegram.is_configured():
            return False
        message = (
            "✅ <b>NOC Monitor — Telegram Test</b>\n\n"
            "Your Telegram notification integration is working.\n"
            "You will receive detailed alerts when new incidents are created."
        )
        return self.telegram.send_message(message)
