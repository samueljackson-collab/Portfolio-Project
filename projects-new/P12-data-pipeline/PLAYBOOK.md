# Operations Playbook

## Deployments
- Local dev: `make up` to start Airflow stack; apply DB migrations via `make init` on first boot.
- QA/Prod: Build image `make image` and push to ECR, then update Helm release `helm upgrade airflow charts/airflow -f values/<env>.yaml`.

## Daily operations
- Monitor DAG SLA misses and task duration trends in Grafana dashboard `airflow-pipeline`.
- Rotate SFTP credentials via `scripts/rotate_sftp_keys.sh` and update Airflow connections.
- Archive quarantine datasets weekly to Glacier and refresh Data Docs for audit trails.

## Run/validate
- `airflow dags list` and `airflow tasks states-for-dag-run etl_curated_daily` to confirm health.
- `python scripts/backfill_window.py --start 2024-01-01 --end 2024-01-07` when replaying historical data.
