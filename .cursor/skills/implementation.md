# Skill: Implementation

## Purpose

Produce focused, reversible, well-tested code changes that satisfy acceptance criteria without exceeding scope.

## When to Use

- At the Implementation stage
- When applying an Auto Fix from an incident
- When executing deployment tasks

## Required Inputs

- Approved architecture notes
- Acceptance criteria from ticket/requirements
- Relevant existing code
- Test conventions for the project

## Procedure

1. **Confirm scope** — Re-read the plan and acceptance criteria before touching any file.
2. **Identify the minimal change** — What is the smallest diff that satisfies the criteria?
3. **Write tests first (when possible)** — Define what passing looks like before implementing.
4. **Implement incrementally** — Make one logical change at a time.
5. **Self-review** — Check the diff against the scope, quality rules, and acceptance criteria.
6. **Run tests** — Execute and record real output.
7. **Update docs if needed** — Interfaces, architecture, infrastructure.

## Outputs

- Code changes (focused diff)
- Test additions or updates
- Updated docs (if applicable)
- Test execution results (real output)

## Validation Checklist

- [ ] Tests written for all new logic
- [ ] Tests pass (actual run, not assumed)
- [ ] No unrelated files modified
- [ ] No commented-out code committed
- [ ] No `print` statements in library code
- [ ] Type hints on all new public functions (Python)
- [ ] Docs updated if public interfaces or architecture changed

## Failure Modes

- **Tests fail** — Fix the implementation; do not modify assertions to pass
- **Scope creep** — Stop and reduce scope; document the remainder as a follow-up task
- **Missing tests** — Add tests before requesting review
- **Broad rewrite** — If more than expected files are changing, stop and consult the plan
