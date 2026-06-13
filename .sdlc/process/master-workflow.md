# Master Workflow — SDLC AI-Native

> **Status:** APPROVED — P0 + P1 implemented  
> **Date:** 2026-05-27  
> **Authority:** prevails over ad hoc chat instructions (complements `change-lifecycle.md`)

---

## Documentation layers

| Layer | File | Audience | Content |
|-------|------|----------|---------|
| L0 — Entry | `AGENTS.md` (root) | Agent (alwaysApply) | One-page decision tree + entry commands |
| L1 — Index | `.sdlc/README.md` + `.sdlc/manifest/catalog.yaml` | Agent + human | Modular SDLC map, agents, skills, MCP catalog |
| L1 — Process | `.sdlc/process/master-workflow.md` | Agent + human | This document — full flow |
| L2 — Machine | `.sdlc/sdlc.yaml` + module YAMLs under `.sdlc/<module>/` | Scripts/hooks/CLI | States, gates, paths, transitions |
| L2 — Canonical model | `.sdlc/process/lifecycle-model.yaml` | Gate, validate, Doctor | Single stage graph + write_policy + operational_map |

Operational steps map to lifecycle stages in `lifecycle-model.yaml` (`operational_map` section). Legacy `gates/paths.yaml` and `workflows/transitions.yaml` are shims during migration.

### Operational map (canonical)

| Step | Lifecycle stages | Agent | Gate stage |
|------|------------------|-------|------------|
| intent_routing | — | intent-analyst | — |
| plan | ticket, requirements | planner | planning |
| architecture | architecture | architect | architecture |
| implement | implementation, autofix | implementer | implementation |
| validate | validation | qa | validation |
| review | review | reviewer | review |
| deploy | deployment, observability | devops | — |

Full machine-readable map: `.sdlc/process/lifecycle-model.yaml` → `operational_map`.

---

## Agreed principles

1. **Always automatic** — any message in `sdlc-ai` goes through Orchestrator first.
2. **Autonomy ≠ bypass** — *"no interruptions"* = autonomous decisions **within scope**, full pipeline, zero gate skips.
3. **Zero human clicks** — autonomous merge always (green CI + Reviewer APPROVE).
4. **Human escalation** — AutoFixer tries to resolve → reports blocker → if exhausted after defined cycles, **stop and ask human**.
5. **Dual state** — Plane = source of truth; `session-gate.json` = mechanical cache for hooks.
6. **Plan artifacts** — live **only on Plane** (HTML); local `specs/` forbidden.
7. **Self-management** — Orchestrator detects structural gap → auto-create `SDLC_META` card.

---

## Step 0 — Entry (every session)

```
User sends message
    → Orchestrator Principal (chat agent)
    → Task(Intent Analyst)  [always, except continuation with gate already open]
    → Markdown handoff + session-gate.json (+ Plane if product work)
```

### Urgency policy

| User input | Behavior |
|------------|----------|
| "no interruptions", "urgent", "just do it" | Full pipeline; autonomous scope decisions; **do not** ask human |
| Out-of-scope request | Orchestrator records in handoff; **do not** expand scope |
| Unrecoverable blocker | AutoFixer → report → **stop and ask human** |

---

## Step 1 — Intent Analyst

**File:** `.cursor/agents/intent-analyst.md`
**Skill:** `.cursor/skills/intent-classification/SKILL.md`

### Responsibility

Interpret any input and return to Orchestrator:

Markdown handoff in `.sdlc/memory/orchestrator-handoff.md`:

| Section | Required fields |
|---------|-----------------|
| Routing | **Next agent**, **Stage complete**, **Previous agent** |
| Classification | **Intent**, **Confidence**, **Requires Plane**, **Requires branch** |
| Session | **Card**, **Branch**, **Stage** when known |
| Scope | Human-readable rationale and boundaries |

### Routing

| Intent | Plane | Branch | Next agent |
|--------|-------|--------|------------|
| READONLY | No | No | none (Orchestrator responds) |
| Pure QUESTION | No | No | none |
| SDLC_META | Yes | `sdlc/` | per scope |
| DOCS_ONLY | Yes | `docs/` | Planner (light) |
| GREENFIELD | Yes (epic) | `feature/` | Planner |
| FEATURE | Yes | `feature/` | Planner |
| BUGFIX | Yes | `bugfix/` | Planner |
| HOTFIX | Yes | `hotfix/` | Planner |
| INFRA | Yes | `infra/` | Architect/DevOps |

