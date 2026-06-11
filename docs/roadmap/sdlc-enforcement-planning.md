# SDLC AI-Native — Enforcement & Structure Planning

> **Purpose:** Consolidated planning after deep audit (2026-06). Use after the current agent run finishes, before implementing hardening work.  
> **Companion:** [`sdlc-enforcement-roadmap.md`](sdlc-enforcement-roadmap.md) — phased delivery and milestones.  
> **Authority unchanged:** `.sdlc/process/change-lifecycle.md` prevails for git/Plane/merge; this doc plans *how* to make that enforceable and lean.

---

## 1. Goals

| Goal | Meaning |
|------|---------|
| **Deterministic** | Gates block by default; bypass requires explicit SDLC_META card + audit trail |
| **Lean** | One canonical machine model; no parallel stage lists |
| **Clear ownership** | Each module has one job; no overlap between `stages/`, `gates/`, `workflows/`, and prose workflow |
| **Verifiable** | CI + Doctor + `sdlc-validate` prove structure; handoff cross-checked against Plane/git/CI |
| **AI-native SaaS-ready** | Orchestrator coordinates; subagents implement; Plane = evidence; repo = mechanics only |

---

## 2. Current State (Honest)

### What works

- L0 entry (`AGENTS.md`), L1 process (`master-workflow.md`, `change-lifecycle.md`), L2 index (`.sdlc/sdlc.yaml`).
- Plane + GitHub integration scripts (`plane_card.py`, `plane_state.py`, `auto_merge_pr.py`).
- Session gate cache (`session-gate.json`) + path gate (`gate.py`, `sdlc_gate_hook.py`).
- Gateway policy (`gateways/policy.yaml`) + handoff contract.
- Doctor structural checks + DSL `validate` (semantic cross-refs).
- Subagent pipeline documented; recent delivery (e.g. INVES-70) completed end-to-end.

### What is weak (audit summary)

| Area | Problem |
|------|---------|
| Hooks | All `failClosed: false`; missing PyYAML/policy → allow |
| Path gate | Only 4 protected prefixes; `Write` tool only; no transition order enforcement |
| CI | Doctor + gitleaks only; no pytest, no `sdlc-validate`, no lint |
| Merge | No GitHub review APPROVE check; CI = latest run on branch, not required checks @ HEAD |
| Manifest | 4 agent rosters (pipeline, gateway, doctor, catalog); validator sees 7 agents only |
| Handoff | Post-gateway trusts agent-written Markdown; no evidence cross-check |
| Intent | Duplicate: `workflow classify` keywords vs `intent-analyst` agent |
| Evidence | Rule: Plane only; tooling still uses `templates/plane/evidence-{CARD}.json` |
| Stages vs workflow | 10 lifecycle stages vs 8-step operational pipeline; no mapping table |
| Transitions | `transitions.yaml` preconditions are descriptive, never executed |

---

## 3. Root Cause: Duplication & Confusion

Today three parallel notions describe “where we are in SDLC”:

```text
┌─────────────────────────────────────────────────────────────────┐
│  master-workflow.md     → 8 operational steps (agents/tasks)   │
│  stages/lifecycle.yaml  → 10 ordered stage ids                   │
│  gates/paths.yaml       → 6 mechanical stage keys (≠ lifecycle)│
│  workflows/transitions  → 7 edges (partial graph)              │
│  gateways/policy.yaml   → 9 agents + handoff routing           │
│  pipeline/agents.yaml   → 7 agents + stage bindings              │
└─────────────────────────────────────────────────────────────────┘
```

**Symptoms:** Planner talks “requirements”; gate opens `implementation`; CLI has no `ticket` stage; `planning`/`architecture` exist only in `paths.yaml`, not in `lifecycle.yaml`.

**Target principle:** **One lifecycle model drives everything else.** Prose and hooks are views on that model, not alternate definitions.

---

## 4. Target Architecture (Lean, Single Source)

### 4.1 Layer model

