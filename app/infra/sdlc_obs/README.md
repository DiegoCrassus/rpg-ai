# SDLC Observability (`sdlc_obs`)

> **Manifest index:** [`.sdlc/runtime/manifest.yaml`](../../.sdlc/runtime/manifest.yaml)
> **Studio UI:** `GET /studio/obs/*` (primary) · **Legacy:** `make obs-server` (port 7700)

SQLite timeline for gateway events, run spans, and KPI aggregates. Hooks append here; Studio reads via `ObsStoreService`.

## Paths (manifest-aligned)

| Artifact | Path |
|----------|------|
| SQLite DB | `app/infra/sdlc_obs/data/sdlc_obs.db` |
| Run state | `.sdlc_obs_state.json` (repo root, ephemeral) |
| Stage ledger | `.sdlc/manifest/executions.jsonl` |
| Learning events | `.sdlc/learning/data/events.jsonl` |

## Quick start

```bash
make obs-init
make studio-dev    # preferred observability UI
make obs-server    # legacy JSON API on :7700
```

## Package layout

```
app/infra/sdlc_obs/
├── schema.sql
├── db.py
├── store.py       ← EventStore (timeline)
├── collector.py   ← run KPIs
├── server.py      ← legacy dashboard
├── auditor.py     ← make sdlc-audit / CI
└── hooks/
    ├── pre_task.py
    └── post_task.py
```

## Boundaries

- **Authoritative process:** `.sdlc/process/lifecycle-model.yaml` — not stored here.
- **Workboard evidence:** Plane cards — not local files.
- Studio displays derived data only; never mutates `.sdlc/` or `.cursor/`.
