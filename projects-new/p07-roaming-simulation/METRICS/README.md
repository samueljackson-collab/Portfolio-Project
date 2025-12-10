# Metrics and Alerts

## Service Metrics
- `roaming_attach_success` (counter) – attach successes per PLMN.
- `roaming_latency_p95_ms` (gauge) – rolling p95 attach latency.
- `roaming_drop_call_pct` (gauge) – percentage of dropped sessions.
- `roaming_fraud_blocks_total` (counter) – fraud rule activations.

## SLOs
- Attach success rate ≥ 99% per region.
- p95 attach latency ≤ 150ms under normal load.
- Fraud detection false positive rate < 0.5%.

## Alert Rules (Prometheus)
```yaml
- alert: RoamingLatencyHigh
  expr: roaming_latency_p95_ms > 200 for 5m
  labels:
    severity: page
  annotations:
    summary: "Roaming attach latency high"
    runbook: RUNBOOKS/replay.md
- alert: RoamingAttachDrop
  expr: rate(roaming_drop_call_pct[5m]) > 0.02
  labels:
    severity: page
  annotations:
    summary: "Attach drop percentage above 2%"
    runbook: PLAYBOOK/latency_spike.md
```
