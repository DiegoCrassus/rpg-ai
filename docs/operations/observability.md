# Observability

## Current Status

**Phase:** SDLC observability active — `app/infra/sdlc_obs/` implemented.
Application-level observability (backend services) is TBD.

## SDLC Observability — sdlc_obs

The `sdlc_obs` tool measures the AI-Native SDLC pipeline itself:
precision, cost, time, tool success, hallucination rate, completion rate, and regressions.

### Quick Start

```bash
make obs-init      # initialize SQLite database
make obs-server    # start dashboard at http://localhost:7700
```

### Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Precision** (completion rate) | completed runs / total runs per stage | ≥ 80% |
| **Cost** | sum(cost_usd) — OpenAI token cost per run | track, minimize |
| **Time** | avg(duration_ms) per stage | track, reduce |
| **Tool success rate** | tool_calls_success / tool_calls_total | ≥ 90% |
| **Hallucination rate** | runs with fabricated results / total | 0% target |
| **Completion rate** | completed / total per agent | ≥ 80% |
| **Regressions** | Doctor/tests failed after claimed success | 0 target |

### Architecture

```
app/infra/sdlc_obs/
├── schema.sql       ← SQLite schema + sdlc_metrics view
├── collector.py     ← read/write API for metrics
├── server.py        ← web dashboard (stdlib, port 7700)
└── hooks/
    ├── pre_task.py  ← emit run start (CLI + .cursor/hooks.json)
    └── post_task.py ← emit run end  (CLI + .cursor/hooks.json)

.cursor/hooks.json   ← sessionStart → pre, stop → post (automatic)
.cursor/hooks/sdlc_obs_session.py
```

### Instrumentation (automatic)

`.cursor/hooks.json` records each agent session:

| Cursor event | Script | Effect |
|--------------|--------|--------|
| `sessionStart` | `sdlc_obs_session.py pre` | opens run in SQLite |
| `stop` | `sdlc_obs_session.py post` | closes run with status `completed` |

Reinicie o Cursor após alterar `hooks.json` para recarregar os hooks.

### Instrumentation (manual, por tarefa)

Every agent task can emit detailed metrics via the CLI hooks:

```bash
# Start (pre-task hook step 7)
python3 app/infra/sdlc_obs/hooks/pre_task.py \
  --task "[AI][BACKEND] Add Plane endpoint" --stage implementation --agent implementer

# End (post-task hook step 6)
python3 app/infra/sdlc_obs/hooks/post_task.py \
  --status completed --cost 0.0048 --tokens-in 1200 --tokens-out 800 \
  --tools-total 5 --tools-ok 5 --tests-pass 12 --doctor 0
```

### Hallucination Detection

A `hallucination_flag` is set when:
1. Agent claimed Doctor passed but `doctor_exit_code = 1`
2. Agent claimed tests pass but `tests_failed > 0`
3. Agent cited a non-existent file or result
4. Human reviewer explicitly flags fabricated output

### Dashboard API

| Endpoint | Description |
|----------|-------------|
| `GET /` | HTML dashboard (auto-refresh 30s) |
| `GET /api/kpis` | Top-level KPIs JSON |
| `GET /api/summary` | Per-stage/agent aggregates JSON |
| `GET /api/runs?limit=N&stage=S` | Recent runs JSON |

---

## Application Observability (TBD)

When backend services are implemented, add:

| Signal | Tool | Status |
|--------|------|--------|
| Logs | Python `logging` | not_ready |
| Metrics | TBD (Prometheus or OpenTelemetry) | not_configured |
| Traces | OpenTelemetry | not_configured |
| Errors | TBD | not_configured |
| Alerts | TBD | not_ready |

### Log Levels Convention

| Level | When to use |
|-------|-------------|
| ERROR | Unrecoverable failure — always include context |
| WARNING | Recoverable failure or unexpected state |
| INFO | Significant business events |
| DEBUG | Detailed diagnostics — not enabled in production by default |

### Observability Checklist (Per Deployment)

- [ ] Error logging confirmed at all failure paths
- [ ] Key metrics defined and appearing
- [ ] Critical path has trace coverage
- [ ] Alert defined for service-down condition
- [ ] Runbook linked to each alert
