# Skill: Observability

## Purpose

Define and verify logs, metrics, traces, and alerts that allow the system to be understood and debugged in production.

## When to Use

- At the Observability stage (after deployment)
- When implementing a new service or component
- When diagnosing an incident

## Required Inputs

- Deployed component or service description
- `docs/operations/observability.md`
- `.sdlc/memory/operational-context.md`

## Procedure

1. **Identify critical paths** — What user-facing operations must be traced?
2. **Define log events** — What must be logged at each step?
   - Error: always
   - Warning: recoverable failures and unexpected states
   - Info: significant business events (request received, job completed)
   - Debug: detailed diagnostic info (not for production by default)
3. **Define metrics** — What numbers matter?
   - Request rate, error rate, latency (RED)
   - Business-specific metrics
4. **Define traces** — What distributed paths need end-to-end tracing?
5. **Define alerts** — What conditions require immediate notification?
6. **Verify signals** — After deployment, confirm signals appear as expected.

## Outputs

- Log coverage notes
- Metric definitions (name, type, labels)
- Trace path descriptions
- Alert definitions (condition, severity, receiver)
- Observability checklist (completed)

## Validation Checklist

- [ ] Error logging confirmed at all failure points
- [ ] At least one business-level metric defined
- [ ] Critical path has distributed trace coverage
- [ ] Alert defined for service-down or error-rate spike
- [ ] Signals verified in actual environment (or marked as pending)

## Failure Modes

- **No error logging** — Every error path must produce a log event with context
- **Undefined metrics** — "We'll add metrics later" is not acceptable; define at least the basics now
- **Missing alerts** — Silent failures are worse than noisy ones
- **Unverified signals** — Mark as "pending verification" if not confirmed; do not claim signals work
