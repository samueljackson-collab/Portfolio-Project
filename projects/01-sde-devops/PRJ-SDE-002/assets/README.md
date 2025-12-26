# PRJ-SDE-002 Assets

Sanitized evidence for the observability and backup stack. Use these exports, configs, and screenshots to reproduce or review the deployment without exposing private infrastructure.

## Contents
- `grafana/dashboards/` — exportable JSON for infrastructure, application, and alert/backup views.
- `configs/` — Prometheus config, recording rules, and demo alerts; add your own secrets separately.
- `alertmanager/alertmanager.yml` — notification routing template with environment variable placeholders.
- `loki/` — Loki and Promtail configs with scrubbed endpoints and label sets.
- `pbs/` — PBS job manifest, retention report, and restore checklist.
- `docs/` — monitoring philosophy (USE/RED), dashboard rationale, backups, and lessons learned.
- `runbooks/` — operational playbooks plus an alert index tying alerts to actions.
- `screenshots/` — (not included in repo) local-only visuals of Grafana dashboards and PBS retention status.

## Usage & Sanitization
- Replace `${VAR}` placeholders with real secrets at deploy time.
- Hostnames, IPs, and datastore IDs are intentionally generic (e.g., `demo-vm-01`, `loki:3100`).
- Screenshots (when captured locally) and JSON exports contain no production identifiers.

## Screenshot Capture (Local Only)
Binary image assets are intentionally excluded from this repo to keep PRs text-only and review-friendly. If you need screenshots, capture them locally and store outside the repo or in a separate artifact bundle.

## Helpful Links
- Project overview: [`../README.md`](../README.md)
- Quick start for contributions: [`../../../../QUICK_START_GUIDE.md`](../../../../QUICK_START_GUIDE.md)
