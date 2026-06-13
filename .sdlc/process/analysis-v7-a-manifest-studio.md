# Analysis A — Manifest-first observability & Studio alignment

> **Lens:** manifest as single runtime index; Studio as observability UI (not parallel truth).
> **Date:** 2026-06-13 · **Scope:** `.sdlc/`, `studio/`, `app/infra/sdlc_obs/`, hooks

---

## 1. Thesis

Observability must **read the manifest**, not invent parallel stores. Studio is the **viewer + SSE bus** over manifest-declared runtime paths. Authoritative process stays in `.sdlc/process/lifecycle-model.yaml` + `manifest/catalog.yaml`.

---

## 2. Current gap map

| Layer | Designed | Actual | Severity |
|-------|----------|--------|----------|
| **L0 manifest** | `catalog.yaml` reading_order + runtime paths | No `runtime/manifest.yaml`; obs paths scattered in docs | P0 |
| **L2 stage ledger** | `manifest/executions.jsonl` | 2 lines (gateway_block only) | P1 |
| **L3 learning** | `learning/data/events.jsonl` | Missing / empty | P1 |
| **L4 obs SQLite** | `app/infra/sdlc_obs/data/sdlc_obs.db` | Package **never committed** — Studio broken | P0 |
| **Studio compiler** | Derived IR from SDLC | Reads **deprecated shims** (`stages/lifecycle.yaml`, `gates/paths.yaml`) | P0 |
| **Studio ObsStore** | Bridge to sdlc_obs | ImportError at runtime | P0 |

---

## 3. Manifest-first observability model

```text
.sdlc/runtime/manifest.yaml     ← machine index (paths only, no logic)
        │
        ├── manifest/executions.jsonl   stage/gateway ledger (Harness L2)
        ├── learning/data/events.jsonl  task rewards (Harness L3)
        ├── learning/policy_memory.yaml policy hints (Harness L4)
        ├── memory/session-gate.json    gate state
        ├── memory/orchestrator-handoff.md routing
        └── app/infra/sdlc_obs/data/sdlc_obs.db  unified timeline (Studio)
```

**Principle:** hooks append to **manifest paths**; Studio **never** owns authoritative YAML. Studio reads manifest index + SQLite timeline + JSONL tails.

---

## 4. Studio alignment requirements

| Studio component | Must read | Must not read |
|------------------|-----------|---------------|
| `compiler_core.py` | `lifecycle-model.yaml`, `transitions.yaml` (metadata overlay), registry | Shim-only without model |
| `pipeline_metadata.py` | `lifecycle-model.yaml` write_policy, `catalog.yaml` agents | `gates/paths.yaml` as SoT |
| `obs_store.py` | `runtime/manifest.yaml` → sqlite path | Ad-hoc path guesses |
| Workflow builder | `lifecycle-model` stage ids | Duplicate stage YAML |
| Event bus / SSE | `EventStore.build_timeline` | Local-only ring without SQLite |

---

## 5. gate vs gateways (semantic split — keep both names, one write SoT)

| Module | Role | Canonical data | Runtime |
|--------|------|----------------|---------|
| **Write gate** (`gate.py`) | Filesystem write ACL | `lifecycle-model.yaml` → `write_policy` | `sdlc_gate_hook.py` |
| **Interaction gateway** (`gateways/`) | Shell deny, handoff, subagent order | `gateways/policy.yaml` | pre/post gateway hooks |

**Recommendation:** deprecate `gates/paths.yaml` as **generated view** from `write_policy`; keep `gateways/policy.yaml` as separate harness policy. Do **not** merge folders — merge **documentation** only.

---

## 6. Reduction targets (manifest lens)

| Delete / generate | Keep | Rationale |
|-------------------|------|-----------|
| Manual `gates/paths.yaml` | Generate via `sdlc_sync_model.py --write` | Drift eliminated |
| Manual `stages/lifecycle.yaml` | Generate from model + definitions objective | Studio/compiler compat |
| Duplicate `plane-*` skills | `board-*` only | RPG-12 incomplete |
| `scripts/optimization/analyzer.py` wrapper | `learning_loop.py analyze` | Single CLI |
| Second obs narrative in 5 docs | Point to `runtime/manifest.yaml` | One index |

**Do not delete:** `workflows/transitions.yaml` — skill/precondition overlay not in lifecycle-model graph.

---

## 7. KPI wiring (Studio dashboard)

From unified SQLite + JSONL:

- **Agentic Velocity** — cards Done / week from ledger + Plane
- **Self-Correction Ratio** — autofix cycles / qa runs from learning events
- **Governance Overhead** — `gateway_block` / total events from obs timeline

Studio `/studio/obs/metrics` exposes KPIs; manifest declares source paths.

---

## 8. Phase plan (Analysis A)

1. **P0** — `runtime/manifest.yaml` + restore `sdlc_obs` + Studio compiler → lifecycle-model
2. **P1** — Shim generation (`sdlc_sync_model --write`) + pipeline_metadata fix
3. **P2** — Wire learning hook → obs timeline correlation; orchestrator hints
4. **P3** — Slim L1 prose; registry points to lifecycle-model not shims

---

## 9. Risk

| Risk | Mitigation |
|------|------------|
| Studio compiler break | Keep generated shims until compiler tests green |
| Obs DB schema drift | Single `schema.sql`; Studio test_obs.py as contract |
| Manifest stale | Doctor check: `runtime/manifest.yaml` paths exist |
