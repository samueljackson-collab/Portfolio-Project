# Metrics and Alerts

## Metrics
- `poc_requests_total` (counter)
- `poc_latency_p95_ms` (gauge)
- `poc_worker_checks_success` / `poc_worker_checks_failure` (counters)

## Alerts
```yaml
- alert: PocLatencyHigh
  expr: poc_latency_p95_ms > 250
  for: 5m
  labels:
    severity: page
  annotations:
    summary: "POC API latency high"
    runbook: PLAYBOOK/latency_regression.md
- alert: PocWorkerFailures
  expr: increase(poc_worker_checks_failure[10m]) > 0
  labels:
    severity: ticket
  annotations:
    summary: "Worker health checks failing"
    runbook: RUNBOOKS/deploy.md
```
