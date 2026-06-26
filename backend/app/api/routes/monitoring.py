from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.repositories.device import DeviceRepository
from app.repositories.incident import IncidentRepository
from app.repositories.monitoring import MonitoringRepository
from app.scheduler.jobs import run_monitoring_job, scheduler
from app.schemas.monitoring import MonitoringLogRead
from app.schemas.monitoring_status import MonitoringStatus

router = APIRouter()


@router.get("/logs", response_model=list[MonitoringLogRead])
def list_monitoring_logs(
    limit: int = Query(100, ge=1, le=1000),
    device_id: int | None = None,
    db: Session = Depends(get_db),
) -> list:
    return MonitoringRepository(db).list_recent(limit=limit, device_id=device_id)


@router.get("/status", response_model=MonitoringStatus)
def monitoring_status(db: Session = Depends(get_db)) -> MonitoringStatus:
    device_repo = DeviceRepository(db)
    monitoring_repo = MonitoringRepository(db)
    incident_repo = IncidentRepository(db)
    recent = monitoring_repo.list_recent(limit=1)
    open_count = incident_repo.count_open()

    note = (
        "New incidents are created only when no OPEN incident exists for that device. "
        "Close or resolve existing open incidents on sim devices to allow new alerts."
        if open_count > 0
        else "Monitoring active. Sim devices need ~90 seconds (3 cycles) to raise incidents."
    )

    return MonitoringStatus(
        scheduler_running=scheduler.running,
        monitor_interval_seconds=settings.monitor_interval_seconds,
        monitored_devices=len(device_repo.list_monitored()),
        total_monitoring_logs=monitoring_repo.count_all(),
        open_incidents=open_count,
        last_log_at=recent[0].created_at if recent else None,
        note=note,
    )


@router.post("/run-now")
def run_monitoring_now() -> dict[str, str]:
    run_monitoring_job()
    return {"status": "ok", "message": "Monitoring cycle completed"}
