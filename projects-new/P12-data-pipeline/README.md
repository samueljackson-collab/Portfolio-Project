# P12 – Airflow Data Pipeline

Containerized Apache Airflow orchestrates daily ETL jobs ingesting CSV/JSON payloads, normalizing with Pandas, and landing curated parquet files in S3. DAGs emphasize idempotency, schema validation, and lineage capture through OpenLineage.

## Quick start
1. Build stack: `make build && make up` to start Airflow + Postgres + Redis via docker-compose.
2. Initialize connections: `airflow connections import config/connections.yaml`.
3. Load sample data: `python scripts/load_sample_data.py --bucket airflow-demo`.
4. Trigger DAG: `airflow dags trigger etl_curated_daily` and watch logs via the UI.
5. Export lineage: `python scripts/export_lineage.py --dag-id etl_curated_daily`.

## Components
- `dags/etl_curated_daily.py`: staging -> validation -> transform -> publish tasks.
- `plugins/operators/validation.py`: Great Expectations wrapper enforcing column contracts.
- `config/airflow_settings.yaml`: pools/variables tuned for parallel ingestion.
