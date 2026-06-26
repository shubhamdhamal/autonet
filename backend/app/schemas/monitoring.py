from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MonitoringLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    device_id: int
    packet_loss: float
    avg_latency: float
    min_latency: float
    max_latency: float
    jitter: float
    response_time: float
    status: str
    created_at: datetime
