from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.incident import IncidentStatus
from app.repositories.device import DeviceRepository
from app.repositories.incident import IncidentRepository
from app.schemas.incident import IncidentClose, IncidentDetail, IncidentResolve

router = APIRouter()


def _to_detail(incident, device=None) -> IncidentDetail:
    return IncidentDetail(
        id=incident.id,
        incident_number=incident.incident_number,
        device_id=incident.device_id,
        severity=incident.severity,
        status=incident.status,
        packet_loss=incident.packet_loss,
        latency=incident.latency,
        jitter=incident.jitter,
        root_cause=incident.root_cause,
        resolution_notes=incident.resolution_notes,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
        closed_at=incident.closed_at,
        device_name=device.name if device else None,
        device_ip=device.ip_address if device else None,
        device_location=device.location if device else None,
    )


@router.get("", response_model=list[IncidentDetail])
def list_incidents(
    status_filter: IncidentStatus | None = None,
    db: Session = Depends(get_db),
) -> list[IncidentDetail]:
    incident_repo = IncidentRepository(db)
    device_repo = DeviceRepository(db)
    incidents = incident_repo.list_all(status=status_filter)
    return [
        _to_detail(incident, device_repo.get(incident.device_id))
        for incident in incidents
    ]


@router.get("/{incident_id}", response_model=IncidentDetail)
def get_incident(incident_id: int, db: Session = Depends(get_db)) -> IncidentDetail:
    repo = IncidentRepository(db)
    incident = repo.get(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    device = DeviceRepository(db).get(incident.device_id)
    return _to_detail(incident, device)


@router.post("/{incident_id}/resolve", response_model=IncidentDetail)
def resolve_incident(
    incident_id: int,
    payload: IncidentResolve,
    db: Session = Depends(get_db),
) -> IncidentDetail:
    repo = IncidentRepository(db)
    incident = repo.get(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    if incident.status != IncidentStatus.open:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incident is not open")
    incident.status = IncidentStatus.resolved
    incident.resolution_notes = payload.resolution_notes
    incident.updated_at = datetime.utcnow()
    repo.update(incident)
    device = DeviceRepository(db).get(incident.device_id)
    return _to_detail(incident, device)


@router.post("/{incident_id}/close", response_model=IncidentDetail)
def close_incident(
    incident_id: int,
    payload: IncidentClose,
    db: Session = Depends(get_db),
) -> IncidentDetail:
    repo = IncidentRepository(db)
    incident = repo.get(incident_id)
    if not incident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    if incident.status == IncidentStatus.closed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incident already closed")
    incident.status = IncidentStatus.closed
    if payload.resolution_notes:
        incident.resolution_notes = payload.resolution_notes
    incident.closed_at = datetime.utcnow()
    incident.updated_at = datetime.utcnow()
    repo.update(incident)
    device = DeviceRepository(db).get(incident.device_id)
    return _to_detail(incident, device)
