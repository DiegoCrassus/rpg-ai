# Studio Service — Operator Guide

Local SDLC console: FastAPI on **8100**, Vite UI on **5174**. Plane and GitHub remain source of truth; Studio surfaces derived views and propose-only patches.

## Quick start

```bash
# One-time
cd app/studio-frontend && npm install

# API + UI (repo root)
make studio-dev
```

- UI: http://127.0.0.1:5174  
- API: http://127.0.0.1:8100/studio/health  
- OpenAPI: http://127.0.0.1:8100/docs  

`STUDIO_REPO_ROOT` defaults to the repo that contains `.sdlc/sdlc.yaml`.

## Optional API auth (S7)

When `STUDIO_AUTH_TOKEN` is set, every `/studio/*` route requires:

```http
Authorization: Bearer <token>
```

**Dev (no token):** leave `STUDIO_AUTH_TOKEN` unset — open access on `127.0.0.1` only.

**With token:**

```bash
export STUDIO_AUTH_TOKEN='choose-a-long-local-secret'
STUDIO_REPO_ROOT=$(pwd) PYTHONPATH=app/studio-backend/src:$PWD \
  python3 -m uvicorn studio_service.main:app --host 127.0.0.1 --port 8100
```

Frontend (Vite) must send the same value:

```bash
# app/studio-frontend/.env.local (gitignored)
VITE_STUDIO_AUTH_TOKEN=choose-a-long-local-secret
```

CORS preflight (`OPTIONS`) is not challenged by auth middleware.

## Make targets

| Target | Purpose |
|--------|---------|
| `make studio-dev` | API :8100 + UI dev server :5174 |
| `make studio-api` | API only (background-friendly) |
| `make studio-smoke` | HTTP smoke against running API |
| `make studio-e2e` | Build UI + Playwright (9 tests: smoke + builder) |

## Smoke and E2E

```bash
# API smoke (API must be running)
make studio-smoke

# Playwright: 3 smoke routes + 6 builder tests (9 total)
make studio-e2e
```

E2E harness (`tests/e2e/run-studio-e2e.sh`) builds the UI, starts API + preview, then runs Playwright.

| Spec | Tests | Routes / scope |
|------|-------|----------------|
| `tests/e2e/studio/smoke.spec.ts` | 3 | `/`, `/workflows`, `/observability` |
| `tests/e2e/studio/builder.spec.ts` | 6 | `/builder` — E2E-B1…B6 |

**E2E-B1…B6 (builder):** heading visible; ≥10 stages; drag connection; inspector agent select; proposal disabled/enabled; unified diff non-empty.

CI check name: **Studio E2E (smoke + builder)**.

**Manual builder QA:** [`docs/operations/studio-workflow-builder-manual-test.md`](operations/studio-workflow-builder-manual-test.md) (required for WB card PASS — not replaced by Playwright alone).

## Enforcement visibility

- **Dashboard** — “Enforcement (fail-closed)” widget shows the latest `gateway.shell_denied` from `GET /studio/obs/timeline?category=gateway`.
- **Observability** — full timeline + SSE at `/observability`.

Aligns with [sdlc-enforcement-roadmap.md](roadmap/sdlc-enforcement-roadmap.md).

## Validation

```bash
make sdlc-doctor
cd app/studio-backend && python3 -m pytest tests/test_auth.py tests/test_obs.py -q
cd app/studio-frontend && npm run test && npm run build
pytest studio/ -q
```

## Related docs

- [studio-service-platform.md](architecture/studio-service-platform.md)
- [sdlc-studio-service-roadmap.md](roadmap/sdlc-studio-service-roadmap.md)
- [studio-workflow-builder-manual-test.md](operations/studio-workflow-builder-manual-test.md)
- [sdlc-studio-workflow-builder-ux-plan.md](roadmap/sdlc-studio-workflow-builder-ux-plan.md)
