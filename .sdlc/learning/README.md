# Learning Loop — Harness v6 Layer 3

> Operational reinforcement (no LLM training). Task-level events + deterministic reward.

## Modules

| File | Role |
|------|------|
| `schemas.py` | `SDLCRunEvent`, task types |
| `reward_engine.py` | Reward in [-1, 1] |
| `event_store.py` | `.sdlc/learning/data/events.jsonl` |
| `policy_memory.py` | `.sdlc/learning/policy_memory.yaml` |
| `policy_optimizer.py` | Observe-mode suggestions |
| `test_learning.py` | pytest |

## CLI

```bash
python .sdlc/scripts/learning_loop.py status
python .sdlc/scripts/learning_loop.py record-session
python .sdlc/scripts/learning_loop.py analyze --last 100
python .sdlc/scripts/learning_loop.py policy-update --card RPG-N
```

## Hooks

`subagentStop` → `.cursor/hooks/sdlc_learning_hook.py` (after post-gateway)

## Related

- [harness-v6-plan.md](../process/harness-v6-plan.md)
- [execution_ledger.py](../scripts/execution_ledger.py) — stage-level ledger
