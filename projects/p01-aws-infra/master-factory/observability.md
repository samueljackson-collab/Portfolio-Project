# Observability

## Metrics
- ALB: request count, 4xx/5xx rates, target response time.
- RDS: CPU, connections, read/write latency, replica lag.
- Route53: health check status, failover switch time.
- Backup: snapshot duration and failures.

## Logs
- ALB access logs to S3 with 30-day retention.
- RDS audit logs shipped to CloudWatch Logs.
- DR drill script logs stored in `artifacts/drills/<date>.log`.

## Tracing
- Enable X-Ray sampling on app instances (if present) to capture DB and external call traces.

## Alerting
- CloudWatch alarms for ALB 5xx, RDS latency > 50 ms, Route53 health check failure, backup failure, and GuardDuty high-severity findings.
- Alerts route to SNS with PagerDuty/webhook integration.
