from datetime import datetime, timedelta

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.monitoring_log import MonitoringLog


class MonitoringRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, log: MonitoringLog) -> MonitoringLog:
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list_recent(self, limit: int = 100, device_id: int | None = None) -> list[MonitoringLog]:
        stmt = select(MonitoringLog).order_by(desc(MonitoringLog.created_at)).limit(limit)
        if device_id:
            stmt = stmt.where(MonitoringLog.device_id == device_id)
        return list(self.db.scalars(stmt).all())

    def get_latest_for_device(self, device_id: int) -> MonitoringLog | None:
        return self.db.scalar(
            select(MonitoringLog)
            .where(MonitoringLog.device_id == device_id)
            .order_by(desc(MonitoringLog.created_at))
            .limit(1)
        )

    def get_trends(self, hours: int = 2) -> list[MonitoringLog]:
        since = datetime.utcnow() - timedelta(hours=hours)
        return list(
            self.db.scalars(
                select(MonitoringLog)
                .where(MonitoringLog.created_at >= since)
                .order_by(MonitoringLog.created_at)
            ).all()
        )

    def count_all(self) -> int:
        return self.db.scalar(select(func.count()).select_from(MonitoringLog)) or 0

    def averages(self) -> tuple[float, float, float]:
        row = self.db.execute(
            select(
                func.avg(MonitoringLog.packet_loss),
                func.avg(MonitoringLog.avg_latency),
                func.avg(MonitoringLog.jitter),
            )
        ).one()
        return float(row[0] or 0), float(row[1] or 0), float(row[2] or 0)
