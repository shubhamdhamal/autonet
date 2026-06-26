from fastapi import APIRouter, Depends, HTTPException, Query, status
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
    if not run_monitoring_job():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Monitoring cycle failed. Check docker compose logs backend.",
        )
    return {"status": "ok", "message": "Monitoring cycle completed"}


@router.get("/debug")
def monitoring_debug(db: Session = Depends(get_db)) -> dict:
    device_repo = DeviceRepository(db)
    incident_repo = IncidentRepository(db)
    monitoring_repo = MonitoringRepository(db)

    devices = []
    for device in device_repo.list_monitored():
        open_incident = incident_repo.get_open_for_device(device.id)
        latest = monitoring_repo.get_latest_for_device(device.id)
        devices.append(
            {
                "id": device.id,
                "name": device.name,
                "ip": device.ip_address,
                "simulation_profile": device.simulation_profile.value,
                "monitoring_enabled": device.monitoring_enabled,
                "consecutive_breach_count": device.consecutive_breach_count,
                "current_status": device.current_status.value,
                "open_incident": open_incident.incident_number if open_incident else None,
                "cycles_until_incident": max(0, 3 - device.consecutive_breach_count),
                "latest_packet_loss": latest.packet_loss if latest else None,
                "latest_latency": latest.avg_latency if latest else None,
            }
        )

    return {
        "scheduler_running": scheduler.running,
        "open_incidents": incident_repo.count_open(),
        "total_logs": monitoring_repo.count_all(),
        "devices": devices,
    }
