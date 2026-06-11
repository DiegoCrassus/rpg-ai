# Skill: Start Change

> **Workflow authority:** `.sdlc/process/change-lifecycle.md`

## Purpose

Start a work unit **before any code edit**, creating Plane traceability + gitflow branch.

## When to use

- Before implementing any feature, bugfix, or infra change
- When the user asks for implementation (even with urgency — gitflow is not optional)
- **Only after** `plane-task-creation` has filled the card with a complete plan

## Procedure

### 0. Verify plan on Plane

Confirm card `RPG-N` passed the gate in `.cursor/skills/plane-task-creation/SKILL.md`. If the body only has AC stubs → **stop** and complete the plan.

### 1. Plane → **In Progress** (required)

**Before** creating a branch or editing code, move the card to **In Progress**:

```bash
python3 .sdlc/scripts/plane_state.py in-progress --card RPG-N \
  --comment "start-change: branch feature/RPG-N-<slug>"
```

| Gate | If it fails |
|------|-----------|
| Card exists on Plane | Stop — create via `plane-task-creation` |
| State = In Progress | Stop — do not implement while Todo/Backlog |

If the card does not exist yet, create via MCP (`.cursor/skills/plane-sdlc/SKILL.md`) already in **In Progress**.

### 2. Record card number

Note `RPG-N` — required in the branch name.

### 3. Create branch from develop

```bash
git checkout develop
git pull origin develop
git checkout -b feature/RPG-N-<slug>
```

Convention: `.cursor/skills/branch-naming.md`

### 4. Observer pre-task (when available)

```bash
python3 .sdlc/obs/hooks/pre_task.py --task "RPG-N: <title>" --stage implementation --agent implementer
```

Fallback if legacy path: `python3 app/infra/sdlc_obs/hooks/pre_task.py`

### 6. Open mechanical gate (required)

```bash
python3 .sdlc/dsl/cli.py workflow start --card RPG-N --slug <slug> --stage implementation
python3 .sdlc/dsl/cli.py workflow status   # gate open + card
```

Legacy (still valid):

```bash
python3 .sdlc/scripts/sdlc_gate.py open --card RPG-N --stage implementation
```

### 7. Only then edit code

Never commit on `develop` or `main` during implementation.

## Failure modes

| Situation | Action |
|-----------|--------|
| Card in Todo/Backlog during implementation | **Stop** — `plane_state.py in-progress` first |
| Plane unavailable | **Stop** — fix token; do not create local backlog |
| No card ID | **Stop** — create Plane card first |
