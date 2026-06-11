# Skill: E2E Testing

## Purpose

Validate the system end-to-end using a headless browser (Playwright), ensuring critical user flows work with integrated frontend and backend, before any PR is merged.

## When to use

- On every PR that modifies `app/frontend/` or `app/backend/` endpoints
- As mandatory QA gate for UI flows
- After unit and integration tests pass

## Required inputs

- Full stack running (use `container-validation.md` first)
- `app/frontend/e2e/` — Playwright test files
- Application `BASE_URL` (e.g. `http://localhost:3000`)

## Procedure

```bash
# 1. Ensure stack is running
docker compose -f app/infra/docker-compose.yml up -d
sleep 15

# 2. Install Playwright (if not installed)
cd app/frontend
npx playwright install --with-deps chromium

# 3. Run E2E tests
BASE_URL=http://localhost:3000 npx playwright test \
  --reporter=json \
  --output=test-results/ \
  2>&1 | tee e2e-results.log

# 4. Capture failure artifacts
# Playwright auto-saves screenshots + videos in test-results/ for failed tests

# 5. Teardown
docker compose down -v
```

## Minimum coverage criteria

| Flow | Test type |
|-------|--------------|
| Login / logout | Authentication |
| Main domain CRUD | Core functionality |
| Form with validation | Inputs |
| Listing + pagination | Data display |
| API error (mock 500) | Resilience |
| Authenticated redirect | Navigation |

## Outputs

- JSON with result per test (pass/fail/flaky)
- Screenshots and videos of failed tests
- Success rate: N/M tests passing
- Exit code: 0 (all passed) or 1 (any non-flaky failure)

## Validation checklist

- [ ] All critical flows have E2E coverage
- [ ] Tests do not depend on external data — use controlled seeds
- [ ] Tests are deterministic — no arbitrary `sleep`
- [ ] Screenshots saved for failed tests
- [ ] Flakiness rate < 5%

## Failure modes

| Failure | Common cause | Action |
|-------|-------------|------|
| Element timeout | Slow UI or missing element | Improve selectors; verify component exists |
| Route 404 | Broken frontend routing | Report to Implementer |
| API error 500 during test | Backend bug exposed by E2E | Report to QA as unmet acceptance criterion |
| Flaky test | UI race condition | Use `waitForSelector` + `expect.poll` |
