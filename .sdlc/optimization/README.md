# Optimization module — Harness v6 Layer 3

> **Mode:** `observe` (see `core.optimization` in `.sdlc/sdlc.yaml`)

## Purpose

Analyze execution ledger events. Detect recurring gateway blocks. Propose new skills/commands/rules (Phase 6 — not auto-applied).

## Files

| File | Role |
|------|------|
| `procedures.yaml` | Meta-tool registry + bandit weights |
| `proposals/` | Generated proposal YAML (Phase 6) |
| `../scripts/optimization/analyzer.py` | Observe-mode report |

## Commands

```bash
make execution-analyze
make execution-analyze N=200
python3 .sdlc/scripts/optimization/analyzer.py --last 100
```

## Related

- [`../process/harness-v6-plan.md`](../process/harness-v6-plan.md)
- [`../scripts/execution_ledger.py`](../scripts/execution_ledger.py)
