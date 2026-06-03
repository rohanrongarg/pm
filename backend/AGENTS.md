# Backend Overview

This folder contains the FastAPI backend for the Project Management MVP.

## Current State

- `app/main.py` exposes:
  - `GET /` static frontend serving (when `frontend-dist` exists).
  - `GET /scaffold` simple HTML scaffold page with a button that calls sample API.
  - `GET /api/health` health check endpoint.
  - `GET /api/hello` sample JSON API endpoint.
  - auth routes (`/api/auth/*`) with cookie sessions.
  - board routes (`/api/board`) backed by SQLite.
  - AI routes (`/api/ai/*`) via OpenRouter.
- `app/db.py` handles SQLite initialization, sessions, and board persistence.
- `app/schemas.py` defines API and board schemas.
- `app/ai.py` handles OpenRouter calls and structured response parsing.
- `tests/` includes backend tests for auth, board, and AI flow.
- Python dependencies are managed with `uv` via `pyproject.toml`.

## Conventions

- Keep backend code simple and explicit.
- Use FastAPI route handlers plus small service helpers when logic grows.
- Add pytest coverage as features are added.
- Keep API contracts stable and typed.

## Local Run

From `backend/`:

```bash
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```