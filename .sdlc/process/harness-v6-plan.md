# Harness v6 — Master Implementation Plan

> **Status:** COMPLETE (implementation landed — merge + Plane Done pending DevOps)  
> **Authority:** `.sdlc/process/change-lifecycle.md` for git/Plane; this doc for harness + learning architecture  
> **Companion:** [`communication-policy.md`](communication-policy.md)

---

## 1. Vision

**Five layers** — one mechanical truth, one learning loop, no LLM training:

| Layer | Name | SoT | Output |
|-------|------|-----|--------|
| **L1** | Harness | `lifecycle-model.yaml` + `gateways/policy.yaml` | Gates, routing, deny |
| **L2** | Stage ledger | `manifest/executions.jsonl` | Stage/gateway events |
| **L3** | Learning loop | `.sdlc/learning/*` | Task events, reward, lessons |
| **L4** | Optimization | `policy_memory.yaml` + `policy_optimizer.py` | Hints, proposals (observe) |
| **L5** | Governance | Plane + Studio dry-run | Applied changes |

**Communication law:** inter-agent = **caveman** (≤45 lines). Human = plans, Plane, user chat.

**Learning paradigm:** operational reinforcement — deterministic reward from verifiable outcomes (tests, lint, tokens, rework, human verdict). **Not** neural RL. Extensible to contextual bandits later.

---

## 2. Plane epic RPG-7 — child cards

| Card | Title | Branch slug | Phase |
|------|-------|-------------|-------|
| **RPG-7** | `[AI][EPIC] Harness v6 — SDLC learning loop` | — | Epic |
| **RPG-8** | Learning loop — schemas and reward engine | `learning-reward-engine` | A |
| **RPG-9** | Learning loop — event store and hook integration | `learning-event-store` | B–C |
| **RPG-10** | Learning loop — policy memory and optimizer | `learning-policy-optimizer` | D–E |
| **RPG-11** | Harness strict gates and lifecycle merge | `harness-strict-gates` | 1 + 3 |
| **RPG-12** | SDLC structure cleanup | `sdlc-structure-cleanup` | Cleanup |

Create/update: `python .sdlc/scripts/plane_create_harness_v6_epic.py`

---

## 3. Learning loop architecture

### 3.1 Two event stores (complementary)

| Store | Path | Granularity | Purpose |
|-------|------|-------------|---------|
| **Task events** | `.sdlc/learning/data/events.jsonl` | 1 per agent run | Reward, cost, tests, lessons |
| **Stage ledger** | `.sdlc/manifest/executions.jsonl` | 1 per subagentStop | Gateway, stage trace |

Task events **feed** policy memory. Stage ledger **feeds** card snapshots (`execution-RPG-N.json`).

### 3.2 Modules (`.sdlc/learning/`)

| Module | Role |
|--------|------|
| `schemas.py` | `SDLCRunEvent`, `TaskType`, `TaskOutcome` |
| `reward_engine.py` | Deterministic reward **[-1, 1]** |
| `event_store.py` | Append task events, QA metrics ingest |
| `policy_memory.py` | YAML rules + hints from history |
| `policy_optimizer.py` | Observe-mode suggestions (no auto-apply) |
| `test_learning.py` | pytest |

CLI: `.sdlc/scripts/learning_loop.py` — `record-session`, `analyze`, `policy-update`, `hints`

### 3.3 Reward rules (v1)

| Condition | Effect |
|-----------|--------|
| Security fail | reward = **-1** |
| Rollback | reward = **-1** |
| Tests fail | reward ≤ **0** |
| Lint/type fail | reward capped low |
| Gateway block | -0.3 |
| Rework (autofix cycles) | -0.15 each (cap) |
| High tokens | -0.1 to -0.25 |
| Human APPROVE | +0.15 |
| Human ESCALATE | -0.3 |
| All green, low cost | reward ≥ **0.8** |

Stage ledger may still use simplified 0–1 rollup; task reward is authoritative.

### 3.4 Policy memory (examples)

Stored in `.sdlc/learning/policy_memory.yaml`:

- Small Python bugfix → fast model, reduced context
- Auth scope → security-scanner + reviewer
- Large feature → planner + architect before implementer
- Low historical reward cluster → detailed prompt + human review

### 3.5 Policy optimizer (observe mode)

`core.optimization.mode: observe` — reports patterns, **does not** write skills/rules automatically.

Phase 6: proposals → SDLC_META card → Studio dry-run → apply.

### 3.6 Integration hooks

| Event | Action |
|-------|--------|
| `subagentStop` | post-gateway → stage ledger; learning hook → task event |
| `workflow finish` | snapshot + policy_memory update |
| Orchestrator spawn | read `learning_loop.py hints` (future: mandatory) |

---

## 4. Phase breakdown

### Phase 0 — Baseline ✅

| ID | Deliverable | Status |
|----|-------------|--------|
| 0.1 | harness-v6-plan.md | Done |
| 0.2 | communication-policy.md + rule 060 | Done |
| 0.3 | orchestrator-handoff.md | Done |
| 0.4 | Plane epic RPG-7 + children 8–12 | Done |

### Phase 2 — Stage ledger ✅

| ID | Deliverable | Status |
|----|-------------|--------|
| 2.1–2.8 | execution_ledger.py, hooks, Makefile | Done |

### Phase A — Learning schemas + reward ✅

