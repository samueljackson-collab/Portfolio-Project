# Testing Strategy — P08

## Suite Composition
- **Smoke:** CRUD happy paths for `/users`, `/orders`, `/payments` using sandbox data.
- **Regression:** Negative cases, pagination, auth failures, idempotency tokens.
- **Contract:** JSON schema validation per endpoint stored in `tests/schemas/`.
- **Performance spot checks:** Lightweight latency benchmarks via Newman `--reporters cli,json --reporter-json-export reports/perf.json`.

## Commands
```bash
make lint
make test # runs newman with default environment
make test-contract ENV=staging
make test-perf BASE_URL=https://api.example.dev
```

## Test Data
- `tests/data/users.csv` for user creation payloads.
- `tests/data/orders.json` for order flows.
- `tests/data/auth_tokens.example.json` describes token shapes without secrets.

## Quality Gates
- All requests must assert on status code, response time (<500ms), and schema.
- Fail build if new endpoints missing schema file.
- Coverage tracked via endpoint checklist in `reports/coverage-matrix.md`.
