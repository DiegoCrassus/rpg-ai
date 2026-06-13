# Harness v7 — Change plan (executed)

> **Authority:** reconciles Analysis A + B + [analysis-v7-comparison.md](analysis-v7-comparison.md)
> **Epic label:** `[AI][EPIC] Harness v7 — Manifest observability + structure slim`
> **Status:** APPLIED (2026-06-13) — P0+P1 complete; P2/P3 deferred

---

## 1. Goal

1. Studio **100% manifest-aligned** observability (reads `runtime/manifest.yaml`, not ad-hoc paths).
2. Restore **working** `app/infra/sdlc_obs` (Studio timeline, hooks, Makefile, CI).
3. **Single lifecycle SoT** — compiler + metadata read `lifecycle-model.yaml`.
4. **Eliminate drift** — generated shims, L1 doc fixes, delete duplicate skills.
5. **Clarify gate vs gateways** — docs only; no erroneous merge.

---

## 2. Architecture (target)

```text
.sdlc/process/lifecycle-model.yaml     ← graph + write_policy + operational_map
.sdlc/workflows/transitions.yaml       ← overlay (skills, preconditions)
.sdlc/runtime/manifest.yaml            ← observability path index (NEW)
.sdlc/manifest/catalog.yaml            ← agent/skill phonebook
.sdlc/gateways/policy.yaml             ← interaction harness
.sdlc/gates/paths.yaml                 ← GENERATED write_policy view
.sdlc/stages/lifecycle.yaml            ← GENERATED stage list view

app/infra/sdlc_obs/                    ← SQLite timeline (Studio primary obs)
  └── data/sdlc_obs.db

studio/                                ← reads manifest + lifecycle-model
```

---

## 3. Execution checklist

### Phase P0 — Manifest observability (this pass)

- [x] `.sdlc/process/analysis-v7-a-manifest-studio.md`
- [x] `.sdlc/process/analysis-v7-b-structure-drift.md`
- [x] `.sdlc/process/analysis-v7-comparison.md`
- [x] `.sdlc/process/harness-v7-change-plan.md`
- [x] `.sdlc/runtime/manifest.yaml` + README
- [x] `app/infra/sdlc_obs/` package (store, collector, db, hooks, server, auditor)
- [x] `sdlc.yaml` → `core.runtime` + `contract.modules.runtime`
- [x] `catalog.yaml` reading_order includes runtime manifest
- [x] Fix `change-lifecycle.md` investiments → RPG
- [x] Delete duplicate plane/github skills (already absent)

### Phase P1 — SoT migration (this pass)

- [x] `studio/engine/compiler_core.py` → lifecycle-model primary
- [x] `studio/.../pipeline_metadata.py` → lifecycle-model write_policy
- [x] `sdlc_sync_model.py` → `--write` generates shims
- [x] `gateways/README.md` + `gates/README.md` → point to lifecycle-model
- [x] Registry: add `sdlc.process.lifecycle_model` + `sdlc.runtime.manifest`

### Phase P2 — Epic RPG-17 (open on Plane)

- [ ] Merge `pipeline/agents.yaml` into `catalog.yaml` — **RPG-20**
- [ ] Orchestrator `learning_loop hints` before Task spawn — **RPG-19**
- [x] Warm learning loop (QA → qa-evidence → reward) — **RPG-18**
- [ ] Slim `master-workflow.md` — **RPG-21**

### Phase P3 — Deferred

- [ ] Merge `gates/README` into `gateways/README`
- [ ] Support agents → skills-only invocation

---

## 4. gate vs gateways (frozen decision)

| Name | Path | Purpose |
|------|------|---------|
| **Write gate** | `lifecycle-model.yaml` → `write_policy` | Protect `app/`, enforce stage ACL |
| **Gateway policy** | `gateways/policy.yaml` | Shell deny, handoff, subagent order, Studio proposals |

Do not collapse into one YAML.

---

## 5. Studio manifest contract

`runtime/manifest.yaml` sections:

| Key | Path | Consumer |
|-----|------|----------|
| `obs.sqlite` | `app/infra/sdlc_obs/data/sdlc_obs.db` | Studio ObsStore, hooks |
| `ledger.jsonl` | `.sdlc/manifest/executions.jsonl` | Session bootstrap |
| `learning.events` | `.sdlc/learning/data/events.jsonl` | Policy optimizer |
| `learning.policy` | `.sdlc/learning/policy_memory.yaml` | Orchestrator hints |
| `session.gate` | `.sdlc/memory/session-gate.json` | Event correlation |
| `session.handoff` | `.sdlc/memory/orchestrator-handoff.md` | Event bus watcher |
| `lifecycle.canonical` | `.sdlc/process/lifecycle-model.yaml` | Compiler, gate.py |

---

## 6. Verification

```bash
make sdlc-doctor
make sdlc-sync-model
python -m pytest studio/engine/tests/test_compiler_core.py studio/backend/tests/test_obs.py -q
python -m pytest .sdlc/dsl/test_learning_loop.py .sdlc/dsl/test_execution_ledger.py -q
make obs-init
```

---

## 7. Rollback

- Restore shims from git if generation fails
- `core.gates.enforcement: strict` unchanged
- Studio compiler falls back to shims if lifecycle-model missing (compiler guard)

---

## 8. References

- Harness v6: [harness-v6-plan.md](harness-v6-plan.md)
- Communication: [communication-policy.md](communication-policy.md)
- Studio platform: `docs/architecture/studio-service-platform.md`
