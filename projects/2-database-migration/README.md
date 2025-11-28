# Project 2: Database Migration Platform

Change data capture service enabling zero-downtime migrations between PostgreSQL clusters.

## Highlights
- Debezium connector configuration in [`config/debezium-postgres-connector.json`](config/debezium-postgres-connector.json).
- Python orchestrator coordinates cutover, validation, and rollback steps in [`src/migration_orchestrator.py`](src/migration_orchestrator.py).
- Container image definition for runtime workers in [`Dockerfile`](Dockerfile).
- Kubernetes deployment + ConfigMap to run the connector in [`k8s/connector-deployment.yaml`](k8s/connector-deployment.yaml).
- Monitoring alerts for replication health in [`monitoring/alerts.yml`](monitoring/alerts.yml).
- Runbook with operational steps in [`RUNBOOK.md`](RUNBOOK.md) and background in [`wiki/overview.md`](wiki/overview.md).
- Pytest coverage in [`tests/test_migration_orchestrator.py`](tests/test_migration_orchestrator.py) executed via [`pytest`](pytest.ini) and CI workflow [`./.github/workflows/ci.yml`](.github/workflows/ci.yml).
