from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.device import Device


class DeviceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[Device]:
        return list(self.db.scalars(select(Device).order_by(Device.name)).all())

    def list_monitored(self) -> list[Device]:
        return list(
            self.db.scalars(
                select(Device).where(Device.monitoring_enabled.is_(True)).order_by(Device.name)
            ).all()
        )

    def get(self, device_id: int) -> Device | None:
        return self.db.get(Device, device_id)

    def get_by_name(self, name: str) -> Device | None:
        return self.db.scalar(select(Device).where(Device.name == name))

    def get_by_ip(self, ip_address: str) -> Device | None:
        return self.db.scalar(select(Device).where(Device.ip_address == ip_address))

    def create(self, device: Device) -> Device:
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        return device

    def update(self, device: Device) -> Device:
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        return device

    def delete(self, device: Device) -> None:
        self.db.delete(device)
        self.db.commit()

    def count_by_status(self) -> dict[str, int]:
        counts = {"Healthy": 0, "Warning": 0, "Major": 0, "Critical": 0}
        for device in self.list_all():
            counts[device.current_status.value] += 1
        return counts
