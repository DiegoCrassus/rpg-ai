# Maintenance

## Current Status

No running services. Maintenance procedures will be defined when services are deployed.

## Maintenance Categories

### Dependency Updates

- Review dependency updates monthly (or via Dependabot when CI is configured).
- Test updates in a branch before merging to main.
- Document breaking changes in ADRs if the update requires code changes.

```bash
# Check outdated packages
pip list --outdated

# Update and test
pip install --upgrade <package>
python -m pytest app/ -v
```

### Database Maintenance

- **Migrations:** All schema changes via migration files in `app/backend/migrations/` (TBD).
- **Backups:** TBD when production database is configured.
- **Vacuum/cleanup:** TBD per Supabase maintenance schedule.

### Log Rotation

- TBD when logging infrastructure is configured.
- Default: rotate daily, retain 30 days in dev, 90 days in production.

### Security Patches

- Apply critical security patches immediately (same-day if possible).
- Document in incident log if a security patch is emergency-deployed.
- Rotate credentials if any exposure is suspected.

### Autonomous Maintenance Tasks (AI-Assisted)

The following tasks can be delegated to the Cursor agent:
- Run `make sdlc-doctor` and report failures
- Check for stale docs (docs older than 90 days without update)
- Identify unused dependencies
- Flag test coverage drops

These are advisory — human confirmation required before any action.

## Maintenance Runbook Template

```markdown
## Runbook: <task name>

- **Frequency:** daily | weekly | monthly | on-demand
- **Owner:** <agent or human>
- **Last run:** YYYY-MM-DD

### Steps
1. <step>
2. <step>

### Expected output
<what success looks like>

### On failure
<what to do if it fails>
```
