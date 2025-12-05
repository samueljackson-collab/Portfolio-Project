# Reporting Package — PRJ-SDE-002

## Audiences & Cadence
- **Engineering Leadership:** Bi-weekly dashboard of SLOs, alert volume/noise, backup success, and incidents.
- **Security & Compliance:** Monthly review of access logs, cert rotations, backup verification evidence.
- **Ops/On-Call:** Weekly summary of alert trends, silences, exporter coverage, and action items.

## KPIs
- Monitoring uptime, alert delivery success, alert false-positive rate.
- Backup success/failure counts, restore RTO/RPO attainment, dedup savings.
- Exporter coverage percentage and scrape error rate.
- Dashboard freshness and adoption (views per service).

## Artifacts
- Grafana reports exported as PDF/PNG for leadership; JSON stored in git.
- Alertmanager silence/audit logs attached to weekly ops notes.
- PBS task logs and restore verification outputs stored in knowledge base.

## Automation
- Scheduled Grafana reporting jobs (or wkhtmltopdf) to email leadership.
- CI job to publish weekly metrics snapshot to S3/share and post links to Slack.
- Automated Jira ticket creation for repeated failing alerts or backup jobs.

## Governance
- Each report lists data sources and collection times; retain artifacts for 180 days.
- Sign-off from SRE lead for changes to KPIs or SLO targets.
