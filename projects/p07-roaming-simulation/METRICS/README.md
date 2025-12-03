# Metrics & Alerts — P07

## Key Metrics
- `p07_roam_attach_success_total` (counter) — successful attach events by MCC/MNC.
- `p07_roam_attach_latency_ms` (histogram) — end-to-end attach latency.
- `p07_billing_events_total` (counter) — billing trigger count by outcome.
- `p07_pcap_bytes_total` (counter) — PCAP data captured per run (PII-scrubbed).
- `p07_retry_attempts_total` (counter) — MAP retry volume.

## Alerts
| Alert | Expression | Severity | Action |
| --- | --- | --- | --- |
| `p07_roam_attach_error_rate` | `rate(p07_roam_attach_success_total{result="fail"}[5m]) > 0.05` | critical | Invoke playbook, capture PCAP |
| `p07_attach_latency_p95_high` | `histogram_quantile(0.95, rate(p07_roam_attach_latency_ms_bucket[10m])) > 500` | warning | Check toxiproxy/latency injection |
| `p07_billing_drop` | `increase(p07_billing_events_total{outcome="success"}[15m]) == 0` | warning | Validate billing emulator | 
| `p07_pcap_gap` | `increase(p07_pcap_bytes_total[30m]) == 0` | info | Ensure capture hook enabled |

## Dashboards
- **Roaming Overview:** attach success/error, latency percentiles, retry counts.
- **Billing:** billing triggers by visited MCC/MNC, failures by cause.
- **Capture Quality:** PCAP bytes per run, capture errors.

## SLOs
- 99% of attach flows succeed within 400ms in dev/ci.
- <1% retries per 15-minute window.
- Billing trigger generated for 99.5% of successful attaches.
