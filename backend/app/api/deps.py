from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.device import Device
from app.repositories.device import DeviceRepository
from app.schemas.device import DeviceCreate, DeviceUpdate


def get_device_or_404(db: Session, device_id: int) -> Device:
    device = DeviceRepository(db).get(device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device


def validate_unique_device(db: Session, payload: DeviceCreate, exclude_id: int | None = None) -> None:
    repo = DeviceRepository(db)
    existing_name = repo.get_by_name(payload.name)
    if existing_name and existing_name.id != exclude_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Device name already exists")
    existing_ip = repo.get_by_ip(payload.ip_address)
    if existing_ip and existing_ip.id != exclude_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="IP address already exists")


def apply_device_update(device: Device, payload: DeviceUpdate) -> Device:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(device, key, value)
    return device
