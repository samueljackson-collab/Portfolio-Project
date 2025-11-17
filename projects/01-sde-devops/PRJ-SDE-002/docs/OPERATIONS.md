# OPERATIONS RUNBOOK

## Day 1 Operations (Initial Deployment)
1. Copy `.env.example` to `.env` and populate secrets from vault.
2. Run `./scripts/deploy.sh validate` to check configs and ports.
3. Deploy with `./scripts/deploy.sh start` and monitor health checks.
4. Log in to Grafana, rotate admin password, and configure SSO/reverse proxy if applicable.

## Day 2 Operations (Ongoing Maintenance)
- Review dashboards daily for capacity trends (CPU/memory/disk).
- Audit Alertmanager silences weekly to avoid stale silences.
- Rotate credentials monthly and rotate TLS certs as required.
- Run `./scripts/deploy.sh backup` weekly to capture volume snapshots.

## Incident Response Procedures
- Trigger `./scripts/health-check.sh` to baseline system health.
- For alert storms, review Alertmanager UI and apply temporary silence on root-cause alert only.
- For data corruption, restore Prometheus volume from most recent backup using `deploy.sh restore` and restart stack.

## Scaling Guidelines
- Increase Prometheus memory to 3-4GB if sampling >50k samples/s.
- Move Loki storage to faster disk (NVMe) for heavy query workloads; increase retention as storage allows.
- Distribute exporters across hosts; add dedicated monitoring host if CPU contention occurs.

## Disaster Recovery Procedures
- Offload `backups/` archives to remote storage (S3/NAS) after each run.
- In DR, provision Docker host, copy `.env` and latest backup archive, run `deploy.sh restore <archive>`, then `deploy.sh start`.
- Validate dashboards and alerts via health-check script before declaring service restored.

## Upgrade Procedures
- Pin image versions in `docker-compose.yml`; bump deliberately.
- Run `docker compose pull` followed by `deploy.sh start` during maintenance window.
- Validate using `health-check.sh`; roll back by redeploying previous images or restoring backup if regressions occur.
