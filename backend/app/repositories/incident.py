from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.models.incident import Incident, IncidentStatus


class IncidentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, incident: Incident) -> Incident:
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def update(self, incident: Incident) -> Incident:
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def get(self, incident_id: int) -> Incident | None:
        return self.db.get(Incident, incident_id)

    def get_open_for_device(self, device_id: int) -> Incident | None:
        return self.db.scalar(
            select(Incident).where(
                Incident.device_id == device_id,
                Incident.status == IncidentStatus.open,
            )
        )

    def list_all(self, status: IncidentStatus | None = None) -> list[Incident]:
        stmt = select(Incident).order_by(desc(Incident.created_at))
        if status:
            stmt = stmt.where(Incident.status == status)
        return list(self.db.scalars(stmt).all())

    def list_recent(self, limit: int = 10) -> list[Incident]:
        return list(
            self.db.scalars(select(Incident).order_by(desc(Incident.created_at)).limit(limit)).all()
        )

    def count_open(self) -> int:
        return (
            self.db.scalar(
                select(func.count()).select_from(Incident).where(Incident.status == IncidentStatus.open)
            )
            or 0
        )

    def count_all(self) -> int:
        return self.db.scalar(select(func.count()).select_from(Incident)) or 0

    def count_auto_closed(self) -> int:
        return (
            self.db.scalar(
                select(func.count())
                .select_from(Incident)
                .where(Incident.status == IncidentStatus.auto_closed)
            )
            or 0
        )

    def next_incident_number(self) -> str:
        count = self.count_all() + 1
        return f"INC-{count:06d}"
