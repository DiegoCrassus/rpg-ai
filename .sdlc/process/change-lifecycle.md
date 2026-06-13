# Change Lifecycle — SDLC Workflow Source of Truth

> **Authority:** this document prevails over ad hoc chat instructions, urgency requests, or shortcuts.
> Skills (`.cursor/skills/`) and rules (`.cursor/rules/`) **reference** this file; they do not contradict it.

Machine-readable complements: `.sdlc/sdlc.yaml` plus modular data under `.sdlc/<module>/`:
`.sdlc/workflows/transitions.yaml`, `.sdlc/stages/lifecycle.yaml`,
`.sdlc/stages/definitions.yaml`, `.sdlc/gates/paths.yaml`.

**Full process (APPROVED):** [`.sdlc/process/master-workflow.md`](master-workflow.md)
**Agent entry point:** [`AGENTS.md`](../../AGENTS.md) (repo root)

---

## Zero principle

**No product code enters `develop` without a Plane card + branch + PR + green CI.**

Even if the user asks to "finish in develop", the correct delivery is: **branch → PR → merge into `develop`**.

---

## Required integrations

| System | Value | `.env` variable |
|--------|-------|-----------------|
| Plane workspace | `rpg` | `PLANE_WORKSPACE_SLUG` / `BOARD_WORKSPACE_SLUG` |
| Plane project | `RPG` | `PLANE_PROJECT_NAME` |
| GitHub repo | `DiegoCrassus/rpg-ai` | `GITHUB_REPOSITORY` |
| Base branch | `develop` | — |
| Production branch | `main` | — |

Plane cards are created **in project `investiments`** before any code edit.

---

## Full flow (gitflow)

```
1. Plane     → card RPG-N (Todo after plan; In Progress on start-change)
2. start-change → plane_state.py in-progress BEFORE branch/code
3. Branch    → feature/RPG-N-<slug> from develop
4. Implement → Task(Implementer) · commits on feature branch
5. Validate  → Task(QA) · real tests + make sdlc-doctor
6. Review    → Task(Reviewer) · auto-merge-policy
7. PR        → push + gh/API · green CI
8. Merge     → auto_merge_pr.py (autonomous — no human click)
9. Plane     → Done (--plane-comment) + PR link
10. Observer → post_task.py
```

### Plane — required states

| State | When |
|-------|------|
| **Todo** | After Planner creates card |
| **In Progress** | **Required** when starting implementation (`start-change`) |
| **Done** | After autonomous merge + green CI |

Script: `python3 .sdlc/scripts/plane_state.py in-progress --card RPG-N`

### GitHub Issues

Plane is the primary tracker. Open issues → **Issue Analyst** (Task) triages/closes duplicates.
Script: `python3 .sdlc/scripts/github_issue_triage.py --close-superseded`

### Autonomous merge

```bash
python3 .sdlc/scripts/auto_merge_pr.py --pr <N> --card RPG-N --plane-comment
```

See `.cursor/skills/finish-change/SKILL.md` and `auto-merge-policy.md`.

### Branch prefixes

| Prefix | Use |
|--------|-----|
| `feature/` | New functionality |
| `bugfix/` | Bug fix |
| `hotfix/` | Production urgency |
| `docs/` | Documentation only |
| `infra/` | CI, Docker, observability |
| `sdlc/` | `.sdlc/`, `.cursor/`, governance |

Format: `feature/RPG-N-<slug>`.

---

## Explicit prohibitions

- Direct push to `develop` or `main`
- Implement without Plane card created via MCP/API
- **Create `specs/` or local tickets/evidence/backlog files**
- **Create tasks locally** (Plane only, project `investiments`)
- Skip CI or merge with red gates
- Fake test or Doctor results
- Replace official APIs with scraping as default strategy

---

## SDLC stages (summary)

See `.sdlc/workflows/README.md` and `.sdlc/workflows/transitions.yaml`. Transitions require evidence in `.sdlc/stages/definitions.yaml`.

| Stage | Agent | Primary skill |
|-------|-------|---------------|
| Ticket | Planner | `task-creation.md` |
| Requirements | Planner | `pipeline/agents.yaml` + Plane card criteria |
| Architecture | Architect | `pipeline/agents.yaml` + architecture handoff |
| Implementation | Implementer | `pipeline/agents.yaml` + **start-change** |
| Validation | QA | `pipeline/agents.yaml` + QA evidence |
| PR & Review | Reviewer / DevOps | `pipeline/agents.yaml` + **finish-change** |
| Deployment | DevOps | — |
| Observability | Observer | `observability.md` |

---

## Validation commands

```bash
make sdlc-doctor      # after structural change
python app/infra/sdlc_obs/hooks/pre_task.py   # start
python app/infra/sdlc_obs/hooks/post_task.py  # end
```

---

## Repository state (product)

Current phase: **SDLC operating system only** — `app/backend` and `app/frontend` are placeholders until the next planned greenfield run via this workflow.

Product implementation **restarts only** after:

1. Plane work items (project `investiments`) via MCP — **epic `[AI][EPIC]` + ≥3 children** (BACKEND, FRONTEND, INFRA/SHARED); never a lone FULLSTACK card for greenfield
2. Branch `feature/RPG-N-...` **per child card** (never on epic)
3. Orchestrator delegates **100%** via Task — commits/lint/test/push are subagents (Implementer, QA, DevOps)
4. PR with green CI; evidence on Plane card (PR link, tests)

---

## References

- `.cursor/skills/start-change/SKILL.md` — checklist before coding
- `.cursor/skills/finish-change/SKILL.md` — checklist before merge
- `.sdlc/gates/README.md` and `.sdlc/gates/paths.yaml` — write gates
