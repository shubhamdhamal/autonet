import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SimulationProfile(str, enum.Enum):
    normal = "normal"
    packet_loss_20 = "packet_loss_20"
    high_latency = "high_latency"
    high_jitter = "high_jitter"
    device_down = "device_down"
    random_issues = "random_issues"


class DeviceStatus(str, enum.Enum):
    healthy = "Healthy"
    warning = "Warning"
    major = "Major"
    critical = "Critical"


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    ip_address: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    device_type: Mapped[str] = mapped_column(String(64), nullable=False)
    location: Mapped[str] = mapped_column(String(128), nullable=False)
    monitoring_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    simulation_profile: Mapped[SimulationProfile] = mapped_column(
        Enum(SimulationProfile), default=SimulationProfile.normal
    )
    current_status: Mapped[DeviceStatus] = mapped_column(
        Enum(DeviceStatus), default=DeviceStatus.healthy
    )
    consecutive_breach_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    monitoring_logs = relationship("MonitoringLog", back_populates="device", cascade="all,delete")
    incidents = relationship("Incident", back_populates="device", cascade="all,delete")
