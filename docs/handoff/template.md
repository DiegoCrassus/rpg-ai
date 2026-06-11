# Handoff Template

Use this template when completing a stage transition or a significant work unit.

---

## Handoff: <title>

- **Date:** YYYY-MM-DD
- **Stage Completed:** <stage id from lifecycle.yaml>
- **Next Stage:** <stage id>
- **Author:** <agent name or human>

### What Changed

| File / Component | What was done |
|-----------------|---------------|
| `<file>`        | <change>      |

### Why It Changed

<Business or technical reason. Link to ticket or requirement.>

### Validation Evidence

| Criterion | Status | Evidence |
|-----------|--------|----------|
| <criterion 1> | PASS / FAIL / NOT TESTED | <test output or link> |

**Doctor result:**
```
[PASS / FAIL] Doctor summary: N passed, N warnings, N failed
```

### Known Risks

| Risk | Severity | Mitigation / Accepted reason |
|------|----------|------------------------------|
| <risk> | high / medium / low | <mitigation> |

### Open Questions

- <question 1>

### Next Steps

1. <next action with responsible agent or human>
2. <next action>

### Rollback

<How to revert this change if something goes wrong. "N/A" only if the change is truly non-reversible and that is documented.>

---

*Use this template by copying it to `docs/handoff/current-state.md` and filling in all sections.*
