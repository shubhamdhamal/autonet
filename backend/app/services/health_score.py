from app.models.device import DeviceStatus
from app.repositories.device import DeviceRepository
from app.repositories.incident import IncidentRepository
from app.repositories.monitoring import MonitoringRepository


def calculate_network_health_score(
    device_repo: DeviceRepository,
    monitoring_repo: MonitoringRepository,
    incident_repo: IncidentRepository,
) -> float:
    devices = device_repo.list_all()
    if not devices:
        return 100.0

    avg_loss, avg_latency, avg_jitter = monitoring_repo.averages()
    open_incidents = incident_repo.count_open()

    loss_penalty = min(avg_loss * 2.5, 40)
    latency_penalty = min(max(avg_latency - 50, 0) / 10, 25)
    jitter_penalty = min(avg_jitter / 2, 15)
    incident_penalty = min(open_incidents * 5, 20)

    critical_count = sum(1 for d in devices if d.current_status == DeviceStatus.critical)
    critical_penalty = min(critical_count * 8, 20)

    score = 100 - loss_penalty - latency_penalty - jitter_penalty - incident_penalty - critical_penalty
    return round(max(0.0, min(100.0, score)), 1)
