# Skill: Performance Testing

## Purpose

Detect performance regressions before deploy, measuring latency, throughput, and resource usage under realistic load, using k6 as the primary tool.

## When to use

- On PRs affecting high-frequency endpoints or database queries
- Before any production deploy
- After database schema or index changes
- After adding/modifying Redis cache

## Required inputs

- Stack running in test environment (use `container-validation.md`)
- `app/backend/tests/performance/` — k6 scripts
- Previous performance baselines (in `.sdlc/memory/`)

## Procedure

```bash
# 1. Install k6
brew install k6
# or: docker pull grafana/k6

# 2. Run load test
k6 run \
  --out json=k6-results.json \
  --vus 10 \
  --duration 30s \
  app/backend/tests/performance/load-test.js

# 3. Smoke test (1 VU, 1 min) to detect basic errors
k6 run --vus 1 --duration 60s \
  app/backend/tests/performance/smoke-test.js

# 4. Compare with baseline
python3 .sdlc/dsl/perf_compare.py \
  --current k6-results.json \
  --baseline .sdlc/memory/perf-baseline.json \
  --threshold 20  # acceptable regression %
```

## Baseline thresholds (default)

| Metric | Alert threshold | Block threshold |
|---------|--------------------|-----------------------|
| p95 latency | > 200ms (+20% from baseline) | > 500ms |
| p99 latency | > 500ms (+30% from baseline) | > 2000ms |
| Error rate | > 0.1% | > 1% |
| Throughput | < 80% of baseline | < 60% of baseline |
| Average CPU usage | > 70% | > 90% |

## k6 script template

```javascript
// app/backend/tests/performance/load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('error_rate');

export const options = {
  vus: 10,
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(95)<200'],
    error_rate: ['rate<0.01'],
  },
};

export default function () {
  const res = http.get(`${__ENV.BASE_URL}/api/v1/investments`);
  check(res, { 'status 200': (r) => r.status === 200 });
  errorRate.add(res.status !== 200);
  sleep(1);
}
```

## Outputs

- `k6-results.json` with full metrics
- Comparison report with baseline (% change per metric)
- Exit code: 0 (within thresholds) or 1 (regression detected)

## Validation checklist

- [ ] Smoke test passes without errors
- [ ] p95 within threshold
- [ ] Error rate < 0.1%
- [ ] No N+1 queries detected (via OTel traces)
- [ ] Redis hit rate > 80% for cached endpoints

## Failure modes

| Failure | Common cause | Action |
|-------|-------------|------|
| Latency regression | Query without index | Report to Implementer + suggest `EXPLAIN ANALYZE` |
| High error rate | Endpoint bug | Report to QA as unmet acceptance criterion |
| Low throughput | Database lock | Review transactions with Architect |
| Degradation with Redis | High cache miss | Verify TTL and cache invalidation |
