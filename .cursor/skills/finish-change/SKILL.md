# Skill: Finish Change

> **Workflow authority:** `.sdlc/process/change-lifecycle.md`

## Purpose

Finish a work unit: validate, open PR, **autonomous merge** into `develop`, evidence on Plane.

## When to use

- Implementation complete and local tests passing
- After **QA** and **Reviewer** (Task subagents) — see `.cursor/skills/subagent-delegation/SKILL.md`

## Procedure

### 1. Local validation

```bash
make sdlc-doctor
python3 -m pytest app/backend/tests/ -v    # when backend exists
cd app/frontend && npm run build           # when frontend exists
```

### 2. Commit on feature branch (never on develop)

```bash
git add <files>
git commit -m "feat(scope): summary (RPG-N)"
```

### 3. Push and open PR to develop

```bash
git push -u origin HEAD
gh pr create --base develop --title "..." --body "..."
```

Without `gh` CLI:

```bash
# GitHub REST API or script — see .sdlc/scripts/auto_merge_pr.py after PR is created
```

PR body must include:
- Plane link `RPG-N`
- Test plan checklist with real outputs
- `Closes` only if a linked GitHub issue exists (Plane is primary)

### 4. Wait for green CI

Workflow: `.github/workflows/ci.yml`

### 5. Autonomous merge (no human approval)

**DevOps/Orchestrator runs merge** when all gates pass (`.cursor/skills/auto-merge-policy.md`):

```bash
python3 .sdlc/scripts/auto_merge_pr.py --pr <N> --card RPG-N --plane-comment
```

The script:
1. Waits for CI `success` on the PR branch
2. Squash merge → `develop`
3. Deletes remote branch
4. Moves Plane card → **Done** with PR link

**Forbidden** to ask the user to click Merge on GitHub when gates are green.

Blocking criteria (human escalation): see `auto-merge-policy.md` — auth, diff >500 lines, security HIGH/CRITICAL, Reviewer ESCALATE.

### 6. Plane → Done (structured evidence)

Fill evidence JSON (see `.cursor/skills/plane-formatting/SKILL.md`):

```bash
python3 .sdlc/scripts/auto_merge_pr.py --pr <N> --card RPG-N --plane-comment \
  --evidence-file .sdlc/templates/plane/evidence-template.json
```

Or manually:

```bash
python3 .sdlc/scripts/plane_state.py done --card RPG-N \
  --evidence-file .sdlc/templates/plane/evidence-template.json
```

**Required evidence:** Problems Solved, Technical Delivery, Validation, Context for Future.

### 7. Observer post-task

```bash
python3 .sdlc/obs/hooks/post_task.py --task "RPG-N" --status completed
```

## Mandatory delegation before merge

| Subagent | When |
|----------|------|
| **QA** | After Implementer — real pytest/build evidence |
| **Reviewer** | After QA — code-review checklist + auto-merge-policy |
| **DevOps** | Run `auto_merge_pr.py` — do not delegate merge to human |

## Failure modes

| Situation | Action |
|-----------|--------|
| CI failed | Fix on branch; new push; **do not** merge |
| Merge blocked by policy | Escalate human; document on Plane |
| User asks for manual merge | Explain that finish-change is autonomous by design |
