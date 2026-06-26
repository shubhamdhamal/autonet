from fastapi import APIRouter

from app.api.routes import dashboard, devices, incidents, monitoring, notifications, statistics

api_router = APIRouter()
api_router.include_router(devices.router, prefix="/devices", tags=["Devices"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incidents"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(statistics.router, prefix="/statistics", tags=["Statistics"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
