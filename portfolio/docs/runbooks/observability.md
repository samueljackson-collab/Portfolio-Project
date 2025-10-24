# Observability Runbook

1. Validate Prometheus targets via `http://localhost:9090/targets`.
2. Import Grafana dashboards from `tools/observability/grafana/dashboards/` and verify data sources.
3. Ensure Loki ingests logs and connect Grafana Explore to the Loki data source.
4. Configure alert rules for critical error rates and latency thresholds.
