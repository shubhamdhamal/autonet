from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.monitoring import MonitoringRepository
from app.schemas.monitoring import MonitoringLogRead

router = APIRouter()


@router.get("/logs", response_model=list[MonitoringLogRead])
def list_monitoring_logs(
    limit: int = Query(100, ge=1, le=1000),
    device_id: int | None = None,
    db: Session = Depends(get_db),
) -> list:
    return MonitoringRepository(db).list_recent(limit=limit, device_id=device_id)
