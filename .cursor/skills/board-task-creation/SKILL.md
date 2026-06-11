# Skill: Plane Task Creation

> **Authority:** `.sdlc/process/master-workflow.md` · `.sdlc/workboard/granularity.yaml`

## Purpose

Create **epic + granular child cards** in Plane. **Never** a single monolithic `[AI][FULLSTACK]` card for greenfield or multi-layer features.

## When to use

- After Intent Analyst routes to Planner (`GREENFIELD`, `FEATURE`)
- Before `validate-all` and `workflow start` on **child** cards

## Mandatory structure (GREENFIELD / FEATURE)

### 1. Epic card `[AI][EPIC]`

- Title: `[AI][EPIC] <product name> — delivery epic`
- State: **Todo**
- Description: full plan (Story, Scope, Non-Goals, Risks, AC at epic level)
- **Task Breakdown** lists every child with future `RPG-N` and branch slug:

```
Child cards (create in Plane with parent = epic):
- RPG-26: [AI][BACKEND] Market API + providers mock/live
- RPG-27: [AI][FRONTEND] Dashboard + charts + watchlist
- RPG-28: [AI][INFRA] Docker compose + Makefile targets
```

### 2. Child cards (minimum)

| Intent | Min children | Required types |
|--------|--------------|----------------|
| GREENFIELD | 3 | BACKEND + FRONTEND + (INFRA or SHARED) |
| FEATURE | 2 | layers touched by scope |

Each child:

- Title: `[AI][BACKEND|FRONTEND|INFRA|SHARED|DOCS] …` — **never FULLSTACK alone**
- Parent: link to epic in Plane
- Own AC (≥3), scope, DoD
- State: **Todo** until `workflow start` on that child

### 3. Validation (blocking)

```bash
python3 .sdlc/scripts/discovery_hook.py
python3 .sdlc/scripts/plane_card.py validate-all --card RPG-N   # epic
python3 .sdlc/dsl/cli.py workflow plan --card RPG-N
```

## Implementation cycle (per child)

Orchestrator runs **one child at a time** (or parallel Tasks if Architect approved split):

```
workflow start --card RPG-26 --slug backend-api --stage implementation
→ Task(Implementer) → commits autonomously
→ Task(QA) → lint/test
→ Task(Reviewer) → Task(DevOps) → workflow finish
→ child Done
```

Epic → **Done** only when **all** children Done.

## Single-card exceptions

Only for: `BUGFIX`, `HOTFIX`, `SDLC_META`, `DOCS_ONLY`, `INFRA` (single layer).

## Required plan sections (every card)

1. Story · 2. Scope · 3. Non-Goals (≥2) · 4. Assumptions · 5. Risks (≥2)
6. Impacted Areas · 7. AC (≥3) · 8. DoD · 9. Task Breakdown · 10. Architecture notes

## Prohibitions

- **Never** `[AI][FULLSTACK]` as sole card for greenfield
- **Never** `workflow start` on epic card
- **Never** one-line stubs · never skip `validate-all`
