import logging
import random
import statistics
from dataclasses import dataclass

from ping3 import ping

from app.core.config import settings
from app.models.device import DeviceStatus, SimulationProfile

logger = logging.getLogger(__name__)


@dataclass
class ProbeResult:
    packet_loss: float
    avg_latency: float
    min_latency: float
    max_latency: float
    jitter: float
    response_time: float
    status: DeviceStatus


def _classify_status(packet_loss: float, avg_latency: float, jitter: float) -> DeviceStatus:
    if packet_loss >= 50 or avg_latency >= 500:
        return DeviceStatus.critical
    if packet_loss > 10 or avg_latency > 200:
        return DeviceStatus.major
    if packet_loss > 5 or avg_latency > 100 or jitter > 30:
        return DeviceStatus.warning
    return DeviceStatus.healthy


def _simulate_probe(profile: SimulationProfile) -> ProbeResult:
    if profile == SimulationProfile.packet_loss_20:
        packet_loss = random.uniform(18, 25)
        latencies = [random.uniform(40, 80) for _ in range(4)]
    elif profile == SimulationProfile.high_latency:
        packet_loss = random.uniform(0, 3)
        latencies = [random.uniform(220, 350) for _ in range(4)]
    elif profile == SimulationProfile.high_jitter:
        packet_loss = random.uniform(0, 5)
        latencies = [random.uniform(30, 200) for _ in range(4)]
    elif profile == SimulationProfile.device_down:
        packet_loss = 100.0
        latencies = []
    elif profile == SimulationProfile.random_issues:
        scenario = random.choice(
            ["normal", "loss", "latency", "jitter", "down"]
        )
        if scenario == "loss":
            packet_loss = random.uniform(12, 30)
            latencies = [random.uniform(40, 90) for _ in range(4)]
        elif scenario == "latency":
            packet_loss = random.uniform(0, 4)
            latencies = [random.uniform(210, 400) for _ in range(4)]
        elif scenario == "jitter":
            packet_loss = random.uniform(0, 6)
            latencies = [random.uniform(20, 250) for _ in range(4)]
        elif scenario == "down":
            packet_loss = 100.0
            latencies = []
        else:
            packet_loss = random.uniform(0, 2)
            latencies = [random.uniform(10, 40) for _ in range(4)]
    else:
        packet_loss = random.uniform(0, 2)
        latencies = [random.uniform(8, 35) for _ in range(4)]

    if not latencies:
        return ProbeResult(
            packet_loss=packet_loss,
            avg_latency=0.0,
            min_latency=0.0,
            max_latency=0.0,
            jitter=0.0,
            response_time=0.0,
            status=DeviceStatus.critical,
        )

    avg_latency = statistics.mean(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)
    jitter = statistics.pstdev(latencies) if len(latencies) > 1 else 0.0
    response_time = max_latency
    status = _classify_status(packet_loss, avg_latency, jitter)

    return ProbeResult(
        packet_loss=round(packet_loss, 2),
        avg_latency=round(avg_latency, 2),
        min_latency=round(min_latency, 2),
        max_latency=round(max_latency, 2),
        jitter=round(jitter, 2),
        response_time=round(response_time, 2),
        status=status,
    )


def _ping_probe(ip_address: str) -> ProbeResult:
    latencies: list[float] = []
    failures = 0
    probe_count = settings.monitor_probe_count
    timeout = settings.monitor_timeout_seconds

    for _ in range(probe_count):
        try:
            result = ping(ip_address, timeout=timeout, unit="ms")
            if result is None or result is False:
                failures += 1
            else:
                latencies.append(float(result))
        except Exception as exc:
            logger.warning("Ping failed for %s: %s", ip_address, exc)
            failures += 1

    packet_loss = (failures / probe_count) * 100 if probe_count else 100.0

    if not latencies:
        return ProbeResult(
            packet_loss=round(packet_loss, 2),
            avg_latency=0.0,
            min_latency=0.0,
            max_latency=0.0,
            jitter=0.0,
            response_time=0.0,
            status=DeviceStatus.critical,
        )

    avg_latency = statistics.mean(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)
    jitter = statistics.pstdev(latencies) if len(latencies) > 1 else 0.0
    response_time = max_latency
    status = _classify_status(packet_loss, avg_latency, jitter)

    return ProbeResult(
        packet_loss=round(packet_loss, 2),
        avg_latency=round(avg_latency, 2),
        min_latency=round(min_latency, 2),
        max_latency=round(max_latency, 2),
        jitter=round(jitter, 2),
        response_time=round(response_time, 2),
        status=status,
    )


def probe_device(ip_address: str, simulation_profile: SimulationProfile) -> ProbeResult:
    if simulation_profile != SimulationProfile.normal:
        return _simulate_probe(simulation_profile)
    return _ping_probe(ip_address)
