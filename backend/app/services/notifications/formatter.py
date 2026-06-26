from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.models.device import Device
from app.models.incident import Incident
from app.core.constants import CONSECUTIVE_CYCLES
from app.services.simulation import ProbeResult

IST = ZoneInfo("Asia/Kolkata")


def _format_dt(dt: datetime) -> tuple[str, str]:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    utc_str = dt.astimezone(timezone.utc).strftime("%d %b %Y, %I:%M:%S %p UTC")
    ist_str = dt.astimezone(IST).strftime("%d %b %Y, %I:%M:%S %p IST")
    return utc_str, ist_str


def _severity_emoji(severity: str) -> str:
    return {
        "Critical": "🔴",
        "Major": "🟠",
        "Warning": "🟡",
        "Healthy": "🟢",
    }.get(severity, "⚪")


def format_incident_console(incident: Incident, device: Device, result: ProbeResult) -> str:
    utc_str, ist_str = _format_dt(incident.created_at)
    banner = "=" * 72
    return (
        f"\n{banner}\n"
        f"  NOC ALERT | NEW INCIDENT\n"
        f"{banner}\n"
        f"  Incident : {incident.incident_number}\n"
        f"  Device   : {device.name} ({device.ip_address})\n"
        f"  Type     : {device.device_type}\n"
        f"  Location : {device.location}\n"
        f"  Severity : {incident.severity}\n"
        f"  Status   : {incident.status.value}\n"
        f"  Loss     : {incident.packet_loss}%\n"
        f"  Latency  : {incident.latency}ms (min {result.min_latency} / max {result.max_latency})\n"
        f"  Jitter   : {incident.jitter}ms\n"
        f"  Response : {result.response_time}ms\n"
        f"  Cause    : {incident.root_cause}\n"
        f"  Breach   : {CONSECUTIVE_CYCLES} consecutive monitoring cycles\n"
        f"  Profile  : {device.simulation_profile.value}\n"
        f"  Time UTC : {utc_str}\n"
        f"  Time IST : {ist_str}\n"
        f"{banner}\n"
    )


def format_incident_telegram_html(incident: Incident, device: Device, result: ProbeResult) -> str:
    utc_str, ist_str = _format_dt(incident.created_at)
    emoji = _severity_emoji(incident.severity)

    return (
        f"{emoji} <b>NOC ALERT — NEW INCIDENT</b>\n\n"
        f"<b>Incident:</b> {incident.incident_number}\n"
        f"<b>Status:</b> {incident.status.value}\n"
        f"<b>Severity:</b> {incident.severity}\n\n"
        f"<b>Device</b>\n"
        f"• Name: {device.name}\n"
        f"• IP: <code>{device.ip_address}</code>\n"
        f"• Type: {device.device_type}\n"
        f"• Location: {device.location}\n"
        f"• Simulation: {device.simulation_profile.value}\n\n"
        f"<b>Network Metrics</b>\n"
        f"• Packet Loss: <b>{incident.packet_loss}%</b>\n"
        f"• Latency (avg): <b>{incident.latency} ms</b>\n"
        f"• Latency (min/max): {result.min_latency} / {result.max_latency} ms\n"
        f"• Jitter: <b>{incident.jitter} ms</b>\n"
        f"• Response Time: {result.response_time} ms\n"
        f"• Device Status: {result.status.value}\n\n"
        f"<b>Root Cause</b>\n"
        f"{incident.root_cause}\n\n"
        f"<b>Trigger</b>\n"
        f"Breach detected for <b>{CONSECUTIVE_CYCLES}</b> consecutive monitoring cycles "
        f"(~{CONSECUTIVE_CYCLES * 30}s)\n\n"
        f"<b>Detected At</b>\n"
        f"• {ist_str}\n"
        f"• {utc_str}"
    )


def format_incident_plain_summary(incident: Incident, device: Device) -> str:
    return (
        f"{incident.incident_number} | {device.name} ({device.ip_address}) | "
        f"{device.location} | {incident.severity} | Loss {incident.packet_loss}% | "
        f"Latency {incident.latency}ms | {incident.root_cause}"
    )
