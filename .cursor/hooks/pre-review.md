# Hook: Pre-Review

## Purpose

Collect changed files, identify risk areas, and verify validation evidence before starting a review.

## When to Execute

Before starting a PR or code review.

## Procedure

### 1. Collect Changed Files

List all files in the diff:
- New files
- Modified files
- Deleted files

### 2. Load Review Context

- Read the original plan or ticket for this change.
- Confirm acceptance criteria are available.
- Load `.sdlc/stages/definitions.yaml` for the review stage gates.

### 3. Identify Risk Areas

For each changed file, assess:
- **Security risk** — Authentication, authorization, data access, external input?
- **Data risk** — Database schema, migrations, data transformations?
- **Performance risk** — Hot paths, queries, loops?
- **Dependency risk** — New external dependencies?
- **Scope risk** — Files changed that are outside the expected scope?

### 4. Verify Validation Evidence

Confirm:
- [ ] Test results are available (real output, not claimed)
- [ ] Each acceptance criterion is mapped to test evidence
- [ ] Doctor was run and passed (if structure changed)
- [ ] QA notes exist

### 5. Flag Missing Evidence

If validation evidence is missing:
- Do not proceed with review
- Request the evidence from QA/Implementer
- Document what is missing

## Output of This Hook

A pre-review context:
```
Files in diff: <count and list>
Risk areas identified: <list>
Validation evidence available: yes | partial | no
Missing evidence: <list or none>
Ready to review: yes | no (reason)
```
