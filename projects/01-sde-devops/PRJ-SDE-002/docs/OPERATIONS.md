# Operations Runbook

## Day 1 Operations
1. Validate prerequisites (`./scripts/deploy.sh validate`).
2. Deploy stack (`./scripts/deploy.sh start`).
3. Verify dashboards and alerts (`./scripts/health-check.sh`).
4. Document access credentials and store in password manager.

## Day 2 Operations
- Daily: Review alert notifications and Grafana dashboards for anomalies.
- Weekly: Rotate logs, confirm backups exist in `backups/`.
- Monthly: Update container images (`docker compose pull`) and restart.

## Incident Response Procedures
1. Triage severity from Alertmanager annotations.
2. For Prometheus down: check container logs, validate volume health, restore from backup if TSDB corrupted.
3. For Loki ingestion failure: check `/ready` endpoint, disk space, compactor logs.
4. For alert storms: review inhibition rules and routing; adjust thresholds if noisy.

## Scaling Guidelines
- Increase Prometheus memory/CPU limits in `docker-compose.yml` when sustained query latency observed.
- Offload logs to external object storage when 7-day retention exceeds disk capacity.
- Shard exporters (per host) rather than increasing scrape interval to avoid cardinality explosion.

## Disaster Recovery Procedures
- Backups via `./scripts/deploy.sh backup` produce tarballs per volume.
- Restore by stopping stack, running `./scripts/deploy.sh restore <archive>`, then `./scripts/deploy.sh start`.
- Validate recovery with `./scripts/health-check.sh` and manual dashboard spot-checks.

## Upgrade Procedures
- Pull new images, run `./scripts/deploy.sh restart`.
- Monitor `prometheus_tsdb_reloads_failed_total` and Grafana health after restart.
- Roll back by redeploying pinned versions in `docker-compose.yml` if regressions appear.
