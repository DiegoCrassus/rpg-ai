# DSL module

> **Canonical lifecycle:** [`.sdlc/process/lifecycle-model.yaml`](../process/lifecycle-model.yaml)

## Purpose

Python CLI and libraries for SDLC workflow, gates, validation, Doctor, and enforcement helpers.

## When to read

| Situation | Start with |
|-----------|------------|
| Gate / write policy | `gate.py`, `lifecycle_model.py` |
| `workflow start` / classify | `workflow.py`, `intent_rules.py`, `transition_check.py` |
| Manifest load / validate | `loader.py`, `validator.py` |
| Shard drift | `lifecycle_shard_drift.py` |
| Emergency bypass | `break_glass.py`, [`../process/break-glass.md`](../process/break-glass.md) |

## Boundaries

- Does not own Cursor hooks (see `.cursor/hooks/`).
- Legacy `stages/lifecycle.yaml` and `workflows/transitions.yaml` are shims; Doctor **FAIL** on drift.

## Commands

```bash
python3 .sdlc/dsl/cli.py doctor
python3 .sdlc/dsl/cli.py workflow status
make sdlc-validate
```
