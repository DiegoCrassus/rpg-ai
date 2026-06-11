# Pipeline module

> **Canonical roster:** [`../manifest/catalog.yaml`](../manifest/catalog.yaml) (Doctor syncs with `gateways/policy.yaml`)  
> **Runtime bindings:** [`agents.yaml`](agents.yaml) · **Stages:** [`../process/lifecycle-model.yaml`](../process/lifecycle-model.yaml)

## Purpose

Maps each **lifecycle stage** to the **agent** and **skill** that should run. This is the runtime pipeline graph; manifest is the static catalog of available agents.

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

## Entry structure in `agents.yaml`

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

- Collapse multiple pipeline roles in one Orchestrator turn
- Skip QA or Reviewer before DevOps merge
