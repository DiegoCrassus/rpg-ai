# Skill: Container Validation

## Purpose

Verify Docker build and `docker compose up` pass before any PR is merged, ensuring the full stack starts correctly in the CI environment.

## When to use

- After any change to `Dockerfile*`, `docker-compose*.yml`, `pyproject.toml`, `requirements.txt`, `package.json`
- As mandatory CI gate after unit tests and before integration tests

## Required inputs

- `app/infra/docker-compose.yml` (or `docker-compose.dev.yml`)
- Dockerfiles for each service
- `.env.example` (required variables)

## Procedure

```bash
# 1. Validate Dockerfile syntax (without build)
docker build --check -f app/infra/docker/Dockerfile.backend .
docker build --check -f app/infra/docker/Dockerfile.frontend .

# 2. Full build of each image
docker compose -f app/infra/docker-compose.yml build --no-cache 2>&1 | tee build.log
BUILD_EXIT=$?

# 3. If build passed, start stack
if [ $BUILD_EXIT -eq 0 ]; then
  docker compose -f app/infra/docker-compose.yml up -d
  sleep 10  # wait for services to become healthy

  # 4. Health checks per service
  docker compose ps --format json | python3 -c "
import json, sys
services = [json.loads(l) for l in sys.stdin]
failed = [s for s in services if s.get('Health') not in ('healthy', '')]
if failed:
    print('FAIL:', [s['Service'] for s in failed])
    sys.exit(1)
print('PASS: all services healthy')
"

  # 5. Teardown
  docker compose -f app/infra/docker-compose.yml down -v
fi

exit $BUILD_EXIT
```

## Outputs

- Build log (stdout + stderr)
- Health status per container
- Exit code: 0 (all healthy) or 1 (any failure)

## Validation checklist

- [ ] `docker build` passed without errors for each image
- [ ] No `docker compose up` service stayed `unhealthy` for more than 30s
- [ ] Backend `/health` returns 200 after `up`
- [ ] PostgreSQL accepts connection after `up`
- [ ] Redis accepts `PING` after `up`
- [ ] No secrets hardcoded in images (verify with `docker inspect`)

## Failure modes

| Failure | Common cause | Action |
|-------|-------------|------|
| Build error | Missing dependency in Dockerfile | Report to Implementer |
| Container unhealthy | Missing env var | Check `.env.example` and report to DevOps |
| Port conflict | Port already in use on CI | Use alternate ports in docker-compose.ci.yml |
| Build timeout | Invalid layer cache or slow base image | Optimize Dockerfile with multi-stage build |
