# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack project management MVP: a Kanban board with AI chat integration. Single Docker container serves both a Next.js frontend (built to static HTML) and a FastAPI backend on port 8000.

## Commands

### Frontend (`frontend/`)

```bash
npm install
npm run dev          # Dev server (port 3000)
npm run build        # Build static output to frontend-dist/ (used by Docker)
npm run lint
npm run test:unit    # Vitest unit tests
npm run test:e2e     # Playwright E2E
npm run test:all     # Both test suites
```

Run a single Vitest test file:
```bash
npx vitest run src/components/__tests__/KanbanCard.test.tsx
```

### Backend (`backend/`)

```bash
uv sync              # Install dependencies
uv sync --dev        # Install with dev dependencies
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
uv run pytest        # All tests
uv run pytest tests/test_auth.py  # Single test file
```

### Docker (full stack)

```bash
./scripts/start.sh   # Build and start (macOS/Linux)
./scripts/stop.sh    # Stop (macOS/Linux)
```

Requires `.env` file at project root with `OPENROUTER_API_KEY`.

## Architecture

### Request Flow

Browser → FastAPI (`/api/*`) → SQLite  
Browser → FastAPI (`/`) → serves static files from `frontend-dist/` (Next.js static export)

In production (Docker), the FastAPI backend serves the frontend. In local development, Next.js dev server runs separately on port 3000 and proxies API calls to the FastAPI backend.

### Backend (`backend/app/`)

- `main.py` — FastAPI app with lifespan, all route definitions (auth, board, AI, static)
- `db.py` — SQLite init, session management, board CRUD (board stored as JSON blob per user)
- `schemas.py` — Pydantic models for all request/response shapes
- `ai.py` — OpenRouter HTTP client; parses structured AI responses that can include board mutations

Auth is session-based with hardcoded credentials (user/password), cookies stored in SQLite. Board state is a single JSON blob per user.

### Frontend (`frontend/src/`)

- `app/page.tsx` — Root page; handles auth gate, board fetch, board state
- `components/KanbanBoard.tsx` — Board container with `@dnd-kit` drag-and-drop and chat sidebar
- `components/KanbanCard.tsx` — Individual card with inline editing
- `lib/kanban.ts` — Board data types (`BoardData`, `Column`, `Card`) and initial state

State management is local React state in `page.tsx`. Board saves are queued and batched to reduce API calls; UI updates optimistically.

### AI Chat

The AI receives board context and can return both a text response and structured board mutations (add/move/delete cards). Model: `openai/gpt-oss-120b` via OpenRouter.

### Styling

Tailwind CSS v4 with custom CSS variables: `--color-accent` (yellow), `--color-primary` (blue), `--color-secondary` (purple), `--color-navy` (dark), `--color-gray`. Fonts: Space Grotesk (display), Manrope (body).

## Development Conventions (from AGENTS.md)

- Use latest library versions and idiomatic approaches
- Simplicity over over-engineering; no unnecessary defensive programming  
- No scope creep; focus on MVP only
- No emojis in code or docs
- Identify root causes before fixing bugs; do not patch over symptoms

## Key Config

- `PM_DB_PATH` env var overrides the SQLite database path (default: `./pm.db`)
- `OPENROUTER_API_KEY` required for AI chat features
- `frontend/next.config.ts` sets `output: 'export'` and `distDir: '../frontend-dist'`
