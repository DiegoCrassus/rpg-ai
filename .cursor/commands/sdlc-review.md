# Command: SDLC Review

## Purpose

Review changes for correctness, security, maintainability, testability, and SDLC alignment.

## When to Use

- When a PR is opened or ready for review
- When peer-reviewing implementation output before merge
- During the PR & Review stage

## Procedure

### Step 1 — Collect Context

1. Identify the PR or diff being reviewed.
2. Read the original Plane work item (MCP) and PR description.
3. Read `.sdlc/stages/definitions.yaml` review stage gates.
4. Note the acceptance criteria.

### Step 2 — Structural Review

Check:
- [ ] Only files in scope were changed
- [ ] No unrelated changes mixed in
- [ ] No unnecessary reformatting
- [ ] Folder conventions respected (`app/frontend/`, `app/backend/`, etc.)

### Step 3 — Correctness Review

Check:
- [ ] Implementation matches the plan
- [ ] Acceptance criteria are met by the diff
- [ ] Edge cases handled
- [ ] No obvious logic errors

### Step 4 — Security Review

Check:
- [ ] No secrets, tokens, or credentials in code
- [ ] No SQL injection risks (use parameterized queries)
- [ ] No arbitrary code execution (no `eval`, `exec` on user input)
- [ ] Input validation present where needed
- [ ] No overly permissive file system access

### Step 5 — Quality Review

Check:
- [ ] Tests exist for new logic
- [ ] Tests are deterministic
- [ ] Type hints on public functions (Python)
- [ ] No `print` in library code
- [ ] Comments explain intent, not mechanics
- [ ] No dead code

### Step 6 — SDLC Alignment Review

Check:
- [ ] Docs updated if required
- [ ] Handoff summary exists for stage transition
- [ ] Doctor passed (confirm via CI or manual run)

### Step 7 — Decision

Output one of:
- **APPROVE** — All checks pass, no required changes.
- **REQUEST CHANGES** — List specific required changes.
- **ESCALATE** — Risk too high for autonomous resolution; human review required.

### Step 8 — Record

Document:
- Review decision
- Risk notes (even if approved)
- Required fixes (if changes requested)
- Any deferred items for future work

## Output Format

```markdown
## Review: <PR title>

### Decision
APPROVE | REQUEST CHANGES | ESCALATE

### Risk Notes
- <risk 1>

### Required Changes (if REQUEST CHANGES)
- [ ] <change 1>

### Deferred Items
- <item 1>
```
