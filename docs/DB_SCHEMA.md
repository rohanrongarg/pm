# Database Schema (MVP)

## Engine

- SQLite
- Database file path:
  - Default: `backend/data/pm.db`
  - Override with `PM_DB_PATH`

## Tables

### `users`

- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `username` TEXT UNIQUE NOT NULL
- `password` TEXT NOT NULL

MVP seed row:

- username: `user`
- password: `password`

### `sessions`

- `token` TEXT PRIMARY KEY
- `user_id` INTEGER NOT NULL (FK -> `users.id`)
- `created_at` TEXT NOT NULL (ISO timestamp)

Used for cookie-based auth via `pm_session` cookie.

### `boards`

- `user_id` INTEGER PRIMARY KEY (FK -> `users.id`)
- `board_json` TEXT NOT NULL
- `updated_at` TEXT NOT NULL (ISO timestamp)

`board_json` stores full Kanban state:

- `columns`: list of fixed columns with `id`, `title`, and `cardIds`
- `cards`: map of card IDs to card payloads (`id`, `title`, `details`)

## Lifecycle

- On startup, backend creates tables if they do not exist.
- On first board read for a user, backend creates a default board row.
- Board updates replace the stored JSON payload for that user.

## Why this design

- Matches MVP requirement to store board as JSON.
- Keeps implementation simple and easy to evolve.
- Supports future multi-user expansion by scoping rows to `user_id`.
