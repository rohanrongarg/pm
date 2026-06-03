# Project Plan: Project Management MVP

## Scope and Assumptions

- MVP is local-only and runs in Docker.
- Login credentials are hardcoded to `user` / `password`.
- One board per user.
- Columns are fixed in count for MVP; only renaming is supported.
- Backend persists board state in SQLite, with board content stored as JSON.
- Auth is cookie/session based so refresh keeps the user signed in.
- Frontend tests use Vitest + Playwright; backend tests use pytest.
- Playwright E2E execution is deferred for now by user request.
- We pause for user sign-off at the end of each part before starting the next part.

## Part 1: Plan and Existing Frontend Documentation

### Implementation checklist

- [x] Expand `docs/PLAN.md` from a high-level list into detailed execution steps.
- [x] Add test plan and success criteria for each part.
- [x] Create `frontend/AGENTS.md` to document the current frontend architecture and conventions.
- [x] Share plan with user and get approval to continue.

### Tests

- [x] Manual review of the updated plan for clarity, sequencing, and completeness.

### Success criteria

- [x] Plan is detailed enough to execute part-by-part without ambiguity.
- [x] Frontend documentation is accurate to the current codebase.
- [x] User explicitly approves the plan.

## Part 2: Scaffolding (Docker + FastAPI + Scripts)

### Implementation checklist

- [x] Add backend FastAPI app scaffold in `backend/`.
- [x] Add app entrypoint and health/API sample routes.
- [x] Add Dockerfile that runs the FastAPI scaffold (frontend build integration lands in Part 3).
- [x] Add docker-compose (or equivalent) for local run with mounted env/config.
- [x] Add start/stop scripts in `scripts/` for macOS, Linux, and Windows.
- [x] Serve a simple hello page and one hello API route from backend to prove runtime.
- [x] Add backend dependency management with `uv` in-container.

### Tests

- [x] Build image successfully.
- [x] Start container with script and verify backend is reachable.
- [x] Verify hello HTML route returns 200.
- [x] Verify hello API route returns expected JSON.
- [x] Stop scripts terminate services cleanly.

### Success criteria

- [x] One command/script starts the local stack.
- [x] FastAPI serves both HTML and JSON hello endpoints.
- [ ] Start/stop scripts work on all target OS paths.

## Part 3: Serve Existing Frontend from FastAPI

### Implementation checklist

- [x] Configure frontend production build output for static serving.
- [x] Integrate frontend build into Docker image build.
- [x] Configure FastAPI static file serving at `/`.
- [x] Ensure existing Kanban demo renders correctly in container runtime.
- [x] Keep current frontend tests operational.

### Tests

- [x] Frontend unit tests pass.
- [ ] Frontend e2e smoke test passes against containerized app. (deferred by user request)
- [x] Route `/` renders the Kanban board with 5 columns.

### Success criteria

- [x] Containerized app serves the existing Kanban UI at `/`.
- [ ] No regression in current frontend interactions (rename/add/remove/drag). (pending deferred e2e run)

## Part 4: Fake Sign-In and Logout

### Implementation checklist

- [x] Add backend auth endpoints for login/logout/session-check.
- [x] Implement hardcoded credential validation (`user` / `password`).
- [x] Set secure cookie-based session state for authenticated access.
- [x] Gate `/` so unauthenticated users see login first.
- [x] Add logout action that clears session and returns to login.
- [x] Keep UX simple and consistent with the project color palette.

### Tests

- [x] Backend tests for login success/failure and logout.
- [x] Frontend unit test for login form behavior.
- [ ] Integration/e2e test: unauthenticated user is redirected/gated. (deferred by user request)
- [ ] Integration/e2e test: valid login reaches board; logout returns to login. (deferred by user request)

### Success criteria

- [x] Only authenticated users can reach Kanban UI.
- [x] Page refresh preserves auth status until logout.

## Part 5: Database Modeling and Documentation

### Implementation checklist

