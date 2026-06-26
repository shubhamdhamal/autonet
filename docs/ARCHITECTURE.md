# Architecture

## Overview

The NOC system follows a modular layered architecture with clear separation between API routes, services, repositories, and models.

```
┌─────────────┐     REST      ┌──────────────┐
│   React UI  │ ◄──────────► │   FastAPI    │
│  (Tailwind) │               │   Routers    │
└─────────────┘               └──────┬───────┘
                                     │
                              ┌──────▼───────┐
                              │   Services   │
                              │ Monitor/Inc  │
                              └──────┬───────┘
                                     │
                              ┌──────▼───────┐
                              │ Repositories │
                              └──────┬───────┘
                                     │
                              ┌──────▼───────┐
                              │  SQLAlchemy  │
                              │   SQLite DB  │
                              └──────────────┘
```

## Monitoring Flow

1. APScheduler triggers `MonitoringService.run_cycle()` every 30 seconds
2. For each enabled device, `probe_device()` runs real ping or simulation
3. Results stored in `monitoring_logs`
4. `IncidentEngine` evaluates breach thresholds and consecutive counts
5. Incidents created/closed; notifications logged and printed to console

## Incident State Machine

```
Open ──resolve──► Resolved ──close──► Closed
  │
  └── metrics normal ──► Auto Closed
```

## Extensibility

- **Email/Slack:** Add channel handlers in `NotificationRepository.create()` pipeline
- **PostgreSQL:** Change `DATABASE_URL` environment variable
- **Auth:** Add FastAPI dependency middleware on routers
