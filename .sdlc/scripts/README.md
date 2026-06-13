# Scripts module

> **Data:** deterministic scripts under this folder · **Index:** `contract.toolchain` and `.sdlc/README.md`

## Purpose

Executable SDLC automation for Plane, GitHub, gates, discovery, evidence, and memory compaction. These scripts are the deterministic counterpart to Cursor agents and skills.

## When to read

| Situation | Script |
|-----------|--------|
| Gate status/check | `sdlc_gate.py` |
| Plane card validation | `plane_card.py` |
| Plane state transition | `plane_state.py` |
| GitHub issue triage | `github_issue_triage.py` |
| PR merge + Plane Done | `auto_merge_pr.py` |
| Discovery before planning | `discovery_hook.py` |
| Memory compaction | `compact_memory.py` |
| Execution ledger | `execution_ledger.py` |
| Learning loop | `learning_loop.py` |
| Optimization observe | `learning_loop.py analyze` |
| Plane evidence formatting | `plane_html.py`, `plane_evidence.py` |
| Legacy migration concern | `migrate_v5_modular.py` (retired guard; exits non-zero) |

## Runtime classification

| Script group | Class | Notes |
|--------------|-------|-------|
| `plane_*.py`, `auto_merge_pr.py` | `runtime-critical` | Used by workflow/DevOps/Plane evidence |
| `sdlc_gate.py`, `discovery_hook.py` | `runtime-critical` | Used by gates and planning |
| `compact_memory.py` | `runtime-state` | Updates operational memory |
| `meta-tools/*.sh` | `agent-procedure` | Deterministic shortcuts invoked directly by Makefile or humans |
| `migrate_v5_modular.py` | `retired-guard` | Must not rewrite the current v5 layout |

## Related modules

- [`../gates/README.md`](../gates/README.md) — gate config and runtime state
- [`../workboard/README.md`](../workboard/README.md) — Plane granularity
- [`../memory/README.md`](../memory/README.md) — generated state and handoff
- [`../doctor/README.md`](../doctor/README.md) — structure validation

## Do not

- Store secrets in scripts.
- Use scripts to create local task/backlog files.
- Re-enable the retired v5 migration behavior.
