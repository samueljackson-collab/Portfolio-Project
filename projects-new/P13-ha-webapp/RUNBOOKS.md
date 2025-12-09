# Runbooks

## Failover drill
1. Run `scripts/trigger_failover.sh` to demote primary.
2. Monitor app health via `/status` and DB replication metrics.
3. Execute `scripts/failover_validation.sh` to confirm read/write success.
4. Capture timings in `docs/incidents/failover-<date>.md`.

## NGINX outage
1. Check container: `docker compose logs nginx`.
2. Validate config syntax: `docker compose exec nginx nginx -t`; if bad, roll back last change.
3. Reload service and rerun synthetic tests.

## Database lag alert
1. Inspect `postgres_exporter` metrics; verify WAL size.
2. Increase resources for replica container and temporarily throttle writes via feature flag.
3. If lag persists, add new replica and rebalance traffic.
