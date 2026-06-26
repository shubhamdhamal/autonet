from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.incident import IncidentStatus


class IncidentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_number: str
    device_id: int
    severity: str
    status: IncidentStatus
    packet_loss: float
    latency: float
    jitter: float
    root_cause: str
    resolution_notes: str | None
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None


class IncidentDetail(IncidentRead):
    device_name: str | None = None
    device_ip: str | None = None
    device_location: str | None = None


class IncidentResolve(BaseModel):
    resolution_notes: str = Field(min_length=3)


class IncidentClose(BaseModel):
    resolution_notes: str | None = None