| Layer | Location | Owns | Does not own |
|-------|----------|------|----------------|
| **L0 Entry** | `AGENTS.md` | Decision tree, delegation matrix | Stage definitions |
| **L1 Process prose** | `.sdlc/process/change-lifecycle.md` | Gitflow, Plane states, merge policy | Path allowlists |
| **L1 Process prose** | `.sdlc/process/master-workflow.md` | Orchestrator pipeline narrative | Duplicate stage list — **becomes index + mapping table only** |
| **L2 Canonical model** | `.sdlc/process/lifecycle-model.yaml` (**new, merge target**) | Stage ids, order, mode, agent, skill, transitions, preconditions, write policy | Runtime state |
| **L2 Runtime** | `.sdlc/memory/session-gate.json` | Current card, branch, stage, gate open/closed | History / evidence |
| **L2 Runtime** | `.sdlc/memory/orchestrator-handoff.md` | Routing cache for hooks | Plane HTML |
| **L2 Enforcement** | `.cursor/hooks/*` + `.sdlc/gateways/policy.yaml` | Interaction harness (shell deny, subagent route, handoff shape) | Business AC text |
| **L2 Validation** | `.sdlc/doctor/checks.yaml` + `dsl/validator.py` | Structural + semantic drift vs model | Product tests |
| **L2 Catalog** | `.sdlc/manifest/catalog.yaml` | **Single** agent/skill/MCP roster | Stage order |
| **L3 Evidence** | Plane (project `investiments`) | AC, QA, PR, Done | Local tickets / `specs/` |

### 4.2 Consolidation: what merges into `lifecycle-model.yaml`

Proposed single file (sections), generated views optional later:

```yaml
# lifecycle-model.yaml (conceptual)
version: "1.0"
stages:          # from lifecycle.yaml + definitions.yaml (slim: id, order, mode, agent, outputs, evidence)
transitions:     # from workflows/transitions.yaml (+ missing ticket→requirements)
write_policy:    # from gates/paths.yaml (stage → allowed_prefixes, protected_prefixes)
operational_map: # master-workflow steps → stage ids (explicit table)
```

**Deprecate (after migration):**

- Standalone duplication in `stages/definitions.yaml` long form → keep only fields needed at runtime; narrative moves to `.sdlc/process/README.md` snippets.
- `workflows/transitions.yaml` → section inside model (or thin re-export for backward compat one release).
- `gates/paths.yaml` → section `write_policy` in model (or symlink/generate step in Doctor).

**Keep separate (clear responsibility):**

| Module | Responsibility |
|--------|----------------|
| `gateways/policy.yaml` | Shell deny patterns, handoff required fields, agent_order for hooks |
| `gateways/` hooks lib | Parse handoff, deny/allow — **reads** lifecycle-model for stage validity |
| `doctor/checks.yaml` | Files exist, forbidden paths, **drift vs lifecycle-model + catalog** |
| `manifest/catalog.yaml` | Agents, skills, MCP, conventions — **source of roster** |
| `pipeline/agents.yaml` | **Generated from catalog** or deleted; validator loads catalog only |
| `workboard/granularity.yaml` | Epic/child rules only |

### 4.3 Operational map (fixes master-workflow vs stages)

| Lifecycle stage (`id`) | Operational step (master-workflow) | Agent | Gate stage key | CLI touchpoint |
|------------------------|-----------------------------------|-------|----------------|----------------|
| `ticket` | (inside Planner) | planner | `planning` | `workflow plan`, Plane create |
| `requirements` | Planner | planner | `planning` | `validate-plan` |
| `architecture` | Architect | architect | `architecture` | `workflow arch` |
| `implementation` | Implementer | implementer | `implementation` | `workflow start`, `implement` |
| `validation` | QA | qa | `validation` | `workflow validate` |
| `review` | Reviewer | reviewer | `review` | `workflow review` |
| `deployment` | DevOps (PR/merge) | devops | — | `workflow finish`, `auto_merge_pr` |
| `observability` | DevOps / Observer | devops / observer | — | post-merge checklist |
| `incident` | (triggered) | implementer | — | hotfix branch |
| `autofix` | AutoFixer loop | auto-fixer | `implementation` | max 2 cycles |

**Intent Analyst** is pre-lifecycle routing (`READONLY` | product | `SDLC_META`), not stage 0.

---

## 5. Gap Remediation Plan (Technical)

### P0 — Fail-closed enforcement

1. Set `failClosed: true` on `preToolUse` (Write), `beforeShellExecution`, `subagentStart`, `subagentStop` for gate/gateway hooks.
2. Hooks: if policy/gate module fails to load → **deny** with fix instruction (not allow).
3. Remove or gate `--force`, `--skip-plane`, `--skip-validate`, `--skip-ci-wait` behind env `SDLC_BREAK_GLASS=1` + Plane SDLC_META comment.
4. Epic check on `workflow start`: fail closed on Plane API error (no silent WARN + open gate).

### P0 — CI truth

1. Add job: `pytest .sdlc/dsl` + `.cursor/hooks/test_sdlc_gateway.py`.
2. Add job: `make sdlc-validate`.
3. Add job: `ruff` (or minimal lint) when touching `.sdlc/` / `app/`.
4. `auto_merge_pr.py`: required status checks for PR HEAD SHA; require review state APPROVE (or bot policy equivalent).

