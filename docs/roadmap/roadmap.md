# Roadmap

## SDLC product lines

| Track | Document | Status |
|-------|----------|--------|
| **Studio Foundation** (engine + CLI) | [`sdlc-studio-mvp-roadmap.md`](sdlc-studio-mvp-roadmap.md) | Delivered (INVES-53) — historical name “MVP” |
| **Studio Service** (backend + UI + observability) | [`sdlc-studio-service-roadmap.md`](sdlc-studio-service-roadmap.md) | **Active** — next implementation |
| **Workflow Builder UX** (manual + E2E gates) | [`sdlc-studio-workflow-builder-ux-plan.md`](sdlc-studio-workflow-builder-ux-plan.md) | Active — INVES-100 epic |
| **Builder manual test script** | [`../operations/studio-workflow-builder-manual-test.md`](../operations/studio-workflow-builder-manual-test.md) | Required for WB QA |
| **SDLC enforcement** (hooks, CI, fail-closed) | [`sdlc-enforcement-roadmap.md`](sdlc-enforcement-roadmap.md) | Planned / in progress |
| **Investment product** (`app/`) | Phases 2–4 below | Separate from Studio |

## Current Phase: Foundation

**Status:** SDLC operating system initialized. Studio Foundation engine in `studio/`; Studio Service UI not started.

## Phase 1 — Foundation (current)

| Item | Status | Notes |
|------|--------|-------|
| SDLC YAML configuration | done | `.sdlc/*.yaml` |
| Python DSL and Doctor | done | `.sdlc/dsl/` |
| Cursor agent configuration | done | `.cursor/` |
| Documentation structure | done | `docs/` |
| App boundary definitions | done | `app/*/README.md` |

## Phase 2 — Backend Foundation (TBD)

| Item | Status | Notes |
|------|--------|-------|
| Python project structure | pending | `app/backend/` |
| Database models | pending | SQLAlchemy + SQLite/Supabase |
| API framework setup | pending | Framework TBD |
| First API endpoint | pending | Depends on product definition |
| Unit test setup | pending | pytest |
| CI/CD pipeline | pending | GitHub Actions |

## Phase 3 — Frontend Foundation (TBD)

| Item | Status | Notes |
|------|--------|-------|
| Frontend framework decision | pending | ADR needed |
| Project scaffold | pending | `app/frontend/` |
| Design system decision | pending | TBD |
| First UI component | pending | Depends on product definition |

## Phase 4 — Infrastructure (TBD)

| Item | Status | Notes |
|------|--------|-------|
| Docker setup | pending | `app/infra/` |
| CI/CD deployment | pending | GitHub Actions |
| Staging environment | pending | TBD |
| Production deployment | pending | TBD |

## Milestones

| Milestone | Target | Criteria |
|-----------|--------|----------|
| SDLC Foundation | 2026-05-26 | Doctor passes, all config in place |
| First Backend Service | TBD | API running locally with tests |
| First E2E Feature | TBD | Frontend + backend + tests + deployed |
| Production Ready | TBD | Monitoring, rollback, and runbook complete |

## Backlog (Unscheduled)

- Auth system
- User management
- Observability stack (OpenTelemetry + Sentry)
- Admin tooling
- Multi-environment deployment

---

*Update this file at each phase transition. Keep it honest — no aspirational dates without commitment.*
