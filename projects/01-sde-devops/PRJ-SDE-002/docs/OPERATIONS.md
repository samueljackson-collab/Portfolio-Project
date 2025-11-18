# Operations Runbook

## Day 1 Operations (Initial Deployment)
1. Prepare `.env` from example and validate credentials.
2. Run `./scripts/deploy.sh validate` to ensure configs are syntactically correct.
3. Start stack via `./scripts/deploy.sh start` and confirm health via `./scripts/health-check.sh`.
4. Log into Grafana and rotate admin password to a secret manager value.

## Day 2 Operations (Ongoing)
- Monitor Grafana dashboards daily for trends; adjust thresholds if frequent false positives.
- Review Alertmanager notifications and silence during planned maintenance using `amtool silence`.
- Weekly: run `./scripts/deploy.sh backup` and store archives off-host.
- Monthly: patch container images by re-running deploy and verifying configs with `validate`.

## Incident Response Procedures
- Critical alert received -> verify Prometheus and exporters are up using health-check script.
- If host unreachable, check hypervisor/physical connectivity before restarting containers.
- For storage alerts, prioritize freeing space to avoid TSDB corruption; snapshot volumes before drastic changes.

## Scaling Guidelines
- Increase Prometheus CPU/memory limits in compose file when sample ingestion exceeds 50k samples/sec.
- Split scraping into multiple jobs or remote write if adding many targets.
- Loki retention/chunk sizes should be revisited if log volume doubles; consider object storage backend.

## Disaster Recovery Procedures
- Restore from latest backup tarball using `./scripts/deploy.sh restore <archive>`.
- If TSDB corrupted, start Prometheus with `--storage.tsdb.allow-overlapping-blocks` temporarily and rebuild indexes.
- Re-provision Grafana dashboards automatically on container start; ensure provisioning files are under version control.

## Upgrade Procedures
- Pin new image versions in `docker-compose.yml`, run `deploy.sh validate`, then `deploy.sh start`.
- Validate dashboards post-upgrade for plugin compatibility.
- Keep changelog of upgrades with date, version, and validation notes.
