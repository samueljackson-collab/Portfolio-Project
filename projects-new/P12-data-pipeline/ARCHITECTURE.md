# Architecture

Airflow runs in docker-compose with a Celery executor. Postgres stores metadata, Redis handles queues, and S3 buckets back staging/curated layers. Each DAG task pulls data from source connectors, validates via Great Expectations, transforms using Pandas, and writes parquet with partitioned layouts.

## Flow
1. `extract` pulls batch files from SFTP/HTTP and uploads to `s3://<bucket>/staging/date=*/`.
2. `validate` executes Great Expectations suites; failed rows are parked in `quarantine/` with Data Docs artifacts.
3. `transform` aggregates and enriches data, writing to `curated/` with Iceberg-compatible schemas.
4. `publish` notifies downstream consumers through SNS and records lineage to OpenLineage backend.

## Dependencies
- Docker Compose with Airflow 2.8+, Postgres, Redis.
- `great_expectations`, `pandas`, `boto3`, `openlineage-airflow`.
- AWS credentials for S3 access; optional MinIO profile for local runs.
