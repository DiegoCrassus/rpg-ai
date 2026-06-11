# Incident Response

## Current Status

No incidents recorded. Repository is in initialization phase.

## Severity Levels

| Level    | Definition                                        | Response Time |
|----------|---------------------------------------------------|---------------|
| critical | Production down or data loss                      | Immediate     |
| high     | Major feature unavailable or severe degradation   | < 1 hour      |
| medium   | Minor feature degraded, workaround exists         | < 4 hours     |
| low      | Cosmetic or non-blocking issue                    | Next sprint   |

## Incident Response Workflow

### 1. Detect

Sources: alert, user report, monitoring, CI failure.
Record: initial observation in `.sdlc/memory/incidents.md`.

### 2. Assess

- What is affected?
- What is the severity?
- Is it a production incident?

### 3. Communicate

For critical/high severity:
- Notify team immediately (Slack or email — see `.sdlc/integrations/services.yaml`)
- Set status page if applicable

### 4. Mitigate

Stabilize the system. This is NOT the fix — it is the stop-the-bleeding step:
- Rollback if a recent deployment caused it
- Disable the affected feature if possible
- Scale up if it is a capacity issue

### 5. Investigate

- Collect logs, traces, and metrics
- Identify root cause
- Document findings in `.sdlc/memory/incidents.md`

### 6. Fix

- Use the **Auto Fix** SDLC stage for structured remediation
- All fixes follow the normal SDLC lifecycle (plan → implement → validate → review)
- Emergency fixes are still documented and reviewed post-hoc

### 7. Post-Mortem

Required for critical and high severity incidents:
- Root cause
- Timeline
- Mitigation actions
- Prevention measures
- Action items with owners and due dates

Post-mortem document goes in `.sdlc/memory/incidents.md`.

## Incident Record Format

See `.sdlc/memory/incidents.md` for the incident log template.

## On-Call

Not yet defined — will be configured when services are deployed.
