# Enterprise Monitoring & Observability Stack

![Architecture Diagram](./docs/architecture-diagram.png)

## Executive Summary
Production-ready monitoring solution for infrastructure observability using Prometheus, Grafana, Loki, Promtail, Alertmanager, Node Exporter, and cAdvisor. Designed for Proxmox virtualization and container workloads with strong defaults, alerting, and dashboards.

## Table of Contents
- Architecture Overview
- Features & Capabilities
- Prerequisites
- Quick Start
- Configuration Guide
- Dashboard Guide
- Alert Rule Reference
- Troubleshooting
- Maintenance & Operations
- Security Considerations
- Performance Tuning
- Contributing
- License

## Architecture Overview
The stack collects host and container metrics (Prometheus + exporters), aggregates logs (Loki + Promtail), and visualizes everything in Grafana. Alertmanager routes alerts to Slack, email, and PagerDuty. Frontend/Backend network split keeps dashboards accessible while exporters remain isolated.

## Features & Capabilities
- Real-time metrics collection with 15s scrape interval
- 15-day metric retention and 7-day log retention (tunable via .env)
- Multi-channel alerting with inhibition to reduce noise
- Pre-built dashboards for infra, hosts, containers, and logs
- Automated deployment scripts with validation, backup, and restore

## Prerequisites
- Docker 24.0+ and Compose plugin
- 4GB RAM and 50GB free disk
- Network access to Proxmox hosts and monitored endpoints
- Optional: SMTP, Slack webhook, PagerDuty integration

## Quick Start
1. Copy `.env.example` to `.env` and fill credentials.
2. `./scripts/deploy.sh start`
3. Access Grafana via http://localhost:3000 (admin credentials from .env).
4. Run `./scripts/health-check.sh` to verify endpoints, metrics, alerts, and logs.

## Configuration Guide
- Prometheus scrape jobs defined in `prometheus/prometheus.yml`; add targets under `static_configs` with labels consistent across environments.
- Alert rules live in `prometheus/alerts/rules.yml`; thresholds tailored for homelab but easily adjustable.
- Alertmanager routing configured in `alertmanager/alertmanager.yml` using severity-based paths with inhibition to prevent storms.
- Loki and Promtail configs tune retention, chunk sizing, and label hygiene to manage cardinality.

## Dashboard Guide
Dashboards auto-provisioned from `grafana/dashboards/`:
- **infrastructure-overview**: exec summary of uptime, CPU/memory trends, top talkers, network, and active alerts.
- **host-details**: per-host deep dive with CPU per core, memory, disk IO, network, load averages, and top processes.
- **container-monitoring**: container CPU/memory, network I/O, filesystem usage, restarts, and health timeline.
- **logs-explorer**: LogQL-driven exploration with filters for container and log level, plus error rate visualizations.

## Alert Rule Reference
Key alerts include InstanceDown, CPU/Memory thresholds, disk capacity and prediction, container resource saturation, and control-plane checks for Prometheus/Grafana health. Runbooks embedded in annotations provide immediate remediation steps.

## Troubleshooting
- Use `docker compose ps` and health checks to confirm service status.
- Query Prometheus `up` metric to ensure targets are scraping.
- Check Loki ingestion by searching for `promtail-test-line` after running health-check script.
- Validate configs with `./scripts/deploy.sh validate` before restarts.

## Maintenance & Operations
- Backups: `./scripts/deploy.sh backup` creates timestamped tarball of data volumes.
- Restore: `./scripts/deploy.sh restore <archive>` to repopulate volumes.
- Updates: rerun `./scripts/deploy.sh start` after bumping images.

## Security Considerations
- Grafana and Prometheus bound to localhost; expose via reverse proxy with TLS if needed.
- Secrets externalized to `.env`; avoid committing populated files.
- Network separation via monitoring_backend prevents exporter exposure.

## Performance Tuning
- Adjust scrape intervals and retention in `.env` to fit hardware budget.
- Review Loki `retention_period` and chunk sizing for log volume changes.
- Reserve adequate CPU/memory in compose deploy blocks to prevent starvation.
