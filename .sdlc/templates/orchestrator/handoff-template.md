# Orchestrator handoff template (caveman — max lines from core.tokens.handoff_max_lines)

> Copy shape only. Write to `.sdlc/memory/orchestrator-handoff.md`. No story. No repeat chat.
> Human plans: `.sdlc/process/*.md` — not handoff.

## Routing

| Field | Value |
|-------|-------|
| **Next agent** | `<agent-id>` |
| **Stage complete** | `yes` / `no` |
| **Previous agent** | `<agent-id>` |

## Session

| Field | Value |
|-------|-------|
| **Card** | `RPG-N` |
| **Epic** | `RPG-M` or `(none)` |
| **Branch** | `feature/RPG-N-slug` |
| **Stage** | `<gate stage>` |
| **Intent** | `<FEATURE|BUGFIX|…>` |

## Delta

- `<one line change or finding>`
- `<max 5 bullets>`

## Policy hints (optional)

When orchestrator ran `learning_loop hints --json`, paste compact JSON here for audit:

```json
{"seed":"harness-v7-p2"}
```

## Next

`<one imperative line for orchestrator>`
