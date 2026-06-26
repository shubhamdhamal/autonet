from datetime import datetime

from pydantic import BaseModel


class MonitoringStatus(BaseModel):
    scheduler_running: bool
    monitor_interval_seconds: int
    monitored_devices: int
    total_monitoring_logs: int
    open_incidents: int
    last_log_at: datetime | None
    note: str
