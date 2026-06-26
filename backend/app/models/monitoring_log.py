from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MonitoringLog(Base):
    __tablename__ = "monitoring_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), nullable=False, index=True)
    packet_loss: Mapped[float] = mapped_column(Float, nullable=False)
    avg_latency: Mapped[float] = mapped_column(Float, nullable=False)
    min_latency: Mapped[float] = mapped_column(Float, nullable=False)
    max_latency: Mapped[float] = mapped_column(Float, nullable=False)
    jitter: Mapped[float] = mapped_column(Float, nullable=False)
    response_time: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    device = relationship("Device", back_populates="monitoring_logs")
