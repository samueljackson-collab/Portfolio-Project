# Metrics and Alerts

## Metrics
- `mr_healthcheck_latency_ms` (gauge) per region.
- `mr_failover_events_total` (counter).
- `mr_snapshot_replication_age_seconds` (gauge).

## Alerts
```yaml
- alert: FailoverActivated
  expr: increase(mr_failover_events_total[5m]) > 0
  labels:
    severity: page
  annotations:
    summary: "Route 53 failover occurred"
    runbook: PLAYBOOK/failover.md
- alert: SnapshotReplicationStale
  expr: mr_snapshot_replication_age_seconds > 900
  labels:
    severity: ticket
  annotations:
    summary: "Backups not replicated in last 15 minutes"
    runbook: SOP/backups.md
```
