# Skill: Subagent Delegation

> **Authority:** `.sdlc/process/master-workflow.md` · `.cursor/rules/orchestrator.mdc`

## Purpose

The Orchestrator **only coordinates**. Every action that mutates code, git, CI, or Plane — except READONLY answers — runs inside a **Task(subagent)**.

## Golden rule

> If the Orchestrator would run `Write`, `git commit`, `pytest`, `ruff`, or `gh pr` — **stop** and spawn the subagent from the matrix below.

## Pipeline vs support agents

| Kind | Handoff Next agent? | Spawn |
|------|---------------------|-------|
| **Pipeline** (Intent Analyst → DevOps) | **Yes** — read handoff → `Task(next_agent)` | Hints mandatory |
| **Support** (Doctor, Observer, …) | **Never** — on-demand only | `Task(subagent)` via agent path or command |

Support agents are listed in `policy.yaml` → `support_agents`. They bypass `pre_gateway` route enforcement when explicitly requested.

| Support agent | Skill / invocation path |
|---------------|-------------------------|
| `doctor` | `.cursor/commands/sdlc-doctor.md` · skill `structural-validation` |
| `observer` | `.cursor/agents/observer.md` |
| `issue-analyst` | `.cursor/agents/issue-analyst.md` |
| `sdlc-auditor` | `.cursor/agents/sdlc-auditor.md` |
| `security-scanner` | `.cursor/agents/security-scanner.md` |
| `migration-runner` | `.cursor/agents/migration-runner.md` |
| `contract-validator` | `.cursor/agents/contract-validator.md` |
| `rollback-agent` | `.cursor/agents/rollback-agent.md` |

## Delegation matrix

| Action | Subagent | Orchestrator |
|--------|----------|--------------|
| Classify intent | `intent-analyst` | Task only |
| Create epic + child Plane cards | `planner` | Task only |
| Architecture notes on Plane | `architect` | Task only |
| Implement code in `app/` | `implementer` | Task only — **never Write app/** |
| Run tests, lint, doctor | `qa` | Task only |
| Fix CI/lint/test failures | `auto-fixer` | Task only (max 2 loops) |
| Code review | `reviewer` | Task only |
| Commit on feature branch | `implementer` | Task only — **never ask human to commit** |
| Push branch + open PR | `devops` | Task only |
| Merge when CI green | `devops` + `workflow finish` | Task only |
| Plane state / comments | `planner` or Orchestrator shell via scripts | Scripts OK |

## Plane granularity

| Intent | Plane structure |
|--------|-----------------|
| GREENFIELD | 1 epic + >=3 child cards |
| FEATURE | 1 epic + >=2 child cards |
| BUGFIX/HOTFIX | 1 focused card OK |

Validate with `python3 .sdlc/scripts/plane_card.py validate-all --card RPG-N` before `workflow start`.

## Orchestrator allowed without Task

- `python3 .sdlc/dsl/cli.py workflow …` meta-tools
- `python3 .sdlc/scripts/plane_state.py …`
- Read files, `workflow status`, `discovery_hook.py`
- READONLY answers to user
- Spawning the **next** Task after handoff Markdown received

## Orchestrator forbidden (never do directly)

- `Write` / `StrReplace` on delegated paths when gate open (`.sdlc/`, `.cursor/`, `app/`, handoff) — hooks block; use `Task(next_agent)`
- `Write` / `StrReplace` under `app/backend`, `app/frontend`, `app/shared`
- `git add`, `git commit`, `git push` (Implementer/DevOps via Task)
- `pytest`, `ruff`, `npm run build`, `make` (except `sdlc-doctor` for gate check) — QA via Task
- Implementing "just this one file" without Task(Implementer)
- Collapsing Planner + Architect + Implementer in one turn

## Session loop (mandatory)

```
1. Task(Intent Analyst) → handoff Markdown
2. Task(Planner) → epic RPG-N + child cards RPG-N+1… (validate-all)
3. python3 .sdlc/dsl/cli.py workflow discover
4. Task(Architect) → notes on epic Plane
5. FOR EACH child card (sequential or parallel Tasks):
     a. workflow start --card RPG-M --stage implementation
     b. Task(Implementer) → code + autonomous commits on feature branch
     c. Task(QA) → lint/test/doctor
     d. IF fail → Task(AutoFixer) → re-Task(QA) (max 2)
     e. Task(Reviewer) → APPROVE|ESCALATE
     f. Task(DevOps) → push + PR if needed
     g. workflow finish --pr N --card RPG-M
6. Mark epic Done when all children Done
```

## Handoff contract

Each subagent overwrites `.sdlc/memory/orchestrator-handoff.md` using **Markdown sections** (see `.sdlc/memory/README.md`). Minimum:

| Section | Key fields |
|---------|------------|
| **Routing** | **Next agent**, **Stage complete**, **Previous agent** |
| **Session** | **Card**, **Branch**, **Stage** |
| **Classification** | **Intent** (when applicable) |

Orchestrator reads **Next agent** → spawns that subagent → does **not** continue work inline.

## Autonomy (no human)

- Implementer commits without asking
- QA runs lint/test without asking
- AutoFixer fixes without asking (within scope)
- DevOps pushes and opens PR without asking
- Merge via `auto_merge_pr.py` when APPROVE + CI green

Human only when: AutoFixer exhausted, ESCALATE, or external blocker (Plane/API down).

## Task prompt skeleton

Before spawning, run policy hints (mandatory):

```bash
python .sdlc/scripts/learning_loop.py hints --json --agent <next_agent> --stage <gate_stage> --task-type <intent>
```

```text
Read .cursor/agents/<agent>.md and the relevant skills.
Card: RPG-N (child card, not epic unless this is planning/architecture).
Branch: feature/RPG-N-<slug>
hints: <JSON stdout from learning_loop hints --json>
Return Markdown handoff to .sdlc/memory/orchestrator-handoff.md.
Do not ask the human to commit, push, or merge.
```
