import logging
from pathlib import Path

from sqlalchemy import func, select

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import Device, Incident, MonitoringLog, Notification  # noqa: F401
from app.models.device import SimulationProfile

logger = logging.getLogger(__name__)

SEED_DEVICES = [
    {
        "name": "Core-Router-01",
        "ip_address": "8.8.8.8",
        "device_type": "Router",
        "location": "Data Center A",
        "simulation_profile": SimulationProfile.normal,
    },
    {
        "name": "Edge-Switch-02",
        "ip_address": "1.1.1.1",
        "device_type": "Switch",
        "location": "Branch Office",
        "simulation_profile": SimulationProfile.normal,
    },
    {
        "name": "Firewall-03",
        "ip_address": "208.67.222.222",
        "device_type": "Firewall",
        "location": "DMZ",
        "simulation_profile": SimulationProfile.normal,
    },
    {
        "name": "Sim-High-Loss",
        "ip_address": "10.0.0.10",
        "device_type": "Router",
        "location": "Lab",
        "simulation_profile": SimulationProfile.packet_loss_20,
    },
    {
        "name": "Sim-High-Latency",
        "ip_address": "10.0.0.11",
        "device_type": "Switch",
        "location": "Lab",
        "simulation_profile": SimulationProfile.high_latency,
    },
    {
        "name": "Sim-Random",
        "ip_address": "10.0.0.12",
        "device_type": "Access Point",
        "location": "Lab",
        "simulation_profile": SimulationProfile.random_issues,
    },
]


def init_db() -> None:
    db_path = Path("database")
    db_path.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        count = db.scalar(select(func.count()).select_from(Device)) or 0
        if count == 0:
            for item in SEED_DEVICES:
                db.add(Device(**item, monitoring_enabled=True))
            db.commit()
            logger.info("Seeded %d sample devices", len(SEED_DEVICES))
    finally:
        db.close()
