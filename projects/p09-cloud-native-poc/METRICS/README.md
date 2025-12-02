# Metrics & Alerts — P09

## Metrics
- `p09_http_requests_total` (counter) with labels route,status.
- `p09_request_latency_seconds` (histogram).
- `p09_worker_retries_total` (counter).
- `p09_queue_depth` (gauge).

## Alerts
| Alert | Expression | Severity | Action |
| --- | --- | --- | --- |
| `p09_http_5xx_rate` | `rate(p09_http_requests_total{status=~"5.."}[5m]) > 0.03` | critical | Trigger playbook, roll back recent deploy | 
| `p09_latency_p95_high` | `histogram_quantile(0.95, rate(p09_request_latency_seconds_bucket[10m])) > 0.4` | warning | Scale or investigate DB | 
| `p09_queue_backlog` | `p09_queue_depth > 50` | warning | Scale worker, check downstream | 

## Dashboards
- Traffic overview with latency heatmap.
- Worker performance with retries vs processed counts.

## SLOs
- 99% requests under 300ms in dev.
- Error rate <1% sustained.
