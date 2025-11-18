# Enterprise Monitoring & Observability Stack

![Architecture Diagram](./docs/architecture-diagram.png)

## Executive Summary
Production-ready monitoring solution combining Prometheus, Grafana, Loki, Alertmanager, Promtail, node-exporter, and cAdvisor. Designed for Proxmox homelab and Docker workloads with secure defaults, operational runbooks, and curated dashboards.

## Table of Contents
- Architecture Overview
- Features & Capabilities
- Prerequisites
- Quick Start
- Detailed Configuration
- Dashboard Guide
- Alert Rule Reference
- Troubleshooting
- Maintenance & Operations
- Security Considerations
- Performance Tuning
- Contributing
- License

## Architecture Overview
Metrics path: exporters → Prometheus → Grafana dashboards. Logs path: Promtail → Loki → Grafana. Alerting path: Prometheus rules → Alertmanager → Slack/Email/PagerDuty. Two-network model isolates backend scrape traffic from frontend UI exposure; localhost bindings enforced.

## Features & Capabilities
- 15-second scrape interval, 15-day retention guidance (configurable via `.env`).
- 7-day Loki retention with boltdb-shipper and filesystem storage.
- Multi-channel alerting (Slack, email, PagerDuty) with inhibition rules.
- Prebuilt dashboards: infrastructure overview, host deep-dive, container monitoring, logs explorer.
- Deployment scripts with validation, backup, restore, and health checks.

## Prerequisites
- Docker 24+ with compose plugin
- 4GB RAM, 50GB disk (baseline for retention targets)
- Access to Proxmox nodes and container hosts
- Optional: SMTP for email, Slack webhook, PagerDuty routing key

## Quick Start
1. Copy `.env.example` to `.env` and populate secrets.
2. `cd projects/01-sde-devops/PRJ-SDE-002`
3. `./scripts/deploy.sh start`
4. Access Grafana via `http://127.0.0.1:3000` (default admin from `.env`).
5. Run `./scripts/health-check.sh` to verify metrics, logs, and alerts.

## Detailed Configuration
- `docker-compose.yml`: pins images, health checks, resource limits, dual networks.
- `prometheus/prometheus.yml`: scrape jobs for stack, cAdvisor, node exporter, Proxmox nodes.
- `prometheus/alerts/rules.yml`: infrastructure, container, and monitoring alerts with runbooks.
- `alertmanager/alertmanager.yml`: hierarchical routing with inhibition and receiver placeholders.
- `loki/loki-config.yml`: single-node boltdb-shipper storage, 7-day retention.
- `promtail/promtail-config.yml`: Docker and system logs with cardinality controls.
- `grafana/provisioning/*`: auto-provision datasources and dashboards.

## Dashboard Guide
- **Infrastructure Overview**: fleet-level CPU/memory trends, disk usage table, top resource consumers, active alerts, network throughput.
- **Host Details**: per-host CPU core load, memory breakdown, disk IO, network interfaces, filesystem gauges, load averages, top processes.
- **Container Monitoring**: per-container CPU/memory/network IO, filesystem usage, restart counts, running container stats.
- **Logs Explorer**: live tail and queries filtered by container and level, log volume trends, error table.

## Alert Rule Reference
See `prometheus/alerts/rules.yml` for expressions, severities, and runbooks. Key thresholds: CPU warning 80%/critical 95%, memory warning 85%/critical 95%, disk warning 15%/critical 5%, predictive disk fill in 24h, container CPU/memory >90% of limits.

## Troubleshooting
- Service won't start: run `docker compose logs <service>`; validate configs via `./scripts/deploy.sh validate`.
- Prometheus scrape failures: verify targets reachable, check firewall, review `up` metric in UI.
- Alerts missing: confirm rules loaded (`/-/reload`), check Alertmanager inhibitions.
- Logs missing: ensure Promtail has access to `/var/lib/docker/containers` and Loki ready endpoint.
- Dashboards empty: confirm datasources provisioned and targets healthy.

## Maintenance & Operations
- Backups: run `./scripts/deploy.sh backup` (archives volumes).
- Updates: `docker compose pull` then `./scripts/deploy.sh restart`.
- Restore: `./scripts/deploy.sh restore <backup.tar.gz>`.
- Capacity planning: watch disk usage and adjust retention in `.env`/Loki config.

## Security Considerations
- Services bound to localhost; expose via reverse proxy with TLS/MFA if remote access is required.
- Secrets only via `.env`; never commit real credentials.
- Backend network isolates scrapes from UI plane.
- Enforce least privilege on SMTP/webhooks; rotate credentials regularly.

## Performance Tuning
- Lower scrape_interval for higher fidelity; monitor TSDB size impact.
- Adjust Loki retention/chunk_target_size for log volume changes.
- Increase container resource limits if persistent throttling observed.
