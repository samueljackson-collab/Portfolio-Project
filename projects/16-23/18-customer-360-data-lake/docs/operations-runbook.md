# Operations Runbook

## Deployment
- Terraform infrastructure updates across ingestion, storage, and serving layers.
- Orchestrate pipelines via Airflow with blue/green DAG deployments.
- Run validation suites covering schema drift and data freshness before go-live.

## Monitoring & Alerting
- Track data freshness, ingestion lag, and quality scorecards per data source.
- Alert on failed DAG runs, schema mismatches, and access violations.
- Publish weekly adoption metrics for workspace usage.

## Rollback Procedures
- Use versioned data lake snapshots to revert to previous curated tables.
- Disable impacted pipelines via Airflow tags while investigating failures.
- Notify privacy office if rollback touches regulated datasets.

## Service Level Objectives
- 99% of data delivered within five minutes of source updates.
- <1% failed pipeline executions per week.
- 100% traceability for data access events.
