# Marketplace Analytics

Analytics service gateway for Canonical's marketplace applications. Collects anonymous event-based analytics from frontend clients and stores them in PostgreSQL.

## Architecture

Frontend applications use the [`@canonical/analytics-events`](https://www.npmjs.com/package/@canonical/analytics-events) npm package to send event batches to this service via `POST /analytics/events`. Events are validated, stored in PostgreSQL, and visualized through Grafana dashboards.

## Local development

### With Docker Compose

```bash
docker compose up --build
```

App runs at `http://localhost:9090`.

### Without Docker

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
POSTGRESQL_DB_CONNECT_STRING=postgresql://user:pass@localhost:5432/marketplace_analytics flask run
```

## Authentication

- `POST /analytics/events` is public (no auth required)
- `GET /analytics/events` and `/dashboard` require Ubuntu SSO login with `canonical-webmonkeys` Launchpad team membership
- `/login` - redirects to Ubuntu SSO
- `/logout` - clears session

## Dashboard

Visit `/dashboard` to view events in a table with filters (app name, event type, session ID) and pagination. Requires login.

## API

### Post events

```bash
curl -X POST http://localhost:9090/analytics/events \
  -H "Content-Type: application/json" \
  -d '{
    "app_name": "snapcraft",
    "events": [
      {
        "event_type": "click",
        "session_id": "abc-123",
        "target": "install_button"
      },
      {
        "event_type": "page_view",
        "session_id": "abc-123",
        "target": "snap_details_page"
      }
    ]
  }'
```

Request body:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `app_name` | string | yes | Application identifier (`snapcraft`, `charmhub`) |
| `events` | array | yes | List of events (1-100) |

Each event:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `event_type` | string | yes | `click`, `hover`, `view`, or `page_view` |
| `session_id` | string | yes | Anonymous session identifier (max 255 chars) |
| `event_source` | string | no | `frontend` (default) or `backend` |
| `target` | string | no | Element identifier (max 255 chars) |
| `url` | string | no | Page URL where the event occurred (max 2048 chars) |
| `attributes` | object | no | Custom key-value pairs (max 4KB JSON) |

Returns `204 No Content` on success.

### CORS

The ingestion endpoint accepts requests from:
- `https://snapcraft.io`
- `https://charmhub.io`
- `https://*.demos.haus`
- `http(s)://localhost:*`

### Rate limiting

`POST /analytics/events` is limited to 1000 requests per minute per client IP.

### Get events

Requires authentication.

```bash
# All events
curl http://localhost:9090/analytics/events

# Filter by app
curl http://localhost:9090/analytics/events?app_name=snapcraft

# Filter by event type
curl http://localhost:9090/analytics/events?event_type=click

# Filter by session
curl http://localhost:9090/analytics/events?session_id=abc-123

# Pagination
curl "http://localhost:9090/analytics/events?page=1&per_page=20"
```

### Health check

```bash
curl http://localhost:9090/db-test
```

## Database

Events are stored in a single `events` table with indexes on `timestamp`, `event_type`, `session_id`, and `app_name`.

| Column | Type | Description |
|--------|------|-------------|
| `event_id` | UUID | Primary key |
| `event_type` | String(50) | Event type |
| `event_source` | String(50) | `frontend` or `backend` |
| `timestamp` | DateTime(tz) | Server-set timestamp |
| `session_id` | String(255) | Anonymous session ID |
| `app_name` | String(100) | Source application |
| `target` | String(255) | Element identifier |
| `url` | Text | Page URL |
| `attributes` | JSON | Custom attributes |

Migrations are managed with Flask-Migrate:

```bash
flask db migrate -m "description"
flask db upgrade
```
