# Stages module

> **Canonical stage graph:** [`../process/lifecycle-model.yaml`](../process/lifecycle-model.yaml)  
> **Shim:** [`lifecycle.yaml`](lifecycle.yaml) (must match model; Doctor **FAIL** on drift)  
> **Definitions:** [`definitions.yaml`](definitions.yaml) · **Index:** `contract.modules.stages`

## Purpose

Defines the **10-stage AI-Native lifecycle**: inputs, outputs, required evidence, context token budgets, and gates per stage. Stages are conceptual; the **pipeline** maps them to agents.

## When to read

| Agent / moment | File | Why |
|----------------|------|-----|
| Planner | `definitions.yaml` → `requirements` | Required outputs before architecture |
| Architect | `definitions.yaml` → `architecture` | Evidence before implementation |
| Implementer | `definitions.yaml` → `implementation` | Scope + `context_budget_tokens` (40k) |
| QA | `definitions.yaml` → `validation` | `required_evidence` checklist |
| Reviewer | `definitions.yaml` → `review` | Review gates |
| Orchestrator | `lifecycle.yaml` | Ordered stage ids (1–10) |

## File roles

| File | Role |
|------|------|
| **`lifecycle.yaml`** | Ordered list: `ticket` → `requirements` → … → `autofix` |
| **`definitions.yaml`** | Full contract per stage: inputs, outputs, evidence, budgets, skills |

## Stage ids (quick reference)

1. `ticket` · 2. `requirements` · 3. `architecture` · 4. `implementation` · 5. `validation` · 6. `review` · 7. `deployment` · 8. `observability` · 9. `incident` · 10. `autofix`

## Related modules

- [`../workflows/README.md`](../workflows/README.md) — legal transitions between stages
- [`../pipeline/README.md`](../pipeline/README.md) — which agent owns which stage
- [`../gateways/README.md#write-gate-mechanical-acl`](../gateways/README.md#write-gate-mechanical-acl) — write permissions per `workflow start --stage`

## Commands

```bash
make sdlc-stages    # print stage list from DSL
```

## Do not

- Skip stages without documented reason (`.sdlc/process/master-workflow.md`)
- Confuse **workflow stage** (`session-gate.json` → `implementation`) with **lifecycle stage id** — they align but gate stage is mechanical
