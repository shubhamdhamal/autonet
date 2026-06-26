import logging
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.device import Device, DeviceStatus
from app.models.incident import Incident, IncidentStatus
from app.models.monitoring_log import MonitoringLog
from app.repositories.device import DeviceRepository
from app.repositories.incident import IncidentRepository
from app.repositories.monitoring import MonitoringRepository
from app.services.notifications.dispatcher import NotificationDispatcher
from app.services.simulation import ProbeResult, probe_device

from app.core.constants import BREACH_LATENCY, BREACH_PACKET_LOSS, CONSECUTIVE_CYCLES


def _is_breach(result: ProbeResult) -> bool:
    return result.packet_loss > BREACH_PACKET_LOSS or result.avg_latency > BREACH_LATENCY


def _determine_severity(result: ProbeResult) -> str:
    if result.packet_loss >= 50 or result.avg_latency >= 500:
        return DeviceStatus.critical.value
    if result.packet_loss > BREACH_PACKET_LOSS or result.avg_latency > BREACH_LATENCY:
        return DeviceStatus.major.value
    if result.packet_loss > 5 or result.avg_latency > 100 or result.jitter > 30:
        return DeviceStatus.warning.value
    return DeviceStatus.healthy.value


def _root_cause(result: ProbeResult) -> str:
    causes: list[str] = []
    if result.packet_loss > BREACH_PACKET_LOSS:
        causes.append(f"Packet loss at {result.packet_loss}%")
    if result.avg_latency > BREACH_LATENCY:
        causes.append(f"Latency at {result.avg_latency}ms")
    if result.jitter > 30:
        causes.append(f"High jitter at {result.jitter}ms")
    if not causes:
        return "Network metrics within acceptable thresholds"
    return "; ".join(causes)


class IncidentEngine:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.device_repo = DeviceRepository(db)
        self.monitoring_repo = MonitoringRepository(db)
        self.incident_repo = IncidentRepository(db)
        self.notification_dispatcher = NotificationDispatcher(db)

    def process_device_result(self, device: Device, result: ProbeResult) -> None:
        log = MonitoringLog(
            device_id=device.id,
            packet_loss=result.packet_loss,
            avg_latency=result.avg_latency,
            min_latency=result.min_latency,
            max_latency=result.max_latency,
            jitter=result.jitter,
            response_time=result.response_time,
            status=result.status.value,
        )
        self.monitoring_repo.create(log)

        device.current_status = result.status
        if _is_breach(result):
            device.consecutive_breach_count += 1
        else:
            device.consecutive_breach_count = 0

        open_incident = self.incident_repo.get_open_for_device(device.id)

        if (
            device.consecutive_breach_count >= CONSECUTIVE_CYCLES
            and open_incident is None
        ):
            incident = Incident(
                incident_number=self.incident_repo.next_incident_number(),
                device_id=device.id,
                severity=_determine_severity(result),
                status=IncidentStatus.open,
                packet_loss=result.packet_loss,
                latency=result.avg_latency,
                jitter=result.jitter,
                root_cause=_root_cause(result),
            )
            created = self.incident_repo.create(incident)
            try:
                self.notification_dispatcher.notify_incident_created(created, device, result)
            except Exception:
                logger.exception(
                    "Notification failed for incident %s; incident was still created",
                    created.incident_number,
                )

        elif open_incident and not _is_breach(result):
            open_incident.status = IncidentStatus.auto_closed
            open_incident.closed_at = datetime.utcnow()
            open_incident.resolution_notes = "Auto-closed: device metrics returned to normal."
            self.incident_repo.update(open_incident)
            device.consecutive_breach_count = 0
            logger.info(
                "Auto-closed incident %s for device %s",
                open_incident.incident_number,
                device.name,
            )

        self.device_repo.update(device)


class MonitoringService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.device_repo = DeviceRepository(db)
        self.incident_engine = IncidentEngine(db)

    def run_cycle(self) -> None:
        devices = self.device_repo.list_monitored()
        logger.info("Starting monitoring cycle for %d devices", len(devices))
        for device in devices:
            try:
                result = probe_device(device.ip_address, device.simulation_profile)
                self.incident_engine.process_device_result(device, result)
            except Exception:
                logger.exception("Monitoring failed for device %s", device.name)
        logger.info("Monitoring cycle completed")
