# Metrics and Alerts

## Metrics
- `api_contract_drift_total` (counter) – number of schema mismatches.
- `api_test_pass_ratio` (gauge) – pass percentage per run.
- `api_latency_p95_ms` (gauge) – p95 response time during tests.

## Alerts
```yaml
- alert: ApiContractDrift
  expr: increase(api_contract_drift_total[5m]) > 0
  labels:
    severity: page
  annotations:
    summary: "Schema drift detected"
    runbook: PLAYBOOK/schema_drift.md
- alert: ApiPassRateLow
  expr: api_test_pass_ratio < 0.95
  labels:
    severity: ticket
  annotations:
    summary: "API test pass rate below threshold"
    runbook: RUNBOOKS/newman_pipeline.md
```
