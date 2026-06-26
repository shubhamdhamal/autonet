import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from app.core.config import settings

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self) -> None:
        self.enabled = settings.telegram_enabled
        self.bot_token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id
        self.parse_mode = settings.telegram_parse_mode

    def is_configured(self) -> bool:
        return bool(self.enabled and self.bot_token and self.chat_id)

    def send_message(self, text: str) -> bool:
        if not self.is_configured():
            logger.debug("Telegram notifications disabled or not configured")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": self.parse_mode,
            "disable_web_page_preview": True,
        }
        data = urllib.parse.urlencode(payload).encode("utf-8")
        request = urllib.request.Request(url, data=data, method="POST")

        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                body = json.loads(response.read().decode("utf-8"))
                if body.get("ok"):
                    logger.info("Telegram notification sent to chat %s", self.chat_id)
                    return True
                logger.error("Telegram API error: %s", body)
                return False
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            logger.error("Telegram HTTP error %s: %s", exc.code, error_body)
            return False
        except Exception:
            logger.exception("Failed to send Telegram notification")
            return False
