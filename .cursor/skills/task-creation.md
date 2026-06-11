# Skill: Task Creation

## Purpose

Produce a complete, structured task plan from a raw idea or ticket request. Every plan created by this skill follows a consistent format that is both human-readable and agent-executable — with a story, measurable acceptance criteria, a Definition of Done, and `[AI][TYPE]` tag naming convention.

## When to Use

- At the Ticket or Requirements stage
- When a user or agent provides a raw idea, request, or bug report
- When planning is delegated by `@sdlc-run` or the Orchestrator
- When creating sub-tasks from an approved architecture plan

---

## Required Inputs

- Raw request (text description of the idea or need)
- `.sdlc/sdlc.yaml` — project name, workspace, integrations
- `.sdlc/memory/architecture.md` — current boundaries and known constraints
- `.sdlc/memory/business-rules.md` — domain invariants and SDLC rules

---

## Task Naming Convention

Every task name produced by this skill must follow this format:

```
[AI][TYPE] Short imperative title (max 8 words)
```

### Tags

| Tag | Meaning |
|-----|---------|
| `[AI]` | Always present — signals this was created or drafted by a Cursor agent. Human review required before merge. |
| `[BACKEND]` | Primary change is in `app/backend/` |
| `[FRONTEND]` | Primary change is in `app/frontend/` |
| `[INFRA]` | Primary change is in `app/infra/` |
| `[SHARED]` | Primary change is in `app/shared/` |
| `[SDLC]` | Change affects `.sdlc/`, `.cursor/`, `Makefile`, or project governance |
| `[DOCS]` | Change is documentation-only (`docs/`) |
| `[FULLSTACK]` | **Deprecated for greenfield/FEATURE** — split into BACKEND + FRONTEND child cards (see `plane-task-creation/SKILL.md`) |

### Title rules

- Imperative verb: "Add", "Create", "Fix", "Refactor", "Remove", "Update" — not "Adding" or "Added"
- Specific enough to identify the change: "Add Plane work item endpoint" not "Add endpoint"
- Max 8 words after the tags
- English only

### Examples

```
[AI][BACKEND]   Add internal Plane work item creation endpoint
[AI][FRONTEND]  Add SDLC stage selector to task creation form
[AI][INFRA]     Add GitHub Actions CI pipeline for backend tests
[AI][SDLC]      Update Doctor to validate integration env vars
[AI][DOCS]      Document deployment procedure for staging environment
[AI][FULLSTACK] Add work item list view with Plane sync   ← legacy; prefer epic + BACKEND + FRONTEND children
```

---

## Procedure

### Step 1 — Load context

Read in order:
1. `.sdlc/sdlc.yaml`
2. `.sdlc/memory/architecture.md`
3. `.sdlc/memory/business-rules.md`

Record the current SDLC stage (ticket or requirements) and the next stage (architecture).

### Step 2 — Determine the task name

Apply the `[AI][TYPE]` convention. If the change spans multiple types, choose the primary one and note the secondary in the story.

### Step 3 — Write the story

The story is the most important section. It must answer three questions in plain prose (2–4 short paragraphs):

1. **Current situation** — what exists today and what is the problem or gap?
2. **Why it matters** — what breaks, degrades, or stays blocked without this change?
3. **What this feature does** — how it solves the problem, where it lives, and what changes for users or agents?

Do not describe implementation details in the story. Describe outcomes and context.

### Step 4 — Define scope and non-goals

Scope: bullet list of what will be built.
Non-goals: bullet list of what will explicitly NOT be built in this task. At least 3 non-goals.

### Step 5 — List assumptions

Table with columns: `Assumption | Confidence | Impact if wrong`

Confidence values:
- `high` — safe to proceed; unlikely to change
- `medium` — Architecture gate is blocking until confirmed
- `low` — requires stakeholder clarification before proceeding

### Step 6 — List risks

Table with columns: `Risk | Likelihood | Impact | Mitigation`

Every risk must have a real mitigation — not just "we'll handle it" but a specific action or accepted trade-off.

### Step 7 — List impacted areas

File tree showing which files will be created or modified, with a short `← comment` on each.

### Step 8 — Write acceptance criteria

Numbered list. Each criterion must be verifiable without ambiguity:
- HTTP status codes for API behavior
- Visual state for UI behavior
- File existence or command exit code for infrastructure
- Never: "it should work correctly", "the user can see it", "it behaves as expected"

Minimum: 4 criteria. Maximum: 10 (split into sub-tasks if more are needed).

### Step 9 — Write the Definition of Done (DoD)

Checkbox list. This is what the Reviewer checks before approving the PR.

Every DoD must include:

- [ ] Architecture gate passed (ADR written if framework or significant decision was made)
- [ ] All unit tests pass locally
- [ ] `make sdlc-doctor` exits `0`
- [ ] Relevant docs updated
- [ ] No secrets in code or diff
- [ ] PR reviewed and approved (human or Reviewer agent)
- [ ] Handoff summary updated in `docs/handoff/current-state.md`

Add task-specific items between the unit tests and the Doctor check.

### Step 10 — Write the task breakdown

Numbered checklist. Each sub-task follows the same `[AI][TYPE]` naming convention with a `PROJECT-N` placeholder.

### Step 11 — State the next step

Single paragraph addressed to the Architect (or the next agent in the lifecycle). State exactly what must be decided or confirmed before implementation can start.

---

## Delivery

Persist the plan on the **Plane work item** via `.cursor/skills/plane-sdlc/SKILL.md`. Do not write `specs/` or local ticket files.

## Outputs

1. **Task name** — `[AI][TYPE] Short imperative title`
2. **Story** — 2–4 paragraphs explaining context and purpose
3. **Scope** — bullet list of what will be built
4. **Non-goals** — bullet list of what will not be built (min 3)
5. **Assumptions** — table with confidence levels
6. **Risks** — table with real mitigations
7. **Impacted areas** — annotated file tree
8. **Acceptance criteria** — numbered, verifiable list (min 4)
9. **Definition of Done** — checkbox list for the Reviewer
10. **Task breakdown** — sub-tasks with `[AI][TYPE]` names
11. **Next step** — addressed to the Architect

---

## Validation Checklist

Before delivering the plan, verify:

- [ ] Task name follows `[AI][TYPE] Short title` format
- [ ] Story answers: current situation, why it matters, what this does
- [ ] At least 3 non-goals listed
- [ ] Every assumption has a confidence level
- [ ] Every risk has a specific mitigation or accepted reason
- [ ] Every acceptance criterion is verifiable (HTTP code, exit code, observable state)
- [ ] DoD includes: tests pass, Doctor exits 0, docs updated, no secrets, PR reviewed
- [ ] No code written or proposed — this is planning only
- [ ] Next step is addressed to the Architect, not vague

---

## Failure Modes

| Failure | Response |
|---------|----------|
| Vague request ("make it better", "fix the bug") | Ask for: what is the current behavior, what is the expected behavior, and what is the impact of not fixing it |
| Missing acceptance criteria | Do not proceed — ask for at least one verifiable expected outcome before writing the plan |
| Scope too broad (more than ~7 sub-tasks) | Split into two plans; deliver the first increment only |
| `medium` confidence assumption that blocks everything | Escalate to Architect immediately; do not write a plan around an unconfirmed assumption |
| All assumptions are `high` confidence | Review again — at least one assumption is almost always medium or unknown at ticket stage |

---

## Reference Example

See `.sdlc/templates/planner/example-sdlc-plan.md` for a complete, annotated example of this skill applied to a real feature.
