# Code Review

**Scope:** `main...HEAD` (branch `feat/mvp-stack-fastapi-ai-chat`) plus uncommitted working-tree changes.
**Reviewed:** card inline-editing feature, login field handling, dev API-proxy config.
**Date:** 2026-06-05

## Files reviewed

- `frontend/src/app/page.tsx` — login field defaults + clearing effect, `autoComplete` attrs
- `frontend/src/components/KanbanBoard.tsx` — new `handleUpdateCard`
- `frontend/src/components/KanbanCard.tsx` — inline edit form, drag disabled while editing
- `frontend/src/components/KanbanColumn.tsx` — `onUpdateCard` prop threading
- `frontend/src/components/KanbanBoard.test.tsx` — edit test
- `frontend/next.config.ts` — dev-only `/api` rewrite (uncommitted)
- `frontend/package-lock.json` — lockfile drift (uncommitted)

Overall this is a clean, well-contained change. No crashing or data-loss bugs found. Findings below are minor; the first is a behavior gap versus the commit's stated intent.

---

## Findings

### 1. Login fields are not cleared on authentication failure (behavior gap)

**File:** `frontend/src/app/page.tsx:75-80`, `:101-126`
**Severity:** Low–Medium

The HEAD commit message states the change is to "clear fields on authentication failure," but the implementation does not do this. The new effect only fires when its deps change:

```ts
useEffect(() => {
  if (!authLoading && !authenticated) {
    setLoginUsername("");
    setLoginPassword("");
  }
}, [authLoading, authenticated]);
```

On a failed login, `handleLogin` sets `loginError` and returns early (`:114-117`) — it does **not** reset the fields, and neither `authLoading` nor `authenticated` changes, so the effect never runs. Result: after a wrong password, the typed username/password remain in component state and in the visible inputs.

The effect does work for the two cases where the deps actually change: initial load (no-op, fields already empty) and logout (`handleLogout` sets `authenticated=false`).

**Fix:** either clear the fields directly in the `!response.ok` branch of `handleLogin`, or drop the "clear on failure" intent if persisting the typed value is the desired UX (arguably better, lets the user fix a typo). Reconcile code and commit message.

### 2. `rewrites()` under `output: "export"` — verify the dev proxy actually applies

**File:** `frontend/next.config.ts:5-16` (uncommitted)
**Severity:** Low (needs verification)

The config sets `output: "export"` and adds a dev-only `rewrites()` proxying `/api/:path*` to `http://localhost:8000`. Next.js treats `rewrites` as unsupported under `output: "export"` and prints a warning. In practice `next dev` generally still applies rewrites (export only governs the static build), and this is the documented local-dev proxy mechanism — so it likely works on Next 16.1.6. Confirm by running `npm run dev` and hitting an `/api/*` route; if requests 404 against the dev server, the proxy is being ignored and an alternative (e.g. a custom dev middleware or pointing fetches directly at `:8000` in dev) is needed.

### 3. Spurious lockfile change: `fsevents` no longer `dev`-only

**File:** `frontend/package-lock.json` (uncommitted)
**Severity:** Low (cleanup)

The only lockfile change removes `"dev": true` from the `fsevents@2.3.2` entry, recategorizing it from a dev-only optional dependency to a production optional dependency. This is unrelated to the feature and almost certainly accidental drift from an `npm install` run. It can cause `fsevents` to be pulled into production installs on macOS. Recommend reverting this hunk so the lockfile change is intentional and scoped.

### 4. Duplicated `"No details yet."` placeholder fallback

**File:** `frontend/src/components/KanbanBoard.tsx:82`, `:123`
**Severity:** Low (cleanup)

`handleAddCard` and the new `handleUpdateCard` both inline `details: details || "No details yet."`. The placeholder string is now repeated; extracting a shared constant (e.g. `DEFAULT_DETAILS` in `lib/kanban.ts`) avoids divergence if the wording changes. Minor.

---

## Notes (not defects)

- **KanbanCard edit state during external updates:** `title`/`details` are local `useState` seeded from props; `handleStartEdit`/`handleCancelEdit` re-seed from `card.*` on each open/cancel, and the read-only view renders `card.*` directly. So a board change while *not* editing is reflected correctly, and an in-progress edit intentionally preserves the user's input. No staleness bug.
- **Drag-while-editing:** `useSortable({ disabled: isEditing })` plus the conditional spread of `attributes`/`listeners` correctly prevents drag from hijacking input interaction during editing.
- **Editing the placeholder:** clearing details and saving stores `"No details yet."`, which then appears as editable text on the next edit. Cosmetic; acceptable for MVP.
- **Accessibility:** edit/save/cancel controls use `aria-label`s and proper `type="button"`/`type="submit"`; the test relies on these, which is good.
