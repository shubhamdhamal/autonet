from pydantic import BaseModel


class StatisticsResponse(BaseModel):
    total_monitoring_cycles: int
    total_incidents: int
    open_incidents: int
    auto_closed_incidents: int
    avg_packet_loss: float
    avg_latency: float
    avg_jitter: float
    network_health_score: float
    devices_by_status: dict[str, int]
