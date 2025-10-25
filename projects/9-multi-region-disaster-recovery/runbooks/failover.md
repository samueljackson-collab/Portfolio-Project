# Failover Runbook

1. Review CloudWatch dashboards for anomalies.
2. Execute `scripts/failover-drill.sh` with the active global cluster ID.
3. Confirm Route53 health checks mark primary region unhealthy.
4. Validate application availability from synthetic monitors.
5. Document timeline and metrics in incident tracker.
