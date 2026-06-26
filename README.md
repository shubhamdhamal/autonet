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

## Environment files

| File | Purpose | Commit to Git? |
|------|---------|----------------|
| `.env.example` | Template with placeholder values | **Yes** |
| `.env` | Your real secrets (Telegram token, etc.) | **Never** |

Docker Compose and the backend read **`.env` only**. Deleting `.env` disables Telegram because variables fall back to empty/disabled defaults.

**On your server (one-time setup):**

```bash
cd ~/networking
cp .env.example .env
nano .env   # set TELEGRAM_ENABLED=true and your real token/chat ID
docker compose up --build -d
```

**Never delete `.env` on the server** — keep it alongside the project (it is gitignored).

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

## How Monitoring Works

This system uses **active monitoring** from the NOC server — **no login to the target device is required**.

```
[NOC Server]  ----ICMP ping---->  [Device IP]
      ↑
  measures reply time, drops, jitter
```

### What happens every 30 seconds

For each device with monitoring enabled:

1. Send **4 ICMP pings** to the device's IP address (via `ping3`)
2. Record round-trip time for each reply → **latency**
3. Count unanswered pings → **packet loss** (%)
4. Measure variation between ping times → **jitter**
5. Store results in `monitoring_logs` and evaluate incident rules

### Normal vs simulation devices

| Type | Profile | How metrics are obtained |
|------|---------|--------------------------|
| Real targets | `normal` | Actual ICMP ping to the IP (e.g. `8.8.8.8`, `1.1.1.1`) |
| Demo/lab | `packet_loss_20`, `high_latency`, etc. | **Simulated** metrics — no real device contacted |

### What you measure vs what you don't

| With ping only (this app) | Requires SNMP/SSH login |
|---------------------------|-------------------------|
| Reachability to an IP | CPU / memory usage |
| Round-trip latency | Interface error counters |
| Packet loss & jitter | Routing tables, config |
| Path quality from NOC server | Per-port traffic stats |

### Monitoring timing

| Setting | Default | Description |
|---------|---------|-------------|
| `MONITOR_INTERVAL_SECONDS` | 30 | Full monitoring cycle interval |
| `MONITOR_PROBE_COUNT` | 4 | Pings per device per cycle |
| `MONITOR_TIMEOUT_SECONDS` | 1.0 | Max wait per ping |
| Incident threshold | 3 cycles | ~90 seconds of breach before incident |

### Limitations

- Many firewalls **block ICMP** — device may show as down even when HTTP/SSH works
- You measure reachability **to an IP**, not internal device health
- Pinging a public IP (e.g. `8.8.8.8`) tests **your server's path to the internet**, not your office router unless you ping the router's IP

## Incident Rules

Incidents are created when **either** condition holds for **3 consecutive** 30-second cycles:

- Packet Loss > 10%
- Latency > 200ms

- No duplicate open incidents per device
- Auto-closed when metrics return to normal
- Console notification printed on creation
- **Telegram alerts** (optional) with detailed incident info — see [docs/TELEGRAM_SETUP.md](docs/TELEGRAM_SETUP.md)

## Telegram Notifications

When `TELEGRAM_ENABLED=true`, the system sends a detailed HTML message to your Telegram chat on every new incident:

- Incident number, severity, status
- Device name, IP, type, location, simulation profile
- Packet loss, latency, jitter, response time
- Root cause and breach trigger details
- Timestamps in IST and UTC

```bash
# Test after configuring .env
curl -X POST http://localhost:8000/api/v1/notifications/telegram/test
```

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
| GET | `/api/v1/notifications/telegram/status` | Telegram config status |
| POST | `/api/v1/notifications/telegram/test` | Send test Telegram message |

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
