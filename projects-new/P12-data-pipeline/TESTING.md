# Testing

## Automated
- `make lint` – black, ruff, and mypy across DAGs and plugins.
- `make unit` – pytest with Airflow DAG parsing and operator unit tests using `airflow.models.DagBag`.
- `make integration` – spins docker-compose, seeds sample data, and runs `airflow dags test etl_curated_daily 2024-01-01`.
- `make expectations` – executes Great Expectations checkpoints under `great_expectations/checkpoints/`.

## Manual validation
- `python scripts/validate_partitions.py --bucket <bucket>` ensures curated parquet partitions and schema compatibility.
- Review OpenLineage events with `scripts/inspect_lineage.py --dag-id etl_curated_daily` to confirm downstream visibility.
