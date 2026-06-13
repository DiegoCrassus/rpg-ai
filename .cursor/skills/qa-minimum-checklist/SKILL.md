# Skill: QA Minimum Checklist

> **Authority:** `.sdlc/process/master-workflow.md` · subagent `qa.md`

## Purpose

QA subagent decides scope but **must** run this minimum checklist before APPROVE handoff.

## When to use

- Every `Task(QA)` after Implementer handoff
- AutoFixer re-runs full checklist after fixes

## Checklist (all required)

| # | Check | Command / evidence |
|---|-------|-------------------|
| 1 | SDLC Doctor | `make sdlc-doctor` exit 0 |
| 2 | Gate tests | `pytest .sdlc/dsl/test_gate.py -q` if SDLC touched |
| 3 | Product tests | `pytest app/` if backend changed |
| 4 | Lint Python | `ruff check app/ .sdlc/` on changed paths |
| 5 | Frontend build | `npm run build` in `app/frontend/` if frontend changed |
| 6 | Plan validation | `validate-all --card RPG-N` if Plane desc changed |
| 7 | AC mapping | Each AC from child card verified individually |
| 8 | QA evidence file | `python .sdlc/scripts/qa_evidence.py write --card RPG-N` → `.sdlc/memory/qa-evidence-RPG-N.json` |

## Handoff Markdown

```markdown
## Routing

| Field | Value |
|-------|-------|
| **Next agent** | reviewer |
| **Stage complete** | yes |
| **Previous agent** | qa |

## Session

| Field | Value |
|-------|-------|
| **Card** | RPG-N |

## Validation

- **Tests passed:** yes
- **Doctor exit:** 0
- **Pytest:** N passed
- **Ruff:** clean
- **Build:** skipped

## Acceptance criteria

- AC-1: pass
```

## On failure

1. Post `qa_fail` comment on Plane card with output
2. Set `next_agent: auto-fixer`
3. Orchestrator spawns Task(AutoFixer) — **not** inline fixes
4. Max 2 QA→AutoFixer cycles → `human_required`

## Prohibitions

- Never fake test output
- Never skip doctor for "small" changes
- Orchestrator never runs pytest/ruff directly
