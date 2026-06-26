from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import apply_device_update, get_device_or_404, validate_unique_device
from app.db.session import get_db
from app.models.device import Device
from app.repositories.device import DeviceRepository
from app.schemas.device import DeviceCreate, DeviceRead, DeviceUpdate

router = APIRouter()


@router.get("", response_model=list[DeviceRead])
def list_devices(db: Session = Depends(get_db)) -> list[Device]:
    return DeviceRepository(db).list_all()


@router.post("", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
def create_device(payload: DeviceCreate, db: Session = Depends(get_db)) -> Device:
    validate_unique_device(db, payload)
    device = Device(**payload.model_dump())
    return DeviceRepository(db).create(device)


@router.get("/{device_id}", response_model=DeviceRead)
def get_device(device_id: int, db: Session = Depends(get_db)) -> Device:
    return get_device_or_404(db, device_id)


@router.put("/{device_id}", response_model=DeviceRead)
def update_device(device_id: int, payload: DeviceUpdate, db: Session = Depends(get_db)) -> Device:
    device = get_device_or_404(db, device_id)
    if payload.name or payload.ip_address:
        check_payload = DeviceCreate(
            name=payload.name or device.name,
            ip_address=payload.ip_address or device.ip_address,
            device_type=payload.device_type or device.device_type,
            location=payload.location or device.location,
            monitoring_enabled=payload.monitoring_enabled
            if payload.monitoring_enabled is not None
            else device.monitoring_enabled,
            simulation_profile=payload.simulation_profile or device.simulation_profile,
        )
        validate_unique_device(db, check_payload, exclude_id=device_id)
    return DeviceRepository(db).update(apply_device_update(device, payload))


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(device_id: int, db: Session = Depends(get_db)) -> None:
    device = get_device_or_404(db, device_id)
    DeviceRepository(db).delete(device)
