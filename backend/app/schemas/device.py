from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.device import DeviceStatus, SimulationProfile


class DeviceBase(BaseModel):
    name: str = Field(min_length=2, max_length=128)
    ip_address: str = Field(min_length=3, max_length=64)
    device_type: str = Field(min_length=2, max_length=64)
    location: str = Field(min_length=2, max_length=128)
    monitoring_enabled: bool = True
    simulation_profile: SimulationProfile = SimulationProfile.normal


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    name: str | None = None
    ip_address: str | None = None
    device_type: str | None = None
    location: str | None = None
    monitoring_enabled: bool | None = None
    simulation_profile: SimulationProfile | None = None


class DeviceRead(DeviceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    current_status: DeviceStatus
    consecutive_breach_count: int
    created_at: datetime
    updated_at: datetime
