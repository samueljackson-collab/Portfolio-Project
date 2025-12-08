# Testing

## Automated
- `make lint` – ruff + mypy over `src/` and `scripts/`.
- `make unit` – pytest with moto to stub DynamoDB and EventBridge calls.
- `make contract` – spins API locally via `sam local start-api` and validates OpenAPI examples with `schemathesis`.
- `make load` – runs `scripts/load_test.py` using k6 thresholds (p95 < 200ms, <1% errors).

## Manual validation
- Invoke `./scripts/verify_tracing.sh` to confirm X-Ray segment annotations for request IDs and user claims.
- Use `aws dynamodb scan` against the dev table to verify conditional writes prevent duplicate keys.
