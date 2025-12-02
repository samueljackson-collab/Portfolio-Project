# Metrics & Alerts — P10

## Metrics
- `p10_healthcheck_status` (gauge) — 1 healthy, 0 unhealthy per region.
- `p10_failover_duration_seconds` (summary) — time to switch traffic.
- `p10_replica_lag_seconds` (gauge) — RDS replication lag.
- `p10_s3_replication_backlog` (gauge).

## Alerts
| Alert | Expression | Severity | Action |
| --- | --- | --- | --- |
| `p10_primary_down` | `p10_healthcheck_status{region="primary"} == 0` for 2m | critical | Trigger failover playbook | 
| `p10_replica_lag_high` | `p10_replica_lag_seconds > 20` | warning | Investigate replication; pause heavy writes | 
| `p10_failover_slow` | `p10_failover_duration_seconds > 180` | warning | Optimize DNS TTL or automation | 

## SLOs
- Failover <120s end-to-end.
- Replica lag <10s steady state.
- Health checks green 99.9% per month.