### Evidence (product intent)

- Markdown handoff → `.sdlc/memory/orchestrator-handoff.md` (latest)
- `session-gate.json` → `{ intent, card, stage, gate_status }`
- Plane → HTML classification comment on card (when `requires_plane=true`)

### Evidence (READONLY)

- Minimal Markdown handoff + `session-gate.json`
- **No Plane card**

---

## Step 2 — GREENFIELD detection

**Combined signal (either or both):**

1. **User words:** "from scratch", "greenfield", "do not reuse", "rethink", etc.
2. **Repo state:** `app/backend` and `app/frontend` are placeholders (README only)

**Discovery hook (Spec Kit pattern):**

Before Plan/Arch, read-only script/hook:

- Lists legacy docs (`docs/product/*`, old API contracts)
- Reports to Orchestrator: `legacy_docs[]`
- Orchestrator decides ignore vs reference (GREENFIELD → ignore by default)

---

## Step 3 — Plane structure (granular — mandatory)

> **Forbidden:** single `[AI][FULLSTACK]` card for GREENFIELD/FEATURE.

### Epic + children

| Role | Title | workflow start |
|------|-------|----------------|
| Epic | `[AI][EPIC] …` | **Never** — tracking only |
| Backend child | `[AI][BACKEND] …` | Yes — one branch per child |
| Frontend child | `[AI][FRONTEND] …` | Yes |
| Infra/shared child | `[AI][INFRA]` or `[AI][SHARED]` | Yes |

Minimums: GREENFIELD ≥3 children · FEATURE ≥2 children

Config: `.sdlc/workboard/granularity.yaml`
Validation: `plane_card.py validate-all --card RPG-N`

### Plan creation gate

**Skill:** `.cursor/skills/board-task-creation/SKILL.md`
**Script:** `python .sdlc/scripts/plane_card.py validate-plan --card RPG-N`

Incomplete plan **blocks** Ticket → Requirements transition:

- [ ] Measurable acceptance criteria (≥3)
- [ ] Non-goals (≥2)
- [ ] Risks + mitigation (≥2)
- [ ] Explicit scope (impacted areas)
- [ ] TipTap HTML format (`board-formatting` skill)

---

## Step 4 — Pipeline (Orchestrator = Task coordinator)

> **Rule:** Orchestrator **never** edits `app/`, **never** commits, **never** runs lint/test.  
> Skill: `.cursor/skills/subagent-delegation/SKILL.md`

```
Task(Intent Analyst)
→ Task(Planner)     epic + child Plane cards + validate-all
→ workflow discover
→ Task(Architect)
→ FOR EACH child card:
      workflow start (child only)
      Task(Implementer)  → autonomous commits on branch
      Task(QA)           → qa-minimum-checklist
      Task(AutoFixer)    → max 2 cycles if QA fail
      Task(Reviewer)
      Task(DevOps)       → push + PR
      workflow finish
→ epic Done
```

### AutoFixer loop

```
QA FAIL → Task(AutoFixer) → re-Task(QA)
         ↳ max 2 cycles
         ↳ if still FAIL → Plane comment + STOP + ask human
```

### Merge

- **Always autonomous:** `auto_merge_pr.py --pr N --card RPG-N --plane-comment`
- Conditions: green CI + Reviewer APPROVE (no ESCALATE)

---

## Step 5 — Mechanical gate

### Files

| File | Function |
|------|----------|
| `.sdlc/gates/paths.yaml` | Configurable protected paths |
| `.sdlc/memory/session-gate.json` | Cache: `{ card, branch, stage, gate, opened_at }` |
| `.cursor/hooks/sdlc_gate_hook.py` | Cursor pre-write hook |
| `.sdlc/scripts/sdlc_gate.py` | open / close / status / validate |

### Model: stage + path gate

