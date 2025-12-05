# Metrics & Observability Strategy — PRJ-SDE-002

## SLOs
- Monitoring plane availability: 99.9% monthly.
- Alert delivery success: 99% within 2 minutes to primary channel.
- Backup success rate: ≥98% weekly; restore drill success 100% quarterly.
- Loki query P95: <2s for 24h window; Prometheus scrape latency P95 <500ms.

## Golden Signals & Dashboards
- **Infrastructure:** CPU/mem/disk, network throughput, storage IOPS, node uptime.
- **Applications:** HTTP latency, error rates, request volume, queue depth, cache hit ratio.
- **Backups:** Job duration, success/failure, dedup savings, restore duration, offsite sync status.
- **Platform Health:** Prometheus TSDB usage, Alertmanager queue depth, Loki ingester load, Grafana datasource health.

## Alerting Standards
- Severity mapping (sev0–sev3) with routing + runbook links.
- Anti-noise: inhibition for related alerts, grouping by service/env, rate limits for flapping exporters.
- Maintenance: mute timings configured for planned windows; auto-expiring silences with owner/reason metadata.

## Retention & Storage
- Prometheus 30d on SSD; optional remote-write to Thanos for 180d.
- Loki: critical 30d, standard 14d, dev 7d with object storage backend.
- Alert history retained 90d; Grafana dashboard versions retained 180d.

## Instrumentation Guidance
- Exporters: Node, blackbox, Proxmox, application-specific; prefer static labels (`service`, `env`, `owner`).
- Logs: Structured JSON with trace/span IDs; align labels to reduce cardinality.
- Backups: PBS metrics scraped; pushgateway for post-restore metrics.

## Validation & Runbooks
- Weekly alert fire drills per severity.
- Monthly dashboard audit to remove stale panels and verify data sources.
- Rolling restart tests to ensure scrape/ingest resumes without data loss.
- Alert fatigue review: track false-positive rate and adjust thresholds.

## Evidence Collection
- Export Grafana dashboards as JSON to git; attach screenshots for quarterly reviews.
- Store promtool test outputs and Alertmanager routing simulations in CI artifacts.
- Backup restore logs archived with tickets.
