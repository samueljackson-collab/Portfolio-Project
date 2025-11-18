# Operations Runbook

## Day 1: Initial Deployment
1. Copy `.env.example` to `.env` and set secrets for Slack, SMTP, and PagerDuty.
2. Run `./scripts/deploy.sh validate` to lint configurations with promtool and amtool.
3. Deploy stack using `./scripts/deploy.sh start`; verify `docker compose ps` shows healthy containers.
4. Import dashboards automatically provisioned in Grafana; confirm datasources are connected.

## Day 2: Ongoing Maintenance
- **Backups**: Execute `./scripts/deploy.sh backup` weekly; store archives off-host.
- **Updates**: Pull latest images monthly (`docker compose pull`) after reviewing release notes; restart via deploy script.
- **Capacity**: Track disk usage via infrastructure dashboard; adjust retention in Prometheus/Loki before reaching 70% disk.
- **Certificate/TLS**: If fronting with reverse proxy, rotate certificates per corporate policy.

## Incident Response Procedures
- **Alert Storms**: Check Alertmanager inhibition rules; temporarily silence noisy alerts with expiration.
- **Exporter Down**: Validate host connectivity, container status, and firewall rules; redeploy exporter if needed.
- **Data Gaps**: Inspect Prometheus WAL for corruption; restart Prometheus after taking snapshot of data volume.
- **Loki Ingestion Lag**: Reduce label cardinality in Promtail pipelines; increase chunk_target_size only if disk I/O allows.

## Scaling Guidelines
- Shard Prometheus or increase resources when scrape load exceeds 50k samples/sec; federate metrics for long-term storage.
- Move Loki to object storage when retention exceeds 7 days or ingest rate grows; switch boltdb-shipper backend accordingly.
- Use multiple Promtail clients on busy nodes to isolate log paths.

## Disaster Recovery
- Restore from latest backup archives using `./scripts/deploy.sh restore <archive>`.
- Validate restored instance by running health-check script and comparing dashboard data with expected time ranges.
- Store configuration files (prometheus.yml, alert rules, dashboards) in version control for reproducibility.

## Upgrade Procedures
- Test image updates in staging environment by swapping `.env` variables for alternate datasources.
- Run validation commands after merging new rules/dashboards.
- Use Grafana snapshots before upgrading plugins to recover quickly.
