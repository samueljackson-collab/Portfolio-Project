# Metrics
- `region_active` gauge per region (1 active, 0 passive) — alert if both 0.
- `failover_duration_seconds` — alert if >60s.
- `http_latency_p95` per region — alert >300ms.
