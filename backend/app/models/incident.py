import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class IncidentStatus(str, enum.Enum):
    open = "Open"
    resolved = "Resolved"
    closed = "Closed"
    auto_closed = "Auto Closed"


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    incident_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[IncidentStatus] = mapped_column(Enum(IncidentStatus), default=IncidentStatus.open)
    packet_loss: Mapped[float] = mapped_column(Float, nullable=False)
    latency: Mapped[float] = mapped_column(Float, nullable=False)
    jitter: Mapped[float] = mapped_column(Float, nullable=False)
    root_cause: Mapped[str] = mapped_column(String(255), nullable=False)
    resolution_notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime)

    device = relationship("Device", back_populates="incidents")
