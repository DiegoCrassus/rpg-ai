# studio/backend — Studio Service API

FastAPI service that exposes the SDLC Studio **control plane** over HTTP. Wraps the Foundation engine in `studio/` and reads authoritative repo configuration from `.sdlc/` and `.cursor/`.

**Not MarketPulse.** This package is isolated from `app/backend/src/marketpulse/`.

## Stack

- Python 3.11+
- FastAPI + Uvicorn
- Pydantic v2
- Imports `studio/` at repository root (compile, validate, canvas, readiness)

## Architecture

Full platform boundaries, OpenAPI route map (S1–S6), event schema, and mutation model:

[`docs/architecture/studio-service-platform.md`](../../docs/architecture/studio-service-platform.md)

## Layout

```text
studio/backend/
├── README.md
├── tests/
└── src/studio_service/
    ├── main.py
    ├── config.py
    ├── api/router.py          # prefix /studio
    ├── services/engine.py     # wraps studio.*
    └── schemas/               # OpenAPI models
```

## Run

```bash
# From repo root
make studio-dev
```

Or manually:

```bash
STUDIO_REPO_ROOT=$(pwd) PYTHONPATH=studio/backend/src:$PWD python -m uvicorn studio_service.main:app \
  --reload --host 127.0.0.1 --port 8100
```

OpenAPI: http://127.0.0.1:8100/docs

## API prefix

All JSON routes live under **`/studio/*`** (see architecture doc for phase map).

| Phase | Example routes |
|-------|----------------|
| S1 | `GET /studio/health`, `GET /studio/readiness`, `GET /studio/engine/canvas` |
| S2 | `GET /studio/canvas/full`, `GET /studio/canvas`, `GET /studio/canvas/nodes/{display_id}` |
| S3 | `GET /studio/obs/timeline`, `GET /studio/obs/events` (SSE) |
| S4 | `POST /studio/proposals` (preview only — no apply endpoint) |
| S5 | `GET /studio/registry/graph`, `GET /studio/validation/inspect`, `POST /studio/validation/run`, `POST /studio/doctor/run`, … |
| S6 | `GET /studio/integrations/plane/cards/{card}` |

## Boundaries

| Owns | Must not |
|------|----------|
| HTTP/WS orchestration, repo scanning, proposal preview | Duplicate compiler logic from `studio/` |
| Event fan-in (obs + gateway + handoff) | Write authoritative `.sdlc/` / `.cursor/` files |
| Plane/GitHub read proxies (S6) | Replace Cursor agent runtime or MCP in IDE |

## Tests

```bash
STUDIO_REPO_ROOT=$(pwd) PYTHONPATH=studio/backend/src:$PWD python -m pytest studio/backend/tests/ -v
```

## Related

- Foundation engine: [`studio/README.md`](../README.md)
- Observability store: [`app/infra/sdlc_obs/README.md`](../../app/infra/sdlc_obs/README.md)
- Frontend: [`studio/frontend/README.md`](../frontend/README.md)
- Roadmap: [`docs/roadmap/sdlc-studio-service-roadmap.md`](../../docs/roadmap/sdlc-studio-service-roadmap.md)
