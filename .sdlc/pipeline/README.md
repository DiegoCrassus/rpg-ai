# Pipeline module

> **Source of truth:** [`../manifest/catalog.yaml`](../manifest/catalog.yaml) → `stage_bindings`  
> **Generated view:** [`agents.yaml`](agents.yaml) (AUTO-GENERATED — do not edit)  
> **Stages:** [`../process/lifecycle-model.yaml`](../process/lifecycle-model.yaml)

## Purpose

`agents.yaml` is a **generated** view of `catalog.yaml` `stage_bindings`. It maps each **lifecycle stage** to the **agent** and **skill** that should run. Edit bindings in catalog; regenerate with:

```bash
python .sdlc/scripts/sdlc_sync_model.py --write
```

## When to read

| You are | Look up |
|---------|---------|
| **Orchestrator** | After handoff `Next agent` — confirm agent exists in `pipeline[]` |
| **Planner** | Stages `ticket`, `requirements` |
| **Architect** | Stage `architecture` |
| **Implementer** | Stages `implementation`, `autofix` |
| **QA** | Stage `validation` |
| **Reviewer** | Stage `review` |
| **DevOps** | Stage `deployment` |

## Pipeline order (typical FEATURE)

```
Intent Analyst → Planner → Architect
  → [per child] workflow start → Implementer → QA → AutoFixer? → Reviewer → DevOps → workflow finish
```

## Entry structure in `agents.yaml` (generated from `stage_bindings`)

Each `pipeline[]` item contains:

| Field | Meaning |
|-------|---------|
| `id` | Agent id (matches `.cursor/agents/<id>.md`) |
| `stages` | Lifecycle stage ids this agent owns |
| `cursor_agent` | Path to agent instruction file |
| `skill` | Bound skill id, description, `expected_outputs` |

## Related modules

- [`../manifest/README.md`](../manifest/README.md) — full agent list + MCPs
- [`../workflows/README.md`](../workflows/README.md) — transition preconditions
- [`../memory/README.md`](../memory/README.md) — handoff `Next agent` field

## Orchestrator rule

After every subagent Task: read [`orchestrator-handoff.md`](../memory/orchestrator-handoff.md) → spawn **`Next agent`** from handoff — never continue implementation inline.

## Do not

- Edit `agents.yaml` by hand — update `catalog.yaml` `stage_bindings` and run sync
- Collapse multiple pipeline roles in one Orchestrator turn
- Skip QA or Reviewer before DevOps merge
