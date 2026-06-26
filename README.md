# NOC Network Quality Monitoring & Incident Management System

Enterprise-style Network Operations Center (NOC) solution for monitoring packet loss, latency, and jitter with automatic incident creation — no ServiceNow required.

## Features

- **Device Management** — CRUD for routers, switches, firewalls, and more
- **Network Monitoring** — APScheduler runs probes every 30 seconds
- **Incident Engine** — Auto-creates incidents after 3 consecutive breach cycles (packet loss > 10% OR latency > 200ms)
- **Dashboard** — Health score, trend charts, device status, problem devices
- **Incident Management** — View, resolve, close, and add resolution notes
- **Historical Logs** — Every monitoring cycle persisted
- **Notifications** — Console alerts + database table (extensible to Email/Slack)
- **Simulation Mode** — Test realistic network failures without physical devices

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Backend | Python, FastAPI, SQLAlchemy, Pydantic, APScheduler, ping3 |
| Frontend | React, Tailwind CSS, Chart.js, Axios, Vite |
| Database | SQLite (PostgreSQL-ready) |
| Deployment | Docker, Docker Compose, Nginx |

## Project Structure

```
networking/
├── backend/          # FastAPI application
├── frontend/         # React NOC dashboard
├── database/         # SQLite data directory
├── docker/           # Dockerfiles and nginx config
├── docs/             # Architecture documentation
├── docker-compose.yml
└── README.md
```

## Quick Start (Docker)

```bash
docker compose up --build
```

- **Dashboard:** http://localhost:3000
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
cd ..
uvicorn app.main:app --reload --app-dir backend
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Simulation Mode

Set a device's **Simulation Profile** when creating/editing:

| Profile | Behavior |
|---------|----------|
| `normal` | Real ICMP ping via ping3 |
| `packet_loss_20` | ~20% packet loss |
| `high_latency` | 220–350ms latency |
| `high_jitter` | High latency variance |
| `device_down` | 100% packet loss |
| `random_issues` | Random failure scenarios |

Pre-seeded lab devices (`Sim-High-Loss`, `Sim-High-Latency`, `Sim-Random`) will generate incidents within ~90 seconds.

## Incident Rules

Incidents are created when **either** condition holds for **3 consecutive** 30-second cycles:

- Packet Loss > 10%
- Latency > 200ms

- No duplicate open incidents per device
- Auto-closed when metrics return to normal
- Console notification printed on creation

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/devices` | List devices |
| POST | `/api/v1/devices` | Create device |
| PUT | `/api/v1/devices/{id}` | Update device |
| DELETE | `/api/v1/devices/{id}` | Delete device |
| GET | `/api/v1/monitoring/logs` | Monitoring history |
| GET | `/api/v1/incidents` | List incidents |
| GET | `/api/v1/incidents/{id}` | Incident detail |
| POST | `/api/v1/incidents/{id}/resolve` | Resolve incident |
| POST | `/api/v1/incidents/{id}/close` | Close incident |
| GET | `/api/v1/dashboard` | Dashboard data |
| GET | `/api/v1/statistics` | Network statistics |
| GET | `/api/v1/notifications` | Notification log |

## Network Health Score

Score (0–100) factors in average packet loss, latency, jitter, open incidents, and critical device count. Displayed on the dashboard.

## PostgreSQL Migration

Update `DATABASE_URL` in `.env`:

```
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/noc_db
```

Add `psycopg2-binary` to `backend/requirements.txt` and remove SQLite `connect_args` in `session.py` for production.

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for component diagrams and data flow.

## License

MIT
