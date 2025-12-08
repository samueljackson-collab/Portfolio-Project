# Runbooks

## DAG failure escalation
1. Check Airflow UI for failing task; download log for context.
2. Run `python scripts/replay_task.py --dag-id <dag> --task-id <task> --execution-date <date>` to retry with trace.
3. If data quality failure, inspect quarantine folder and adjust validation suite; re-trigger DAG via `airflow dags trigger`.

## Metadata DB outage
1. Verify Postgres container health: `docker ps | grep airflow-postgres`.
2. Restore from latest backup: `scripts/restore_metadata.sh --backup-file backups/postgres/latest.dump`.
3. Run `airflow db upgrade` and restart scheduler/webserver containers.

## Staging S3 pollution
1. Run `scripts/cleanup_staging.sh --older-than 3d` to purge stale files.
2. Validate curated partitions with `python scripts/validate_partitions.py` and ensure Data Docs regenerated.
3. Record incident notes in `docs/incidents/YYYY-MM-DD.md`.
