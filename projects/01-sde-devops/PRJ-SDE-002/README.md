# Enterprise Monitoring & Observability Stack

Production-ready monitoring solution for Proxmox and container workloads. The stack combines Prometheus, Grafana, Loki, Promtail, Alertmanager, node_exporter, and cAdvisor with hardened defaults, health checks, and operational runbooks.

## Architecture Overview
- **Prometheus** scrapes exporters and the Proxmox nodes every 15s and evaluates alerts shipped to Alertmanager.
- **Grafana** renders prebuilt dashboards for infrastructure, hosts, containers, and logs.
- **Loki + Promtail** aggregate container/system logs with low cardinality labeling.
- **Alertmanager** routes critical/warning notifications to Slack, email, or PagerDuty with inhibition to avoid storms.
- **Node Exporter & cAdvisor** expose host and container metrics.
- Dual-network topology isolates exporter traffic from user-facing endpoints.

## Features & Capabilities
- Pinned container versions, explicit resource limits, and localhost binding for UI components.
- Prebuilt alert rules covering infrastructure, containers, and monitoring-plane health.
- Provisioned dashboards with variables for environment, instance, and container filtering.
- Backup/restore scripts for all persistent volumes.
- Health-check script that exercises metrics, logs, and alert pathways.

## Quick Start
1. Copy `.env.example` to `.env` and adjust credentials and retention parameters.
2. Validate configuration: `./scripts/deploy.sh validate`.
3. Start the stack: `./scripts/deploy.sh start`.
4. Open Grafana via `http://127.0.0.1:3000` (admin credentials from `.env`).
5. Confirm dashboards and alerts via the provided panels and send a test alert with `./scripts/health-check.sh`.

## Configuration Guide
- **Prometheus targets**: edit `prometheus/prometheus.yml` to add new exporters or Proxmox hosts; prefer file-based service discovery for larger fleets.
- **Alert rules**: tune thresholds in `prometheus/alerts/rules.yml`; use `promtool check rules` before reload.
- **Alertmanager routing**: configure Slack/email/PagerDuty secrets via `.env`; adjust routes and inhibition as needed.
- **Loki retention**: controlled in `loki/loki-config.yml` (defaults to 7 days) and compactor settings.
- **Promtail pipelines**: extend `promtail/promtail-config.yml` to parse structured logs and drop high-cardinality labels.

## Dashboard Guide
- `infrastructure-overview.json`: executive snapshot of fleet health, capacity, and firing alerts.
- `host-details.json`: per-host CPU, memory, disk I/O, network traffic, and top processes with instance variable.
- `container-monitoring.json`: per-container CPU/memory/network usage and restart tracking.
- `logs-explorer.json`: LogQL-driven search with variables for container name and log level.

## Alert Rule Reference
Key alerts include instance down, CPU/memory saturation, disk capacity and growth prediction, container instability, and monitoring-plane failures (Prometheus/Grafana). All alerts include summaries, descriptions, and runbooks embedded in annotations.

## Operations
- **Backup**: `./scripts/deploy.sh backup` stores compressed copies of all volumes in `backups/`.
- **Restore**: `./scripts/deploy.sh restore <archive>` stops the stack and restores data.
- **Validate**: run validation prior to deploy to catch syntax issues.
- **Health**: `./scripts/health-check.sh` checks endpoints, queries Prometheus, exercises Loki, and fires a test alert.

## Security Considerations
- UI ports bind to 127.0.0.1; publish externally only via reverse proxy with TLS.
- Secrets and credentials are sourced from `.env`; avoid committing real secrets.
- Resource limits prevent runaway processes from exhausting the host.

## Performance Tuning
- Increase Prometheus retention or scrape interval based on disk/CPU headroom.
- Adjust Loki chunk size or retention for higher log throughput.
- Scale node_exporter to remote Proxmox hosts and add recording rules for heavy dashboards.
