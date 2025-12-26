# Monitoring & Observability Philosophy

**Project:** PRJ-SDE-002 — Observability & Backups Stack  
**Scope:** Prometheus, Alertmanager, Grafana, Loki/Promtail, and Proxmox Backup Server (PBS)

---

## Principles

### USE Method (Utilization, Saturation, Errors)
- **Utilization:** Track per-resource usage (CPU, memory, disk, network) with headroom targets (e.g., CPU <70% sustained).
- **Saturation:** Watch queue lengths and pressure signals (runnable threads, disk IO wait, API latency p95).
- **Errors:** Measure hard failures and slowdowns (HTTP 5xx/4xx ratios, scrape errors, log error rates).

### RED Method (Rate, Errors, Duration)
- **Rate:** Request/ingest counts per service; use SLO-aligned rates for sustained change detection.
- **Errors:** Error rate burn alerts with short (5m) and long (1h) windows to avoid alert storms.
- **Duration:** Latency percentiles (p50/p95/p99) for API and backup job steps to detect degradation before outages.

### Dashboard Rationale
- **Infrastructure Overview:** Combines USE views per host/exporter with saturation callouts (CPU steal, IO wait) and log ingestion rates for triangulation.
- **Application Reliability:** RED-focused views for the demo API and supporting services with request/error/latency correlations and deploy markers.
- **Backup & PBS Health:** Job success rates, retention adherence, repository capacity, and dedup efficiency to surface risks before RPO/RTO drift.

---

## Alert Strategy & Runbooks
- **Routing tiers:** `critical` (paging via PagerDuty + Slack), `warning` (Slack only), `backup` (email + Slack) with receiver mapping in Alertmanager.
- **Noise controls:** Group by `alertname`, `cluster`, `service`; inhibit warnings when criticals fire on the same instance; repeat interval of 12h for long-lived issues.
- **Runbook URLs:** Every alert links to a Markdown runbook under `assets/runbooks/` (see `alert-rules.yml` and `demo-alerts.yml`).
- **Multi-window SLO burn alerts:** 5m/1h windows for latency and error rates to balance sensitivity and stability.

Key runbooks:
- `ALERTING_BACKUP_FAILURE.md` — PBS job and retention failures.
- `OPERATIONAL_RUNBOOK.md` — Core incident response for infra/logging/monitoring stack.
- `PRODUCTION_RUNBOOKS_INCIDENT_RESPONSE.md` — Escalation and communication patterns.

---

## Backup Strategy (PBS)
- **Daily VM and container backups** with 30d retention; weekly synthetic fulls to control storage usage.
- **Offsite sync** enabled via PBS datastore replication to cold storage once per week (sanitized target placeholder).
- **Verification:** Automated `verify-pbs-backups.sh` runs checksum verification and alerts on drift (see scripts directory).
- **Retention enforcement:** PBS prune policies aligned to `pbs-retention-policy.yaml` and monitored via Prometheus exporter metrics.

### PBS Job Artifacts
- `pbs-jobs.yaml`: Sanitized job definitions (datastore, schedule, rate limits, verification hooks).
- `pbs-retention-policy.yaml`: Keep-last/keep-daily/keep-weekly policy used by prune tasks.
- `pbs-report.md`: Lessons learned and operator notes from recent test restores and verification runs.

---

## Lessons Learned
1. **Link alerts to actions:** Adding `runbook_url` annotations reduced mean-time-to-mitigate because responders land directly on the steps.
2. **Dashboard discipline:** USE/RED separation prevents overloaded single dashboards and keeps SRE reviews focused.
3. **Backup proof, not trust:** Scheduled restore tests and checksum verification surfaced misconfigured retention before capacity exhaustion.
4. **Sanitization-first:** All configs here replace real hostnames/IPs/secrets with placeholders; screenshots redact tenant names and URLs.

---

## Sanitization & How to Use
- Sensitive values are represented with placeholders (`demo-api:5000`, `pbs.example.internal`, dummy webhook URLs).
- Screenshots intentionally omit tenant identifiers and real timestamps.
- Import Grafana JSON via **Dashboard → Import → Upload JSON** and map data sources to your environment.
- Copy configs into your infrastructure repo, then replace placeholders and secret env vars before deployment.

**Related Files**
- Grafana dashboards: `assets/grafana/dashboards/*.json`
- Alerting rules: `assets/configs/alerts/demo-alerts.yml`, `assets/configs/alert-rules.yml`
- Backup policies: `assets/pbs/*.yaml`
- Runbooks: `assets/runbooks/*.md`
