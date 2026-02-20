# Marketplace Analytics

Analytics service for the marketplace. Collects anonymous event-based analytics (clicks, hovers, views) from marketplace applications.

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
curl -X POST http://localhost:9090/analytics/events -H "Content-Type: application/json" -d '{"app_name": "snapcraft", "events": [{"event_type": "click", "session_id": "abc-123", "target": "install_button"}, {"event_type": "view", "session_id": "abc-123", "target": "description_section", "attributes": {"duration_ms": 5000}}]}'
```

Request body:

```json
{
  "app_name": "snapcraft",
  "events": [
    {
      "event_type": "click",
      "session_id": "abc-123",
      "target": "install_button"
    },
    {
      "event_type": "view",
      "session_id": "abc-123",
      "target": "description_section",
      "attributes": {
        "duration_ms": 5000
      }
    }
  ]
}
```

Returns `204 No Content` on success.

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
