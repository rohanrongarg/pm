# Frontend Overview

This folder contains the Next.js frontend for the Project Management MVP.

## Stack

- Next.js App Router (`next`, `react`, `react-dom`)
- TypeScript
- Tailwind CSS v4
- `@dnd-kit` for drag-and-drop
- Vitest + Testing Library for unit/integration tests
- Playwright for end-to-end tests

## Key Files

- `src/app/page.tsx`: app entry point; renders `KanbanBoard`.
- `src/components/KanbanBoard.tsx`: top-level board state and drag/drop orchestration.
- `src/components/KanbanColumn.tsx`: column UI, editable title, drop zone, add-card entry.
- `src/components/KanbanCard.tsx`: sortable card UI and delete action.
- `src/components/NewCardForm.tsx`: inline create-card form.
- `src/lib/kanban.ts`: board types, seed data, and `moveCard` helper.
- `src/app/globals.css`: global styles and design tokens.

## Current Behavior

- On `/`, unauthenticated users must log in (`user` / `password`).
- After login, the app loads one persisted board for the session user.
- Column titles are editable inline.
- Cards can be created and deleted.
- Cards can be moved within and across columns via drag-and-drop.
- Board changes are persisted through `/api/board`.
- Right sidebar AI chat posts to `/api/ai/chat` and can apply board updates.

## Frontend Test Surface

- Unit/integration:
  - `src/components/KanbanBoard.test.tsx`
  - `src/lib/kanban.test.ts`
- End-to-end:
  - `tests/kanban.spec.ts`

Run from `frontend/`:

- `npm run test:unit`
- `npm run test:e2e`
- `npm run test:all`

## Editing Guidance

- Keep UI behavior simple; do not add extra features outside MVP scope.
- Preserve the existing color tokens from `src/app/globals.css`.
- Keep components small and focused; place reusable logic in `src/lib/`.
- Prefer updating existing tests when behavior changes; add new tests only where needed.
- When integrating backend, keep API code isolated so board UI stays clean.