### P1 — Single roster & drift detection

1. `catalog.yaml` = canonical agents; generate `pipeline/agents.yaml` or remove and teach loader to read catalog pipeline section.
2. `gateways/policy.valid_agents` = derived from catalog (script check in Doctor).
3. Doctor: verify every `hooks.json` command path exists; catalog path exists; lifecycle-model stage ids referenced by gate hook.

### P1 — Evidence & handoff integrity

1. Post-gateway: before accepting `Stage complete: yes`, verify (script): Plane card In Progress/Done rules, branch exists if required, last test command exit 0 if stage ≥ validation.
2. Evidence JSON: only under `.sdlc/memory/.evidence-{CARD}.json` (gitignored); `make plane-evidence` reads ephemeral; **no** committed `templates/plane/evidence-INVES-*.json`.
3. One intent path: deprecate `workflow classify` keyword heuristic → wrapper calls intent-analyst contract or shared `intent_rules.yaml`.

### P1 — Transition enforcement

1. `workflow start --stage X` checks `lifecycle-model.transitions`: allowed only if previous stage evidence satisfied (or explicit `SDLC_META` override).
2. `gate.py` uses same stage ids as lifecycle (align `planning` → `ticket`/`requirements` or document alias map in model).

### P2 — Lean docs & generator (optional)

1. Slim `master-workflow.md` to mapping table + pipeline diagram; link to `lifecycle-model.yaml`.
2. `make sdlc-sync-model` — validates and optionally emits backward-compat shims for one release.
3. Metrics (P2 from process doc): obs DB compliance rate — after enforcement stable.

---

## 6. Module Responsibility Matrix (After Consolidation)

| Path | Single responsibility |
|------|------------------------|
| `.sdlc/process/change-lifecycle.md` | Git/Plane/PR/merge law |
| `.sdlc/process/master-workflow.md` | Orchestrator choreography + operational map (thin) |
| `.sdlc/process/lifecycle-model.yaml` | **Canonical** stages, transitions, write policy |
| `.sdlc/manifest/catalog.yaml` | Agents, skills, MCP, prohibitions |
| `.sdlc/gateways/policy.yaml` | Handoff shape, shell deny, agent_order |
| `.sdlc/gateways/README.md` | How pre/post hooks interact with model |
| `.sdlc/doctor/checks.yaml` | Structural inventory + drift rules |
| `.sdlc/dsl/gate.py` | Runtime write check (reads model) |
| `.sdlc/dsl/workflow.py` | CLI commands (reads model) |
| `.sdlc/dsl/validator.py` | Semantic validation (reads model + catalog) |
| `.sdlc/memory/*` | Session cache only (handoff, gate, ephemeral evidence) |
| `.cursor/hooks/*` | Cursor integration enforcement |
| `docs/roadmap/sdlc-enforcement-*.md` | Human planning/roadmap (this folder) |

**Eliminate confusion rule:** If a stage id appears in two YAML files without generation, Doctor **FAIL**.

---

## 7. Non-Goals (Stay Lean)

- Do not add `specs/` or local ticket stores.
- Do not add a second orchestrator ruleset in `docs/`.
- Do not expand to 16 first-class pipeline agents in runtime — catalog lists support agents; **pipeline** stays ~8 active roles.
- Do not duplicate Plane HTML in repo beyond handoff cache.
- Do not build full BPM engine — preconditions are scriptable checks, not a workflow server.

---

## 8. Preconditions for Implementation

Before starting P0 work on `develop`:

1. Current agent execution branch merged or rebased; no conflicting `.sdlc/` refactor in flight.
2. `make sdlc-doctor` green on baseline.
3. Plane epic for hardening (suggested: `[AI][EPIC] SDLC deterministic enforcement`) with children: INFRA (CI/hooks), SDLC (model merge), SDLC (merge/review gates).
4. Break-glass policy documented on Plane if `--force` retained for emergencies.

---

## 9. Success Criteria (Planning Complete When)

- [x] `lifecycle-model.yaml` exists; Doctor fails on stage id mismatch across repo.
- [x] Hooks fail-closed; manual test: write to `app/backend/` with gate closed → deny.
- [x] CI runs pytest + validate + doctor + ruff on every PR.
- [x] `auto_merge_pr` refuses merge without green required checks + review.
- [x] `master-workflow.md` contains operational map table; legacy shards deprecated.
- [x] Evidence files not committed under `templates/plane/`.
- [x] Single agent roster validated by `sdlc-validate` / Doctor roster sync.

---

*Last updated: 2026-06-03 — reflects repository audit and orchestrator conversation.*
