from datetime import datetime
from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.incident import IncidentStatus
from app.repositories.device import DeviceRepository
from app.repositories.incident import IncidentRepository
from app.repositories.monitoring import MonitoringRepository
from app.schemas.dashboard import (
    DashboardResponse,
    DashboardSummary,
    DeviceStatusRow,
    ProblemDevice,
    TrendPoint,
)
from app.services.health_score import calculate_network_health_score


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.device_repo = DeviceRepository(db)
        self.monitoring_repo = MonitoringRepository(db)
        self.incident_repo = IncidentRepository(db)

    def get_dashboard(self) -> DashboardResponse:
        devices = self.device_repo.list_all()
        status_counts = self.device_repo.count_by_status()
        health_score = calculate_network_health_score(
            self.device_repo, self.monitoring_repo, self.incident_repo
        )

        summary = DashboardSummary(
            total_devices=len(devices),
            healthy=status_counts["Healthy"],
            warning=status_counts["Warning"],
            major=status_counts["Major"],
            critical=status_counts["Critical"],
            open_incidents=self.incident_repo.count_open(),
            network_health_score=health_score,
        )

        trend_logs = self.monitoring_repo.get_trends(hours=2)
        bucket: dict[datetime, list] = defaultdict(list)
        for log in trend_logs:
            bucket_key = log.created_at.replace(second=0, microsecond=0)
            bucket[bucket_key].append(log)

        trends: list[TrendPoint] = []
        for ts in sorted(bucket.keys()):
            logs = bucket[ts]
            trends.append(
                TrendPoint(
                    timestamp=ts,
                    packet_loss=round(sum(l.packet_loss for l in logs) / len(logs), 2),
                    latency=round(sum(l.avg_latency for l in logs) / len(logs), 2),
                    jitter=round(sum(l.jitter for l in logs) / len(logs), 2),
                )
            )

        device_status: list[DeviceStatusRow] = []
        for device in devices:
            latest = self.monitoring_repo.get_latest_for_device(device.id)
            device_status.append(
                DeviceStatusRow(
                    id=device.id,
                    name=device.name,
                    ip_address=device.ip_address,
                    location=device.location,
                    status=device.current_status.value,
                    packet_loss=latest.packet_loss if latest else 0.0,
                    avg_latency=latest.avg_latency if latest else 0.0,
                    jitter=latest.jitter if latest else 0.0,
                    last_check=latest.created_at if latest else None,
                )
            )

        recent_incidents = []
        for incident in self.incident_repo.list_recent(8):
            device = self.device_repo.get(incident.device_id)
            recent_incidents.append(
                {
                    "id": incident.id,
                    "incident_number": incident.incident_number,
                    "device_name": device.name if device else "Unknown",
                    "severity": incident.severity,
                    "status": incident.status.value,
                    "packet_loss": incident.packet_loss,
                    "latency": incident.latency,
                    "created_at": incident.created_at.isoformat(),
                }
            )

        problem_devices: list[ProblemDevice] = []
        for device in devices:
            open_count = 1 if self.incident_repo.get_open_for_device(device.id) else 0
            latest = self.monitoring_repo.get_latest_for_device(device.id)
            if device.current_status.value in ("Warning", "Major", "Critical") or open_count:
                problem_devices.append(
                    ProblemDevice(
                        id=device.id,
                        name=device.name,
                        ip_address=device.ip_address,
                        status=device.current_status.value,
                        open_incidents=open_count,
                        packet_loss=latest.packet_loss if latest else 0.0,
                        avg_latency=latest.avg_latency if latest else 0.0,
                        jitter=latest.jitter if latest else 0.0,
                    )
                )

        problem_devices.sort(
            key=lambda d: (
                {"Critical": 0, "Major": 1, "Warning": 2, "Healthy": 3}.get(d.status, 4),
                -d.packet_loss,
            )
        )

        return DashboardResponse(
            summary=summary,
            trends=trends,
            recent_incidents=recent_incidents,
            device_status=device_status,
            top_problem_devices=problem_devices[:5],
        )


class StatisticsService:
    def __init__(self, db: Session) -> None:
        self.device_repo = DeviceRepository(db)
        self.monitoring_repo = MonitoringRepository(db)
        self.incident_repo = IncidentRepository(db)

    def get_statistics(self) -> dict:
        avg_loss, avg_latency, avg_jitter = self.monitoring_repo.averages()
        health_score = calculate_network_health_score(
            self.device_repo, self.monitoring_repo, self.incident_repo
        )
        return {
            "total_monitoring_cycles": self.monitoring_repo.count_all(),
            "total_incidents": self.incident_repo.count_all(),
            "open_incidents": self.incident_repo.count_open(),
            "auto_closed_incidents": self.incident_repo.count_auto_closed(),
            "avg_packet_loss": round(avg_loss, 2),
            "avg_latency": round(avg_latency, 2),
            "avg_jitter": round(avg_jitter, 2),
            "network_health_score": health_score,
            "devices_by_status": self.device_repo.count_by_status(),
        }
