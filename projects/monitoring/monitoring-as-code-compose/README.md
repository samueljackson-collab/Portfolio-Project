# Monitoring-as-Code Docker Compose

## Overview
Composable observability stack featuring Prometheus, Grafana, Loki, Tempo, and Alertmanager. Provides local environment parity with production monitoring tooling.

## Components
- `docker-compose.yml` defines services, persistent volumes, and networks.
- Pre-provisioned Grafana dashboards and alert rules stored in Git for version control.
- Prometheus scrape configs aligned with Kubernetes/VM targets; includes Pushgateway for batch jobs.
- Loki + Promtail for log aggregation; Tempo for distributed tracing demos.

## Usage
1. `docker compose up -d` to launch stack locally.
2. Access Grafana at `http://localhost:3000` (default credentials stored securely).
3. Load sample dashboards via provisioning files under `grafana/provisioning/`.
4. Run smoke test script `scripts/validate.sh` to ensure data ingestion from demo workloads.

## Integration
- CI pipelines run containerized checks to validate dashboards and alerts (`grizzly` tests).
- Supports remote writes to managed Prometheus (AMP) and Grafana Cloud for production.
- Alert routing to PagerDuty/Slack configured via `.env` secrets.

## Operations
- Runbook outlines backup/restore of Grafana dashboards and Prometheus data.
- Automation scripts handle certificate rotation and TLS termination using Traefik proxy.

