# Metrics & Alerts — P08

## Metrics
- `p08_api_latency_ms` (histogram) — response latency per endpoint.
- `p08_api_errors_total` (counter) — HTTP 4xx/5xx grouped by endpoint.
- `p08_contract_violations_total` (counter) — schema mismatches.
- `p08_newman_iterations_total` (counter) — executed iterations for coverage tracking.

## Alerts
| Alert | Expression | Severity | Action |
| --- | --- | --- | --- |
| `p08_payment_5xx_rate` | `rate(p08_api_errors_total{endpoint="/payments",status=~"5.."}[5m]) > 0.02` | critical | Fail pipeline, switch to mock | 
| `p08_contract_drift` | `increase(p08_contract_violations_total[15m]) > 0` | warning | Review schemas vs responses | 
| `p08_latency_p95_high` | `histogram_quantile(0.95, rate(p08_api_latency_ms_bucket[10m])) > 600` | warning | Investigate backend/slowness | 

## Dashboards
- Endpoint drill-down showing latency and error rate.
- Coverage tracker comparing executed vs planned endpoints.

## SLOs
- 99% of requests complete <500ms in staging.
- Zero schema violations per release.
