# Scripts Overview

This folder contains cross-platform helper scripts for running the local Docker stack.

## Files

- `start.sh`: start app on macOS/Linux (`docker compose up --build -d`)
  - Loads `.env` first if present so `OPENROUTER_API_KEY` can flow into container.
- `stop.sh`: stop app on macOS/Linux (`docker compose down --remove-orphans`)
- `start.bat`: start app on Windows Command Prompt
- `stop.bat`: stop app on Windows Command Prompt

## Guidance

- Keep scripts minimal and easy to debug.
- Prefer `docker compose` commands from the project root.
- Print clear success/failure output for users.