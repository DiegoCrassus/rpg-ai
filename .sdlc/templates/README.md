# Templates module

> **Data:** [`plane/`](plane/README.md) · **Use:** evidence payload examples and reusable Plane payload shapes

## Purpose

Holds non-runtime templates and examples used by Plane evidence flows. This is not a task backlog and not long-term source of truth; Plane cards and PRs hold delivery evidence.

## When to read

| Situation | Look at |
|-----------|---------|
| Posting evidence to Plane | `plane/README.md` and `plane/evidence-template.json` |
| Designing a new evidence payload | `plane/README.md` |
| Reviewing planner output shape | `planner/example-sdlc-plan.md` |

## Classification

| Path | Class | Recommendation |
|------|-------|----------------|
| `plane/evidence-template.json` | `agent-procedure` | Keep as the canonical evidence payload template |
| `planner/example-sdlc-plan.md` | `human-reference`, `agent-procedure` | Keep as the canonical planner output example |
| Future generic templates | `agent-procedure` | Prefer generic names such as `evidence-template.json` |

## Related modules

- [`../scripts/README.md`](../scripts/README.md) — `plane_evidence.py`, `plane_card.py`, `auto_merge_pr.py`
- [`../workboard/README.md`](../workboard/README.md) — Plane card rules
- [`../memory/README.md`](../memory/README.md) — runtime handoff vs durable evidence

## Do not

- Create local tickets or backlog files here.
- Store secrets or API responses with private data.
- Add per-card evidence unless it is required for a current Plane/PR workflow.
