# Optimization module — Harness v6 Layer 3

> **Mode:** `observe` (see `core.optimization` in `.sdlc/sdlc.yaml`)

## Purpose

Analyze execution ledger + learning events. Detect recurring gateway blocks. Propose new skills/commands/rules (Phase 6 — not auto-applied).

## Files

| File | Role |
|------|------|
| `procedures.yaml` | Meta-tool registry + bandit weights |
| `proposals/` | Generated proposal YAML (Phase 6) |

## Commands

```bash
make execution-analyze
make execution-analyze N=200
make learning-loop-analyze
python3 .sdlc/scripts/learning_loop.py analyze --last 100
```

## Related

- [`../process/harness-v6-plan.md`](../process/harness-v6-plan.md)
- [`../process/harness-v7-change-plan.md`](../process/harness-v7-change-plan.md)
- [`../scripts/execution_ledger.py`](../scripts/execution_ledger.py)
- [`../runtime/manifest.yaml`](../runtime/manifest.yaml)
