# Enterprise Monitoring & Observability Stack

![Architecture Diagram](./docs/architecture-diagram.png)

## Executive Summary
Production-ready monitoring solution for infrastructure observability using Prometheus, Grafana, Loki, Promtail, Alertmanager, cAdvisor, and Node Exporter. Designed for Proxmox homelab but deployable to any Docker host. Provides metrics, logs, alerting, dashboards, and operational tooling with clear runbooks.

## Table of Contents
- Architecture Overview
- Features & Capabilities
- Prerequisites
- Quick Start (5-minute deployment)
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
- Prometheus scrapes exporters (Node Exporter, cAdvisor, Proxmox) over monitoring_backend network.
- Grafana runs on monitoring_frontend network and queries Prometheus/Loki for metrics and logs.
- Promtail tails system and container logs, shipping to Loki for indexing and retrieval.
- Alertmanager receives alerts from Prometheus and routes to email/Slack/PagerDuty with inhibition rules.
- Docker Compose enforces health checks, restart policies, and resource limits for each component.

## Features & Capabilities
- Real-time metrics with 15s scrape cadence and 15-day retention.
- Centralized logs with 7-day retention and JSON parsing for containers.
- Multi-channel alerting (Email, Slack, PagerDuty) with grouping and inhibition.
- Pre-built dashboards for infra overview, host deep dive, containers, and logs explorer.
- Deployment scripts for validation, health checks, and backups/restores of stateful volumes.

## Prerequisites
### Required
- Docker 24.0+ with compose plugin
- 4GB RAM and 50GB free disk
- Network reachability to monitored Proxmox exporters and hosts

### Optional
- SMTP endpoint for email alerts
- Slack webhook for chat notifications
- PagerDuty routing key for paging
- Reverse proxy (Traefik/Nginx) for TLS and external access

## Quick Start
1. `cp .env.example .env` and set secure credentials.
2. Run `./scripts/deploy.sh validate` to verify configs.
3. Deploy stack: `./scripts/deploy.sh start`.
4. Verify services: `./scripts/health-check.sh`.
5. Login to Grafana at http://localhost:3000 with credentials from `.env`.

Expected: all services healthy within 2 minutes; Prometheus targets UP; dashboards pre-provisioned.

## Detailed Configuration
- **docker-compose.yml**: Service wiring, networks, resource limits, and health checks.
- **prometheus/prometheus.yml**: Scrape jobs for Prometheus, exporters, Grafana, Loki, and Proxmox. Alertmanager endpoint and rule files included.
- **prometheus/alerts/rules.yml**: Infrastructure, container, and monitoring alerts with runbooks and tuning notes.
- **alertmanager/alertmanager.yml**: Grouping, routing, receivers, and inhibition to reduce noise.
- **loki/loki-config.yml**: Single-node boltdb-shipper with 7-day retention and compaction.
- **promtail/promtail-config.yml**: Log pipelines for Docker, system logs, journald, and auth logs with label hygiene.
- **grafana/provisioning**: Datasources and dashboards auto-loaded read-only at startup.

## Dashboard Guide
- **Infrastructure Overview**: Hosts count, uptime gauge, average CPU/memory, top hosts, disk table, alerts timeline, and network throughput.
- **Host Details**: Per-instance variable, CPU per core, memory breakdown, disk IO, network IO, filesystem usage, load averages, and top processes.
- **Container Monitoring**: Counts by status, per-container CPU/memory/network, filesystem usage, restart counts, and health timeline.
- **Logs Explorer**: Live log stream, log volume by level, samples table, error-rate timeseries, with container/log level filters.

## Alert Rule Reference
Key alerts include InstanceDown, HighCPUUsage/HighMemoryUsage (warning/critical tiers), DiskSpaceLow/DiskWillFillSoon, container CPU/memory/restart issues, and monitoring stack health (PrometheusDown, GrafanaDown, TSDB reload failures). Each alert includes annotations and runbooks for rapid response.

## Troubleshooting
Common issues and fixes live in [docs/TROUBLESHOOTING.md](./docs/TROUBLESHOOTING.md). Highlights:
- Service won't start -> run `./scripts/deploy.sh validate`, check ports.
- Prometheus scrape failures -> verify exporter endpoints and firewall.
- Alerts not firing -> confirm Alertmanager reachable and rules loaded.
- Logs missing -> check promtail permissions to /var/log and Docker socket.

## Maintenance & Operations
- Backups: `./scripts/deploy.sh backup` creates timestamped archive of volumes.
- Restore: `./scripts/deploy.sh restore <archive>` restores data.
- Health: `./scripts/health-check.sh` validates endpoints, queries, alert path, and Loki ingestion.
- Updates: rerun `deploy.sh start` after updating images/config; configs hot-reload via Prometheus web lifecycle.

## Security Considerations
- Grafana and Prometheus bound to localhost; expose via TLS-enabled reverse proxy if needed.
- Secrets provided via `.env`; never commit real credentials. Prefer secrets manager for production.
- Networks segmented (frontend/backend) to limit blast radius.
- Promtail gRPC disabled; restrict Loki/Promtail ports with host firewall when exposed.

## Performance Tuning
- Adjust scrape_interval for busy workloads; lower intervals increase TSDB size (estimate in docker-compose comments).
- Manage label cardinality (avoid container_id in Promtail labels) to keep Loki memory bounded.
- Increase Prometheus memory/CPU limits if running >50k samples/s; tune retention accordingly.

## Contributing
PRs welcome for new dashboards, exporters, or automation improvements. Ensure configs validate with promtool/amtool.

## License
MIT (inherit project root license).