| Stage | Allowed paths (example) |
|-------|-------------------------|
| `planning` | `.sdlc/`, `.cursor/` |
| `architecture` | + Plane comments; no `app/` |
| `implementation` | `app/backend/`, `app/frontend/`, `app/shared/`, `pyproject.toml` |
| `sdlc_meta` | `.sdlc/`, `.cursor/`, `.github/` |

Gate opens via: `python .sdlc/dsl/cli.py workflow start --card RPG-N`

### Enforcement

- **Cursor pre-write hook** — blocks Write tool if path ∈ `gates/paths.yaml` and gate closed
- **On block:** Orchestrator **auto-corrects once** (runs missing step, e.g. `workflow start`) before reporting

---

## Step 6 — CLI meta-tool

```bash
python .sdlc/dsl/cli.py workflow classify   # Intent Analyst wrapper
python .sdlc/dsl/cli.py workflow plan       # validate-plan gate
python .sdlc/dsl/cli.py workflow discover   # legacy docs scan
python .sdlc/dsl/cli.py workflow arch       # arch gate check
python .sdlc/dsl/cli.py workflow start      # Plane in-progress + branch + open gate
python .sdlc/dsl/cli.py workflow implement  # gate check impl
python .sdlc/dsl/cli.py workflow validate   # QA gate prep
python .sdlc/dsl/cli.py workflow review     # review gate prep
python .sdlc/dsl/cli.py workflow finish     # auto_merge + close gate + Done
python .sdlc/dsl/cli.py workflow status     # session-gate + handoff
```

Makefile optional wrappers (`make workflow-start CARD=RPG-N`).

---

## Step 7 — Tracking (Plane timeline)

Each stage transition → **structured HTML comment** on Plane card:

| Event | Template |
|-------|----------|
| `intent_classified` | Intent + confidence + scope |
| `plan_validated` | AC count + validate-plan exit 0 |
| `gate_opened` | stage + branch + timestamp |
| `stage_complete` | agent + handoff summary |
| `gate_blocked` | path + attempted action + auto-fix result |
| `qa_pass` / `qa_fail` | summarized test output |
| `review_approve` / `review_escalate` | decision + risks |
| `merge_complete` | PR URL + CI run URL |
| `human_required` | blocker + AutoFixer attempts |

> **Note:** aggregate metrics (compliance rate) may be added later via obs DB — phase 2.

---

## Step 8 — SDLC self-management

When Orchestrator or Doctor detects:

- Missing referenced skill (e.g. `board-task-creation`)
- Missing referenced script (e.g. `sdlc_gate.py`)
- Missing referenced rule (e.g. `orchestrator.mdc`)
- Unregistered hook

**Autonomous action:**

1. Create Plane card `[AI][SDLC] Fix gap <description>` (SDLC_META)
2. Comment with evidence (grep, doctor output)
3. **Do not** implement product until P0 gap blocking gate is resolved

---

## AGENTS.md L0 — Decision tree (implementation summary)

```
MESSAGE RECEIVED
│
├─ session-gate.json has active card in impl?
│   └─ YES → continue current stage (do not re-classify)
│
└─ NO → Task(Intent Analyst)
         │
         ├─ READONLY → respond (no Plane)
         │
         └─ PRODUCT/META → Plane card
                │
                ├─ validate-plan OK?
                │   └─ NO → Task(Planner) + board-task-creation
                │
                ├─ arch gate OK? (product)
                │   └─ NO → Task(Architect)
                │
                ├─ workflow start (gate open)
                │
                ├─ Task(Implementer) — Orchestrator does NOT touch app/
                │
                ├─ Task(QA) → AutoFixer loop (max 2)
                │
                ├─ Task(Reviewer)
                │
                └─ workflow finish → Done

URGENCY / "NO INTERRUPTIONS" → same tree, zero questions, zero skip
BLOCKER → AutoFixer → report → human if exhausted
```

---

## Implementation map

### P0 — Done (2026-05-27)

Gate, hook, CLI, anti-bypass rules, intent analyst, board-task-creation, validate-plan.

### P1 — Done (2026-05-27)

Granularity, delegation loop, discovery hook, QA checklist, epic start block.

### P2 — Metrics

Obs DB events (compliance rate) — optional; Plane timeline first.

---

## References

- Workflow authority: `.sdlc/process/change-lifecycle.md`
