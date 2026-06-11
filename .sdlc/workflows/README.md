# Workflows module

> **Canonical transitions:** [`../process/lifecycle-model.yaml`](../process/lifecycle-model.yaml)  
> **Shim metadata:** [`transitions.yaml`](transitions.yaml) · **CLI:** `python3 .sdlc/dsl/cli.py workflow …`

## Purpose

Defines **allowed transitions** between lifecycle stages: preconditions, responsible agent, skill, and expected outputs. Complements `stages/definitions.yaml` (what each stage is) with **when you may move** (workflow edges).

## When to read

| Transition | Workflow id | Agent |
|------------|-------------|-------|
| Requirements approved → design | `requirements_to_architecture` | architect |
| Architecture approved → code | `architecture_to_implementation` | implementer |
| Code done → test | `implementation_to_validation` | qa |
| Tests pass → PR | `validation_to_review` | reviewer |
| Review pass → merge | `review_to_deployment` | devops |

## Structure in `transitions.yaml`

Each workflow entry:

| Field | Meaning |
|-------|---------|
| `from_stage` / `to_stage` | Lifecycle stage ids |
| `preconditions` | Must be true before transition (e.g. tests pass) |
| `agent` / `skill` | Who runs the transition |
| `outputs` | Artifacts expected after transition |

## Related modules

- [`../stages/README.md`](../stages/README.md) — stage definitions and evidence
- [`../pipeline/README.md`](../pipeline/README.md) — agent bindings
- [`../gates/README.md`](../gates/README.md) — gate opens on `workflow start`, closes on `workflow finish`

## CLI mapping

| Command | Effect |
|---------|--------|
| `workflow classify` | Intent → handoff |
| `workflow plan` | Validate Plane card plan |
| `workflow start` | Open gate + In Progress on Plane |
| `workflow finish` | Close gate + optional merge |
| `workflow status` | Gate + handoff preview |

## Do not

- Jump from `architecture` to `deployment` without validation and review workflows
- Treat urgency as a reason to skip transitions (`.sdlc/process/master-workflow.md`)
