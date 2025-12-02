# Standard Operating Procedures — P09

## Daily Checks
- Confirm `/readyz` returns 200 and includes DB connectivity flag.
- Review Grafana latency and error panels; ensure error rate <1%.
- Rotate app secrets monthly; update `.env` and k8s secrets.

## Change Management
- Any API change requires schema update in `src/schemas.py` and contract tests.
- Container images built with `make build-image` and scanned before deployment.

## Backup and Retention
- SQLite demo DB backed up nightly to `artifacts/backups/` during CI runs.
- Logs rotated via `jobs/rotate_logs.py` weekly.
