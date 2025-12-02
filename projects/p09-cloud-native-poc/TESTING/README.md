# Testing Strategy — P09

## Pyramid
- **Unit:** FastAPI routers, pydantic models, worker retry logic.
- **Integration:** API + DB using sqlite fixture; worker consumes queue.
- **E2E:** Docker-compose smoke test hitting `/items` CRUD and `/metrics`.
- **Security:** Dependency check (`pip-audit`), container scan stub.

## Commands
```bash
make lint
make test-unit
make test-integration
make test-e2e
docker compose -f docker/compose.poc.yaml run api pytest -q
```

## Test Cases
- Create/read/update/delete item round trip.
- Health endpoints return 200 and readiness validates DB connectivity.
- Worker retries on transient error and records metrics.
- Metrics endpoint exposes `p09_request_latency_seconds` histogram.

## Reporting
- Coverage XML at `reports/coverage.xml`.
- JUnit XML at `reports/junit.xml`.
- Perf snapshot saved to `reports/perf.json` from e2e run.
