# Testing
- **Unit**: schema validators and helpers; run `pytest docker/tests/unit`.
- **Contract**: OpenAPI-driven schema validation using `schemathesis`; cases stored in `docker/tests/contracts`.
- **Integration**: Compose brings up mock API + runner; check end-to-end response codes and latency.
- **Load**: Locust profiles with 50 RPS baseline to guard against regressions.

## Key scenarios
- 200 OK with valid payload
- 422 validation errors with missing required fields
- Idempotent POST with `Idempotency-Key` header
- Rate-limit behavior at threshold
