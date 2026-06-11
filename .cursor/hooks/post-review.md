# Hook: Post-Review

## Purpose

Record the review decision, capture required fixes, and update handoff if needed.

## When to Execute

After completing a code review.

## Procedure

### 1. Record the Review Decision

Document:
- Decision: APPROVE | REQUEST CHANGES | ESCALATE
- Reason for the decision
- Date and reviewer identity

### 2. Capture Required Fixes (if REQUEST CHANGES)

For each required change:
- What must be fixed
- Why it must be fixed (correctness, security, quality)
- Priority: blocking | non-blocking

Do not mark a fix as non-blocking if it involves a security issue or failing test.

### 3. Capture Risk Notes

Even for APPROVE decisions, record:
- Known risks accepted
- Deferred items for future work
- Assumptions made during review

### 4. Update Handoff If This Is a Stage Transition

If the review is the final gate before deployment or a major transition:
- Update `docs/handoff/current-state.md`
- Record what was approved, what risks were accepted, and what the next step is

### 5. Notify Next Agent

If APPROVE:
- Notify DevOps for deployment, or Implementer to merge
- State any post-merge observability steps

If REQUEST CHANGES:
- Notify Implementer with the required changes list
- Set expectation for re-review

If ESCALATE:
- Document the escalation reason
- Identify who needs to resolve it

## Output of This Hook

A post-review summary:
```
Decision: APPROVE | REQUEST CHANGES | ESCALATE
Risk notes: <list or none>
Required fixes: <list or "none">
Handoff updated: yes | no
Next step: <description>
```
