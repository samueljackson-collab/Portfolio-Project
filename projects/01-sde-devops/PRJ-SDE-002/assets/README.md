# Observability & Backups Stack Assets

**Status:** 🟢 Complete (sanitized for sharing)

## Overview
Evidence and configurations for PRJ-SDE-002, covering Prometheus, Alertmanager, Grafana, Loki/Promtail, and Proxmox Backup Server (PBS). All hostnames, IPs, and secrets are placeholders.

## Documentation
- [Monitoring & Observability Philosophy](./docs/monitoring-observability.md) — USE/RED approach, alert/runbook wiring, backup strategy, lessons learned.
- [Project README](../README.md) — Parent project context.

## Dashboards (Grafana JSON)
- Infrastructure USE view: [`grafana/dashboards/infrastructure-overview.json`](./grafana/dashboards/infrastructure-overview.json)
- Application RED view: [`grafana/dashboards/application-metrics.json`](./grafana/dashboards/application-metrics.json)
- Backup/PBS health: [`grafana/dashboards/backup-health.json`](./grafana/dashboards/backup-health.json)

## Configurations
- Prometheus: [`configs/prometheus.yml`](./configs/prometheus.yml) and alert rules [`configs/alert-rules.yml`](./configs/alert-rules.yml), [`configs/alerts/demo-alerts.yml`](./configs/alerts/demo-alerts.yml)
- Alertmanager: [`alertmanager/alertmanager.yml`](./alertmanager/alertmanager.yml) (use `.env.example` for secrets)
- Loki/Promtail: [`loki/loki-config.yml`](./loki/loki-config.yml), [`loki/promtail-config.yml`](./loki/promtail-config.yml)

## Backups (PBS)
- Job definitions: [`pbs/pbs-jobs.yaml`](./pbs/pbs-jobs.yaml)
- Retention policy: [`pbs/pbs-retention-policy.yaml`](./pbs/pbs-retention-policy.yaml)
- Verification report & lessons: [`pbs/pbs-report.md`](./pbs/pbs-report.md)
- Verification script: [`scripts/verify-pbs-backups.sh`](./scripts/verify-pbs-backups.sh)

## Runbooks
- Core operations: [`runbooks/OPERATIONAL_RUNBOOK.md`](./runbooks/OPERATIONAL_RUNBOOK.md)
- Incident management: [`runbooks/PRODUCTION_RUNBOOKS_INCIDENT_RESPONSE.md`](./runbooks/PRODUCTION_RUNBOOKS_INCIDENT_RESPONSE.md)
- Backup alerts: [`runbooks/ALERTING_BACKUP_FAILURE.md`](./runbooks/ALERTING_BACKUP_FAILURE.md)

## Evidence / Screenshots
Binary screenshots are intentionally omitted because the PR channel cannot transport binaries. To generate sanitized captures:
- Import the Grafana JSON dashboards above into a lab Grafana instance.
- Point them at demo datasources with placeholder hosts (e.g., `demo-api`, `pbs.example.internal`).
- Export/share sanitized PNGs into [`./screenshots/`](./screenshots/) following [`screenshots/README.md`](./screenshots/README.md).

## Sanitization Checklist
- ✅ Dummy hostnames/URLs (`demo-api`, `pbs.example.internal`)
- ✅ Secrets referenced via env vars/templates only
- ✅ Screenshots redact tenant data and use demo labels
- ✅ README links updated to all new artifacts

## Quick Import Notes
- Import dashboards via Grafana **Dashboard → Import → Upload JSON** and map to your Prometheus/Loki datasources.
- Apply Prometheus/Alertmanager/Loki configs to your environment after replacing placeholders and loading secrets from `.env` or a secret manager.
- Sync PBS YAML into your Proxmox Backup Server, validate retention with a dry-run prune, and schedule verification using `verify-pbs-backups.sh`.
