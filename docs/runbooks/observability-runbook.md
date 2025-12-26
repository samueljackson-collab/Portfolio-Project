# Observability Runbook

## Dashboards
- **Portfolio Orchestration Overview** (Grafana): request rates, latency, orchestration run counters, collector logs.
- **Collector health**: verify `otel-collector` scrape status via Prometheus exporter (`:9464/metrics`).

## Playbooks
1. **Confirm collector availability**
   - `kubectl -n monitoring port-forward svc/otel-collector 9464:9464`
   - Visit `http://localhost:9464/metrics` and ensure `otelcol_process_uptime` is present.
2. **Trace validation**
   - Generate a run from `/operations` and verify traces in Tempo/Loki for the `service.name=portfolio-api` attribute.
3. **Alert triage**
   - If latency > 500ms P95, capture the `Orchestration Run Counters` graph and correlate with recent deployments.
   - Roll back using the orchestration runbook if errors coincide with a specific change ticket.
4. **Log sampling**
   - Use Grafana logs panel with query `{container="otel-collector"}` to inspect collector errors.

## Exports and SLOs
- Metrics are exported via OTLP and re-exposed for Prometheus scraping on port 9464.
- Set availability SLO at 99.5% for the API service based on `http_requests_total` success ratios.