| ID | Deliverable | Status |
|----|-------------|--------|
| A.1 | schemas.py, reward_engine.py | Done (RPG-8) |
| A.2 | test_learning.py | Done |

### Phase B–C — Event store + hooks ✅

| ID | Deliverable | Status |
|----|-------------|--------|
| B.1 | event_store.py | Done (RPG-9) |
| C.1 | sdlc_learning_hook.py | Done |
| C.2 | learning_loop.py CLI | Done |

### Phase D–E — Policy memory + optimizer ✅

| ID | Deliverable | Status |
|----|-------------|--------|
| D.1 | policy_memory.py | Done (RPG-10) |
| E.1 | policy_optimizer.py | Done |
| E.2 | workflow finish → policy-update | Done |

### Phase 1 — Harness strict (RPG-11)

| ID | Deliverable | Status |
|----|-------------|--------|
| 1.1 | `core.gates.enforcement: strict` | Done |
| 1.2 | Gateway routing strict | Done (same flag) |
| 1.3 | failClosed verified | Done (hooks.json) |

### Phase 3 — Lifecycle merge (RPG-11)

| ID | Deliverable | Status |
|----|-------------|--------|
| 3.1 | Remove shims after loader-only model | Deferred — shims still referenced by Studio/registry drift checks |
| 3.2 | Single roster in catalog.yaml | Partial — pipeline/agents.yaml retained |
| 3.3 | Slim master-workflow.md | Deferred |

### Phase 5 — Optimization observe ✅

| ID | Deliverable | Status |
|----|-------------|--------|
| 5.1 | procedures.yaml seed | Done |
| 5.2 | analyzer + policy_optimizer | Done |
| 5.3 | core.optimization.mode observe | Done |

### Phase 6 — Optimization propose (backlog)

Proposal YAML → Studio dry-run → SDLC_META apply.

### Phase Cleanup — SDLC only (RPG-12)

**Scope:** `.sdlc/`, `.cursor/`, `Makefile`, `docs/` SDLC refs — **exclude** `studio/`, `app/`.

| ID | Action | Status |
|----|--------|--------|
| CL.1 | Delete `plane-*` / `github-sdlc` skill stubs; refs → `board-*` | Done |
| CL.2 | Delete legacy `memory/rpg-*-evidence.json` | Done |
| CL.3 | Fix investiments/sdlc-ai drift in L1 docs | Done (change-lifecycle, master-workflow, integrations) |
| CL.4 | Doctor: `board-formatting` not `plane-formatting` | Done |
| CL.5 | Remove dead Makefile targets (`sdlc-session-status` dup) | Deferred |
| CL.6 | Remove orphan `test_board_connection.py` | Done |

**Not in cleanup:** `app/infra/sdlc_obs/` (app scope — separate INFRA card later).

---

## 5. Evidence policy

| Class | Path | Git | Role |
|-------|------|-----|------|
| Task events | `.sdlc/learning/data/events.jsonl` | Yes (pruned) | Learning input |
| Stage ledger | `.sdlc/manifest/executions.jsonl` | Yes (pruned) | Stage trace |
| Policy memory | `.sdlc/learning/policy_memory.yaml` | Yes | Strategy hints |
| Snapshot | `.sdlc/memory/execution-RPG-N.json` | Yes | Card rollup |
| QA ephemeral | `.sdlc/memory/.qa-evidence-RPG-N.json` | No | Verify |
| Done official | Plane HTML | Plane | SoT |

Legacy `rpg-N-evidence.json` → **delete** (RPG-12).

---

## 6. Commands

```bash
# Stage ledger
make execution-ledger-status
make execution-ledger-tail N=20

# Learning loop
python .sdlc/scripts/learning_loop.py status
python .sdlc/scripts/learning_loop.py tail -n 20
python .sdlc/scripts/learning_loop.py analyze --last 100
python .sdlc/scripts/learning_loop.py policy-update --card RPG-N
python .sdlc/scripts/learning_loop.py hints --task-type feature --stage implementation --agent implementer

# Optimization (delegates to learning)
make execution-analyze

# Gates
python .sdlc/dsl/cli.py workflow gates strict

# Validate
make sdlc-doctor
python -m pytest .sdlc/learning/test_learning.py .sdlc/dsl/test_execution_ledger.py -q
```

---

## 7. KPIs (90 days)

| Metric | Target |
|--------|--------|
| Task event coverage | 100% subagentStop when gate open |
| Avg task reward (rolling 50) | ≥ 0.7 |
| Gateway blocks per card | < 1 avg |
| Policy rules with evidence_count ≥ 2 | ≥ 5 |
| Doctor drift FAIL | 0 |

---

## 8. Risks

| Risk | Mitigation |
|------|------------|
| Duplicate stores | Task vs stage roles documented §3.1 |
| Strict gates block work | `workflow start --stage sdlc_meta` for `.sdlc/` |
| Over-proposing | observe mode; min_runs_before_propose: 5 |
| sdlc_obs missing | Learning loop self-contained; obs = future INFRA |

---

## 9. Definition of Done (epic RPG-7)

- [x] Learning loop code + hooks + CLI
- [x] Learning pytest + execution_ledger pytest green (11 tests)
- [x] `make sdlc-doctor` exit 0
- [x] Gates strict enabled
- [x] SDLC cleanup (stubs, rpg-evidence, doc drift)
- [ ] All children RPG-8..RPG-12 marked Done on Plane after merge
- [ ] PR merged to develop
