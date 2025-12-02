# PRJ-SDE-002 Assets

Supporting materials for the Observability & Backups Stack. Dashboards, configs, backups, and runbooks are sanitized: secrets removed, hostnames/IPs replaced with placeholders, and screenshots captured with demo data.

## Contents
- **docs/** — [Monitoring philosophy](./docs/monitoring-philosophy.md) (USE/RED), dashboard rationale, alert mapping, backups approach, and lessons learned.
- **runbooks/** — [Alert responses](./runbooks/ALERT_RESPONSES.md) and [operational playbook](./runbooks/OPERATIONAL_RUNBOOK.md) for triage and recovery.
- **grafana/dashboards/** — JSON exports for Infrastructure Overview, Application Metrics, Alert Operations, and PBS Backups.
- **screenshots/** — Placeholder folder for dashboard evidence; binaries are excluded from the repo to keep PRs lintable.
- **configs/** — Prometheus, Alertmanager, Loki, and Promtail example configs (placeholders for endpoints/webhooks).
- **backups/** — PBS job plan and retention report summarizing backup posture.
- **scripts/** — Helpers such as `verify-pbs-backups.sh` for sandbox restore checks.
- **diagrams/** — Architecture diagrams for topology context.
- **logs/**, **prometheus/**, **loki/** — Sample exports and placeholders for evidence organization.

## Usage
1. Import the dashboard JSON files into Grafana via **Dashboards → Import**.
2. Drop the configs into your lab for testing; replace placeholder endpoints, webhooks, and emails.
3. Follow `ALERT_RESPONSES.md` for first-response steps and escalation paths.
4. Confirm PBS schedules with `backups/pbs-job-plan.yaml` and review `pbs-retention-report.md` before enabling jobs.
5. Run `scripts/verify-pbs-backups.sh` after snapshot completion to validate integrity.

## Sanitization Checklist
- Webhooks/emails use example values; tokens and passwords removed.
- IPs and hostnames use non-routable or generic placeholders.
- Screenshots generated with demo data and no tenant identifiers (store outside the repo when creating new captures).
- Backup exports omit datastore credentials; only schedules and retention values are shown.

## References
- [Project Overview](../README.md)
- [QUICK_START_GUIDE.md](../../../../QUICK_START_GUIDE.md) for upload instructions.
- [SCREENSHOT_GUIDE.md](../../../../SCREENSHOT_GUIDE.md) for evidence hygiene.
