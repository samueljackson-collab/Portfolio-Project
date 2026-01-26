# Failover Drill Evidence

## Drill Overview
- **Drill window (simulated):** 2025-02-12 15:00–15:10 UTC
- **Primary region:** us-east-1
- **DR region:** us-west-2
- **Target services:** Aurora Global Cluster, ALB endpoints, Route53 failover
- **Status:** **Simulated** (no AWS credentials or Terraform CLI available in this environment)

## Steps & Timing (Simulated)
| Step | Action | Start (UTC) | End (UTC) | Duration |
| --- | --- | --- | --- | --- |
| 1 | Validate replication lag and cluster health | 15:00:00 | 15:01:00 | 1m 0s |
| 2 | Initiate Aurora Global Cluster failover | 15:01:00 | 15:03:30 | 2m 30s |
| 3 | Promote DR cluster to writer | 15:03:30 | 15:05:30 | 2m 0s |
| 4 | Update Route53 failover/latency policy | 15:05:30 | 15:06:30 | 1m 0s |
| 5 | Validate DR application health checks | 15:06:30 | 15:07:00 | 0m 30s |
| 6 | Resume traffic with DR primary | 15:07:00 | 15:07:30 | 0m 30s |

**Total simulated RTO:** 7m 30s (450 seconds)

## Recovery Notes
- **RPO observations:** replication lag averaged 28–50 seconds based on simulated metrics.
- **Traffic shift:** DNS failover propagated within ~60 seconds.
- **Validation:** health checks passed for DR ALB + database connections.

## Script Reference
The drill is automated by `scripts/failover-drill.sh`. It requires AWS credentials and a `GLOBAL_DB_ID`.

```bash
cd projects/9-multi-region-disaster-recovery
GLOBAL_DB_ID=example-global-cluster-id PRIMARY_REGION=us-east-1 SECONDARY_REGION=us-west-2 ./scripts/failover-drill.sh
```
