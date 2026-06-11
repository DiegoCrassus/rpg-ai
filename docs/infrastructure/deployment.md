# Deployment

## Current Status

**Phase:** Not ready — no deployable services yet.

This document will be updated when the first deployable component is implemented.

## Deployment Principles

1. Every deployment has a documented rollback procedure.
2. Environment variables are verified before deployment.
3. Observability signals are confirmed after deployment.
4. No manual changes to production — all through CI/CD or IaC.

## Target Environments

| Environment | Target         | Status     |
|-------------|----------------|------------|
| local       | Developer machine | active  |
| dev         | TBD            | not ready  |
| production  | TBD            | not ready  |

## Deployment Procedure (Template)

When a deployable service exists, the procedure will follow this pattern:

### Pre-Deployment Checklist

- [ ] PR approved and merged
- [ ] CI pipeline passed
- [ ] Environment variables verified
- [ ] Rollback plan documented
- [ ] Observability checklist prepared

### Deployment Steps

```bash
# TBD — will be documented when services exist
```

### Post-Deployment Checklist

- [ ] Service health check passed
- [ ] Key metrics appearing
- [ ] No error spike in logs
- [ ] Rollback tested or confirmed available

## Rollback Procedure (Template)

```bash
# TBD — will be documented when services exist
```

## CI/CD Pipeline

Not yet configured. Will use GitHub Actions when backend/frontend services are defined.
See `.sdlc/integrations/services.yaml` for integration roles and environment variables.
