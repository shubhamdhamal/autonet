# Telegram Notifications Setup

Get detailed NOC incident alerts in Telegram when a new incident is created.

## 1. Create a Telegram bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Choose a name and username for your bot
4. Copy the **HTTP API token** (looks like `7123456789:AAH...`)

## 2. Get your Chat ID

### Option A — Personal chat

1. Send any message to your new bot (e.g. `hello`)
2. Open in a browser (replace `YOUR_BOT_TOKEN`):

```
https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
```

3. Find `"chat":{"id":123456789` — that number is your **chat ID**

### Option B — Group channel

1. Add the bot to your NOC group
2. Send a message in the group
3. Call `getUpdates` as above
4. Use the group's chat ID (often negative, e.g. `-1001234567890`)

## 3. Configure environment variables

On your server, create or edit `.env` in the project root:

```env
TELEGRAM_ENABLED=true
TELEGRAM_BOT_TOKEN=7123456789:AAHxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TELEGRAM_CHAT_ID=123456789
TELEGRAM_PARSE_MODE=HTML
```

## 4. Restart the backend

```bash
cd ~/networking
docker compose down
docker compose up --build -d
```

## 5. Test the integration

```bash
curl -X POST http://localhost:8000/api/v1/notifications/telegram/test
```

Or from your PC (replace with your public IP):

```bash
curl -X POST http://YOUR_EC2_IP:8000/api/v1/notifications/telegram/test
```

You should receive a test message in Telegram.

Check status:

```bash
curl http://localhost:8000/api/v1/notifications/telegram/status
```

## What you'll receive on incident raise

Each alert includes:

- Incident number and severity
- Device name, IP, type, location
- Packet loss, latency (avg/min/max), jitter, response time
- Root cause and breach trigger info (3 consecutive cycles)
- Timestamp in **IST** and **UTC**

## Troubleshooting

| Problem | Fix |
|---------|-----|
| No messages | Ensure `TELEGRAM_ENABLED=true` and token/chat ID are set |
| `chat not found` | Send `/start` to the bot first, or add bot to the group |
| `Unauthorized` | Bot token is wrong — copy again from BotFather |
| Test works but no incident alerts | Wait ~90s for sim devices, or check `docker compose logs backend` |

## Security notes

- Never commit `.env` or bot tokens to git
- Restrict who can access the test endpoint in production
- Use a dedicated NOC group/channel for alerts
