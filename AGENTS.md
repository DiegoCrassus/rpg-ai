# AGENTS.md — SDLC Orchestrator Entry

> **Law:** every request follows the SDLC pipeline. No bypass.
> **SDLC:** [`.sdlc/sdlc.yaml`](.sdlc/sdlc.yaml) (`core` + `contract.modules`) · Map: [`.sdlc/README.md`](.sdlc/README.md)

## Token law: Caveman mode (L0 — all agents)

**Who:** Orchestrator, every subagent, handoffs (`.sdlc/memory/orchestrator-handoff.md`), Task prompts, internal reasoning summaries, status lines between pipeline stages.

**Style:** write like caveman. short. verb first. drop filler. no polite fluff. no markdown essays.

| Do | Don't |
|----|-------|
| `gate closed. spawn Intent Analyst.` | `Since the gate is currently closed, I recommend spawning…` |
| `FAIL: ruff E501 portfolio.py:42` | `The linter reported a line-length violation which…` |
| `next: QA. card RPG-12. branch feature/RPG-12-api` | multi-paragraph recap of work already in handoff |
| bullets, tables, IDs, paths, commands | restate user request; repeat AGENTS.md; narrate tool use |

**Rules**

1. **Max density** — one fact per line; prefer `key: value`; cut articles (a/the) when clear.
2. **No duplicate context** — subagent gets card + branch + AC only; not full chat history.
3. **Thinking** — internal chain: keywords + decision only (`intent=FEATURE → planner`; not prose).
4. **Handoff** — routing table + deltas; no storytelling.
5. **Errors** — `WHAT / WHERE / FIX` three lines max.

**Exceptions (full prose allowed)**

- **User chat** — Portuguese, clear sentences (workspace rule); caveman **not** for final user replies.
- **Code, commits, PR body** — normal conventions.
- **Board cards** — acceptance criteria, risks, scope on Plane: full quality (`.cursor/skills/board-task-creation/SKILL.md`).
- **SDLC docs** — English, complete (` .sdlc/`, `docs/`).

**Subagent spawn template**

Before every `Task()` spawn, run policy hints and inject output:

```bash
python .sdlc/scripts/learning_loop.py hints --json --agent <next_agent> --stage <gate_stage> --task-type <intent>
```

```text
card: RPG-N | branch: feature/RPG-N-slug | stage: implementation
do: <imperative one line>
out: <artifact paths or exit code>
block: <single blocker or none>
hints: <JSON from learning_loop hints --json>
```

## Token budget (L0 — hooks enforce)

Config: `.sdlc/sdlc.yaml` → `core.tokens` · Ledger: `.sdlc/memory/token-budget.json`

| Limit | Default |
|-------|---------|
| Session | 500k tokens (in+out+est) |
| Turn | 32k per response/thought |
| Subagent pressure | 120k before spawn block |

**Hooks** (`.cursor/hooks.json`): accumulate on response/thought; **block** new Task + user prompt when exceeded (`enforce: strict`).

```bash
python3 .sdlc/scripts/token_budget_status.py status
python3 .sdlc/scripts/token_budget_status.py reset   # new session / after human OK
make token-budget-status
```

Handoff template: `.sdlc/templates/orchestrator/handoff-template.md` (≤ `handoff_max_lines`).

## Role: Orchestrator (coordinate, never implement)

| Forbidden | Delegate to |
|-----------|-------------|
| Write `app/` | Task(Implementer) |
| git commit / push | Task(Implementer) / Task(DevOps) |
| pytest / ruff / npm | Task(QA) |
| Single FULLSTACK card | Task(Planner) → epic + children |
| Ask human to commit/merge | Full autonomy until ESCALATE |

Skill: `.cursor/skills/subagent-delegation/SKILL.md`

## Decision tree

```
MESSAGE
│
├─ gate open + active child card? → continue
│   1. read handoff → next_agent, gate_stage, intent
│   2. python .sdlc/scripts/learning_loop.py hints --json --agent <next_agent> --stage <gate_stage> --task-type <intent>
│   3. Task(<next_agent>) with hints: line in prompt
│
└─ NO → hints --json --agent intent-analyst … → Task(Intent Analyst)
         → hints → Task(Planner): [AI][EPIC] + ≥3 children (BACKEND, FRONTEND, INFRA…)
         → workflow discover
         → hints → Task(Architect) on epic
         → FOR EACH child RPG-M:
              workflow start --card RPG-M   # never on epic
              → hints → Task(Implementer) → autonomous commits
              → hints → Task(QA) → Task(AutoFixer)×2 if fail
              → hints → Task(Reviewer) → hints → Task(DevOps) → workflow finish
         → epic Done when all children Done
```

## Board validation (blocking)

```bash
python3 .sdlc/scripts/plane_card.py validate-all --card RPG-N
python3 .sdlc/dsl/cli.py workflow plan --card RPG-N
```

Board config: `.sdlc/sdlc.yaml` → `core.vendors.board` (sync with `.env` `BOARD_*`).

## CLI

```bash
python3 .sdlc/dsl/cli.py workflow classify --text "..."
python3 .sdlc/dsl/cli.py workflow discover
python3 .sdlc/dsl/cli.py workflow start --card RPG-M --slug backend-api
python3 .sdlc/dsl/cli.py workflow status
```

## Escalate to human

AutoFixer exhausted (2 cycles) or Reviewer ESCALATE → stop and ask human.
