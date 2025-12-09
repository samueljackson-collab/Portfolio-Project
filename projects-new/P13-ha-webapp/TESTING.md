# Testing

## Automated
- `make lint` – ruff and hadolint across app and NGINX configs.
- `make unit` – pytest for service layer; uses sqlite to mock DB interactions.
- `make integration` – brings stack up and runs `scripts/failover_validation.sh` to ensure reads/writes survive leader change.
- `k6 run tests/synthetic.js` – stress test verifying p95 < 300ms during replica promotion.

## Manual validation
- None at this time.
