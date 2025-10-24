# Big Data ETL Job with PySpark

## Overview
PySpark job orchestrated via Apache Airflow or AWS Glue to process large-scale task analytics. Implements extract-transform-load pipeline from Kafka/S3 into curated data lake and warehouse.

## Pipeline Steps
1. **Ingest** – Consume raw events from Kafka or load S3 Parquet files.
2. **Transform** – Apply schema enforcement, deduplication, enrichment with user metadata.
3. **Aggregate** – Compute KPIs (completion rates, SLA adherence) stored in Delta Lake tables.
4. **Load** – Publish curated datasets to Redshift/Snowflake and expose to ML pipelines.

## Development Workflow
- Local testing using `pyspark` with sample datasets in `data/sample/`.
- Unit tests using `pytest` + `chispa` for DataFrame assertions.
- Data quality checks via Great Expectations with expectations stored in `great_expectations/`.

## Deployment
- Packaged as Docker image executed by Airflow DAG or Glue job.
- Parameterized via environment variables/JSON config.
- Logs shipped to CloudWatch/S3 for auditing.

## Observability
- Metrics (job duration, row counts) pushed to Prometheus via StatsD exporter.
- Data lineage tracked with OpenLineage/Marquez integration.

