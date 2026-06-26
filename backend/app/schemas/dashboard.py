from datetime import datetime

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_devices: int
    healthy: int
    warning: int
    major: int
    critical: int
    open_incidents: int
    network_health_score: float


class TrendPoint(BaseModel):
    timestamp: datetime
    packet_loss: float
    latency: float
    jitter: float


class DeviceStatusRow(BaseModel):
    id: int
    name: str
    ip_address: str
    location: str
    status: str
    packet_loss: float
    avg_latency: float
    jitter: float
    last_check: datetime | None


class ProblemDevice(BaseModel):
    id: int
    name: str
    ip_address: str
    status: str
    open_incidents: int
    packet_loss: float
    avg_latency: float
    jitter: float


class DashboardResponse(BaseModel):
    summary: DashboardSummary
    trends: list[TrendPoint]
    recent_incidents: list[dict]
    device_status: list[DeviceStatusRow]
    top_problem_devices: list[ProblemDevice]
