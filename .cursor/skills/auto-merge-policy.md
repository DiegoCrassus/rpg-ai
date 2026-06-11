# Skill: Auto-Merge Policy

## Purpose

Define the exact criteria that allow automatic PR merge without human intervention, ensuring AI autonomy is exercised only when all quality gates are met.

## When to use

- When configuring a new repository
- When reviewing whether a PR is eligible for auto-merge
- As reference for DevOps deciding whether to merge automatically

## Auto-merge criteria (ALL must be true)

### Mandatory gates

| Gate | Check | Required status |
|------|-------|-----------------|
| Doctor | `make sdlc-doctor` | exit code 0 |
| Unit tests | `pytest` or `npm test` | 100% passing |
| Integration tests | `pytest -m integration` | 100% passing |
| Container | `docker compose up` | all healthy |
| Migrations | `alembic upgrade head` | no errors |
| Security scan | `gitleaks + bandit + npm audit` | 0 HIGH/CRITICAL |
| Secrets check | `gitleaks detect` | 0 findings |
| Reviewer | Agent Reviewer decision | APPROVE |
| Doctor orphan branches | Doctor check | No orphan branches |
| Branch naming | Follows branch-naming.md | Validated |

### Conditional gates (when relevant)

| Condition | Additional gate |
|----------|----------------|
| PR modifies `app/frontend/` | E2E tests passing |
| PR modifies API endpoints | ContractValidator synchronized |
| PR modifies `app/backend/migrations/` | MigrationRunner reversible |
| PR modifies performance-critical files | Performance thresholds within baseline |
| PR modifies `Dockerfile*` | Container build without security warnings |

### BLOCKING criteria (any one prevents auto-merge)

| Blocker | Reason |
|----------|--------|
| Change in `app/backend/auth/` | Authentication requires human review |
| Change in authorization/permissions logic | Critical security |
| Change in production database configuration | Data loss risk |
| Change in production environment variables | Operational impact |
| Security scan with CRITICAL or HIGH | Known vulnerability |
| Diff > 500 lines | Scope too large for reliable autonomous review |
| Reviewer issued ESCALATE | Requires explicit human judgment |

## Verification procedure

```python
# DevOps runs before merge
def can_auto_merge(pr) -> tuple[bool, list[str]]:
    blockers = []

    # Mandatory gates
    if pr.doctor_exit_code != 0:
        blockers.append("Doctor failed")
    if pr.tests_passing < pr.tests_total:
        blockers.append(f"Tests: {pr.tests_passing}/{pr.tests_total}")
    if pr.security_scan_level in ("CRITICAL", "HIGH"):
        blockers.append(f"Security: {pr.security_scan_level} found")
    if pr.reviewer_decision != "APPROVE":
        blockers.append(f"Reviewer: {pr.reviewer_decision}")
    if pr.diff_lines > 500:
        blockers.append(f"Diff too large: {pr.diff_lines} lines")

    # Area-based blockers
    if any(f in pr.changed_files for f in ["auth/", "permissions/", "prod.env"]):
        blockers.append("Critical file changed — requires human review")

    return len(blockers) == 0, blockers
```

## Reviewer confidence score (for auto-APPROVE)

Reviewer may issue autonomous APPROVE if confidence score ≥ 0.95:

```
score = 1.0
- Doctor failed:              score -= 0.5
- Test failed:                score -= 0.4
- Security HIGH:              score -= 0.6
- Security MEDIUM:            score -= 0.2
- Diff > 200 lines:           score -= 0.1
- Diff > 500 lines:           score -= 0.3
- Change in auth:             score = 0 (forces human escalation)
- ContractValidator diverged: score -= 0.3
- Performance regressed:      score -= 0.2

If score < 0.95: REQUEST_CHANGES or ESCALATE
If score >= 0.95: automatic APPROVE
```

## Validation checklist

- [ ] All mandatory gates are green
- [ ] No blocking criterion active
- [ ] Confidence score ≥ 0.95
- [ ] Plane card in **In Progress** during implementation
- [ ] Plane card linked to PR
- [ ] **Merge executed by agent** via `.sdlc/scripts/auto_merge_pr.py` — do not wait for human

## Autonomous merge (default)

When all gates pass, **DevOps/Orchestrator MUST run**:

```bash
python3 .sdlc/scripts/auto_merge_pr.py --pr <N> --card RPG-N --plane-comment
```

Human merge in GitHub UI is **exception only** (ESCALATE, auth changes, policy block).

## Outputs

- Decision: CAN_MERGE or BLOCKED
- List of blockers (if any)
- Calculated confidence score
- Record in Observer (auto-merge metrics)