- [x] Define SQLite schema for users and board storage.
- [x] Store board content as JSON payload per user board.
- [x] Add migration/init logic to create DB/tables if missing.
- [x] Document schema and data lifecycle in `docs/`.
- [x] Get user sign-off on schema and data access approach.

### Tests

- [x] Backend unit tests for DB initialization and seed/default data path.
- [x] Backend test for read/write round trip of board JSON.

### Success criteria

- [x] DB initializes automatically on first run.
- [x] Schema supports current MVP and near-term multi-user growth.
- [x] User approves documented schema approach.

## Part 6: Backend Kanban API

### Implementation checklist

- [x] Add authenticated API routes for board read/update.
- [x] Implement service/repository layer to isolate DB access.
- [x] Validate payload shape before DB writes.
- [x] Return stable API contracts for frontend usage.
- [x] Ensure board is scoped to authenticated user.

### Tests

- [x] Unit tests for service and repository logic.
- [x] API tests for happy path and invalid payloads.
- [x] API tests for auth-required behavior and per-user scoping.

### Success criteria

- [x] Backend fully supports loading and persisting Kanban board data.
- [x] Errors are predictable and returned in a consistent format.

## Part 7: Frontend + Backend Integration

### Implementation checklist

- [x] Replace in-memory board initialization with backend fetch on load.
- [x] Persist rename/add/delete/move operations through backend API.
- [x] Add loading/error states for network operations.
- [x] Keep drag-and-drop UX responsive while saving.
- [x] Ensure logout/login transitions rehydrate correct board state.

### Tests

- [x] Frontend unit tests for API client and state updates.
- [x] Integration tests for board persistence across refresh.
- [ ] E2E tests for main board flows using real backend API. (deferred by user request)

### Success criteria

- [x] Board changes survive refresh/restart through SQLite persistence.
- [x] Frontend behavior remains smooth and stable.

## Part 8: AI Connectivity via OpenRouter

### Implementation checklist

- [x] Add backend OpenRouter client with env-based API key loading.
- [x] Configure model to `openai/gpt-oss-120b`.
- [x] Add backend endpoint/service to run a simple connectivity prompt.
- [x] Add robust timeout and error handling for upstream failures.

### Tests

- [x] Unit tests for request payload construction.
- [x] Integration test (mocked) for successful AI response.
- [x] Manual/API smoke test with prompt `"2+2"` to confirm live connectivity.

### Success criteria

- [x] Backend can successfully call OpenRouter using configured model.
- [x] Failures surface clear actionable errors.

## Part 9: Structured AI Response with Board Context

### Implementation checklist

- [x] Define structured output schema including assistant message text and optional board mutation operations.
- [x] Add backend endpoint that sends current board JSON, user prompt, and conversation history.
- [x] Parse and validate structured output.
- [x] Apply AI-proposed board updates only when schema-valid.
- [x] Persist resulting board state.

### Tests

- [x] Unit tests for schema validation and parsing.
- [x] Unit tests for board mutation application.
- [x] Integration tests for response-only and response+mutation paths.
- [x] Integration tests for malformed AI output fallback handling.

### Success criteria

- [x] AI responses always parse into a safe, known structure.
- [x] Valid AI mutations update persisted board correctly.
- [x] Invalid AI output does not corrupt board state.

## Part 10: AI Chat Sidebar in Frontend

### Implementation checklist

- [x] Add right sidebar chat UI with message history.
- [x] Connect chat submit to backend AI endpoint.
- [x] Render assistant responses and optimistic/pending states.
- [x] Apply returned board mutations and re-render board immediately.
- [x] Keep layout clean, responsive, and aligned with project colors.

### Tests

- [x] Frontend unit tests for chat state management.
- [x] Integration tests for chat request/response lifecycle.
- [ ] E2E tests for end-to-end user prompt -> AI response -> board update flow. (deferred by user request)

### Success criteria

- [x] Chat is usable, visually polished, and reliable.
- [x] AI-triggered board updates appear without manual reload.
- [x] Core Kanban interactions continue to work after chat integration.