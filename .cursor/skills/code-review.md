# Skill: Code Review

## Purpose

Review code changes for correctness, security, maintainability, testability, and SDLC alignment.

## When to Use

- At the PR & Review stage
- When reviewing an auto-fix before merge
- When reviewing architecture implementation against the plan

## Required Inputs

- PR diff or changed file list
- Original plan and acceptance criteria
- Validation evidence from QA stage

## Procedure

1. **Understand the intent** — Read the plan and acceptance criteria.
2. **Check structural compliance** — Only in-scope files changed?
3. **Check correctness** — Does the diff satisfy the criteria?
4. **Check security** — No secrets, injection risks, or unsafe patterns?
5. **Check quality** — Tests, type hints, no dead code?
6. **Check SDLC alignment** — Docs updated, Doctor passed?
7. **Produce review decision** — APPROVE, REQUEST CHANGES, or ESCALATE.

## Outputs

- Review decision (APPROVE | REQUEST CHANGES | ESCALATE)
- Risk notes
- Required changes list (if REQUEST CHANGES)
- Deferred items

## Validation Checklist

- [ ] No secrets in diff
- [ ] Tests exist for new logic
- [ ] Acceptance criteria met
- [ ] Docs updated if required
- [ ] Doctor passed
- [ ] No broad scope creep

## Failure Modes

- **Rubber-stamping** — Never approve without checking; read the diff
- **Missing security check** — Always scan for secrets, input handling, and injection
- **Ignoring test gaps** — Missing tests are a required change, not a suggestion
- **Approving failing Doctor** — Never approve if Doctor fails on required checks
