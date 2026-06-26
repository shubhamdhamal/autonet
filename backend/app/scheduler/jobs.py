import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.incident_engine import MonitoringService

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def run_monitoring_job() -> bool:
    db = SessionLocal()
    try:
        MonitoringService(db).run_cycle()
        return True
    except Exception:
        logger.exception("Scheduled monitoring job failed")
        return False
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler:
    if not scheduler.running:
        scheduler.add_job(
            run_monitoring_job,
            "interval",
            seconds=settings.monitor_interval_seconds,
            id="network_monitoring",
            replace_existing=True,
        )
        scheduler.start()
        logger.info(
            "APScheduler started with %ss monitoring interval",
            settings.monitor_interval_seconds,
        )
    return scheduler


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped")
