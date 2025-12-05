# Operations Package — PRJ-SDE-002

## Deploy & Upgrade
1. **Pre-checks:**
   - Verify TLS cert validity (`openssl x509 -enddate`).
   - Ensure storage free space (Prometheus/Loki/PBS volumes) >30%.
   - Confirm exporter inventory current.
2. **Deploy (Compose):**
   - `docker compose pull && docker compose up -d` from `/opt/monitoring`.
   - Run `promtool check config` and `loki-canary` after start.
   - Validate Grafana data sources and dashboards via provisioning logs.
3. **Upgrade:**
   - Stagger Prometheus/Loki upgrades; backup configs to git and snapshot VM.
   - Use canary environment (staging) to run rule regression tests before prod.

## Rollback
- `docker compose rollback` (if using versioned images) or `docker compose up -d <previous tag>`.
- Restore Prometheus/Loki config from git; restart stack.
- For VM-level issues, restore from PBS snapshot; verify service ports post-restore.

## Runbooks
- **Alert Flooding:** Enable Alertmanager silence for affected service, inspect rule changes, adjust thresholds; validate inhibition.
- **High Cardinality:** Use Prometheus `topk by(__name__)` queries; enable `labeldrop` in scrape config; cap per-target series.
- **Loki Ingest Errors:** Check Promtail logs, TLS handshake, and rate limits; scale out Promtail or adjust pipeline stages.
- **Backup Failures:** Inspect PBS task logs, confirm storage availability, rerun job; if repeated, failover to secondary target.
- **Grafana Login Issues:** Verify OIDC provider status, rotate client secrets, and fall back to local admin if emergency.

## On-Call Playbook
- **Sev0 (data loss or monitoring outage):** Page primary on-call, initiate incident bridge, restore PBS data or failover monitoring VM; update status page.
- **Sev1 (alerting gaps, backup delays):** Acknowledge within 10 minutes, check exporters and Alertmanager queues, run synthetic probe.
- **Sev2 (dashboard errors, minor backup warnings):** Create ticket, schedule fix within 2 business days.
- **Sev3 (requests for new dashboards):** Plan into backlog with acceptance criteria.

## DR & Backup
- PBS nightly backups with 30d retention; weekly verify and monthly offsite sync.
- Document recovery steps with screenshots/logs; store in knowledge base.
- Conduct quarterly game days simulating monitoring VM loss and PBS restore.

## Maintenance Windows
- Pre-announce maintenance in Slack + status page; apply Alertmanager mute timings.
- Post-maintenance validation: exporter scrape success, alert test, Grafana dashboard load, PBS job status.
