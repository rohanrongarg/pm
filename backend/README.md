# Backend

FastAPI backend for the Project Management MVP.

## Run locally (without Docker)

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run tests

```bash
uv sync --dev
uv run pytest
```

## Endpoints

- `GET /` - serves exported frontend when available
- `GET /scaffold` - scaffold HTML page with sample API call button
- `GET /api/health` - health check
- `GET /api/hello` - sample JSON API response
- `POST /api/auth/login` - login with hardcoded credentials (`user` / `password`)
- `POST /api/auth/logout` - clear session
- `GET /api/auth/session` - current session status
- `GET /api/board` - get current user's board
- `PUT /api/board` - save current user's board
- `POST /api/ai/ping` - check OpenRouter connectivity (`2+2` style prompt)
- `POST /api/ai/chat` - AI chat with structured board updates
