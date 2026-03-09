# Runbook: Failback to Primary

1. **Ensure Primary Healthy**: Verify `/healthz` passes for 15m.
2. **Sync Data**: Copy latest snapshot from secondary to primary bucket (simulated via `jobs/sync.sh`).
3. **Restore Routing**: Mark primary as healthy (`jobs/toggle_primary.sh up`) and wait for Route 53 to converge.
4. **Verify**: Run `consumer/validate.py --report out/failover.json --expect primary`.
5. **Cleanup**: Resume replication schedule; close incident with updated metrics.
