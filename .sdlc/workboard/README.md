# Workboard module

> **Data:** [`granularity.yaml`](granularity.yaml) · **Provider:** Plane (board role) · **Scripts:** `.sdlc/scripts/plane_card.py`, `plane_state.py`, `board_client.py`

## Purpose

Rules for **board card granularity** — when an epic is required, minimum child cards, forbidden tags, and one-branch-per-child policy. Enforced by `validate-all` before `workflow start`.

## When to read

| Intent | Rule (from `granularity.yaml`) |
|--------|--------------------------------|
| **GREENFIELD** | Epic `[AI][EPIC]` + ≥3 children (BACKEND + FRONTEND + INFRA/SHARED) |
| **FEATURE** | Epic + ≥2 children covering touched layers |
| **BUGFIX / HOTFIX / SDLC_META** | Single card allowed |
| Any greenfield/feature | **`[AI][FULLSTACK]` alone is forbidden** |

## Key fields

| Field | Meaning |
|-------|---------|
| `requires_epic` | Intents that must have a parent epic |
| `min_child_cards` | GREENFIELD: 3, FEATURE: 2 |
| `greenfield_required_groups` | Must match BACKEND, FRONTEND, and one of INFRA/SHARED/SDLC |
| `one_branch_per_child` | Each child gets `feature/RPG-N-<slug>` |
| `child_title_pattern` | `[AI][TYPE] Short imperative title` |

## Board context (from `sdlc.yaml` core)

- Workspace: `RPG-AI`
- Project: `RPG`
- Card prefix: `RPG`

## Related modules

- [`../manifest/README.md`](../manifest/README.md) — Planner agent path
- [`../integrations/README.md`](../integrations/README.md) — `BOARD_API_KEY` / `PLANE_API_KEY`
- [`../memory/orchestrator-handoff.md`](../memory/orchestrator-handoff.md) — current `card` / `epic`

## Commands

```bash
python3 .sdlc/scripts/plane_card.py validate-all --card RPG-N
python3 .sdlc/scripts/plane_state.py in-progress --card RPG-N --branch feature/RPG-N-slug
python3 .sdlc/dsl/cli.py workflow plan --card RPG-N
```

## Do not

- Create local tickets (`specs/`, backlog files) — board only
- Run `workflow start` on epic card — start on **child** only
