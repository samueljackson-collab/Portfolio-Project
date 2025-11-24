# Metrics and Alerts
- **roaming_events_processed_total** (counter) — success throughput; alert if drop >30% over 5m.
- **roaming_consumer_lag** (gauge) — Kafka lag; alert at >1k for 10m.
- **roaming_db_write_seconds** (histogram) — p95 > 250ms triggers DB latency investigation.
- **roaming_anomalies_total** (counter) — spikes >3x baseline open SEV-2.
- **backup_job_success** (gauge) — 0 signals failed backup; page if 2 consecutive failures.
