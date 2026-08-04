# Spectre Frontend

Experimental React front-end for [Spectre](https://spectregrams.org/). Read-only in most panels; can create configs, generate spectrogram plots, and kick off recordings.

Aesthetic reference: TIS-100 (Zachtronics). Monochrome monospaced panels, hard-edged buttons, discreet Spectre watermark. All state ephemeral: reload resets the UI.

The front-end is a strict client of the existing backend HTTP API — no new endpoints, no changes to `backend/` or `cli/`, no CORS middleware added. Same-origin traffic in the browser is achieved via a Vite dev-server proxy: everything under `/api/*` is stripped and forwarded to the backend.

## Run (development)

Two terminals.

Terminal 1 — backend dev-server on port 5001:

```bash
docker compose -f docker-compose.dev.yml up spectre-dev-server
```

Terminal 2 — Vite dev-server on port 5173, proxying `/api` to `http://localhost:5001`:

```bash
cd frontend
npm ci
npm run dev
```

Open http://localhost:5173.

Point the proxy at a different backend by exporting `SPECTRE_BACKEND_URL` before `npm run dev`.

## Keyboard shortcuts

- `/` — focus the batch-browser tag filter
- `r` — focus the record duration input
- `n` — start creating a new config
- `esc` — close any modal

## Recording limitations (issue #192)

The backend recording endpoints (`POST /recordings/signal`, `POST /recordings/spectrogram`) block synchronously until the recording completes, and there is no status, progress, or cancel endpoint. Consequences for this UI:

- The "REC" chip in the top-right is a client-side visual only. Its timer is wall-clock, not server-progress.
- Recordings cannot be cancelled from the UI. Restart the backend to abort.
- Closing the browser tab orphans the client's view of an in-flight recording. The backend continues recording; batches will appear on the next reload of the batch browser.
- A recording started from another client (CLI, another browser tab) is invisible to this UI until it produces output files.

## Layout

Single-page dashboard, 12-col grid, no routing. Panels:

| Panel | Backend surface | Notes |
|-------|-----------------|-------|
| LOG STREAM | `GET /spectre-data/logs`, `.../raw` | Polls newest worker log while a recording is in-flight or `[TAIL]` is on. |
| RECEIVERS | `GET /receivers`, `.../connected`, `.../modes`, `.../model` | Modal shows JSON schema. |
| CONFIGS | `GET /spectre-data/configs/` | Selecting a row drives the CONFIG EDITOR. |
| REC | `POST /recordings/{signal,spectrogram}` | Guards duplicate-tag submissions client-side. |
| SPECTROGRAM VIEWER | `PUT /spectre-data/batches/plots`, `GET /spectre-data/batches/tags` | Renders returned PNG inline; recent-plots strip is in-memory. |
| BATCH BROWSER | `GET /spectre-data/batches/`, `.../<file>` | Groups by date; PNGs open in a lightbox. |
| LOGS | `GET /spectre-data/logs/`, `.../<file>/raw` | On-demand full-text viewer. |
| CONFIG EDITOR | `PUT`, `PATCH`, `DELETE /spectre-data/configs/<file>` | Dynamic form driven by receiver schema. Delete has dry-run preview. |

## Scripts

- `npm run dev` — Vite dev server on port 5173
- `npm run build` — Type-check and produce `dist/`
- `npm run typecheck` — Type-check only
- `npm run preview` — Preview a production build locally

## Out of scope

- Authentication, CORS middleware, WebSockets, SSE.
- Production deployment. `npm run build` produces `dist/` but there is no reverse-proxy story shipped in this repo.
- Client-side HDF5 rendering — all spectrogram visualisation goes through the server-rendered `PUT /plots` endpoint.
- Persistence of UI state across reloads.
- Responsive layout below ~1200px width.
- Test runner. Manual verification only.

## Fonts

The dashboard references VT323 (title / meter font) and IBM Plex Mono (body). Both are loaded from Google Fonts via `<link>` in `index.html`. Swap to self-hosted `.woff2` under `src/assets/fonts/` if offline use is required.
