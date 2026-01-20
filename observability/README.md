# Observability Stack

This directory contains the Grafana dashboard payloads and OpenTelemetry Collector configuration used to
support the portfolio observability stack.

## What's here

- **Grafana dashboards**: [grafana/dashboards/orchestration.json](./grafana/dashboards/orchestration.json) provides the
  "Portfolio Orchestration Overview" dashboard with panels for API request rate, latency, orchestration run counters,
  and collector logs.
- **Grafana provisioning**: [grafana/provisioning/datasources/datasource.yml](./grafana/provisioning/datasources/datasource.yml)
  defines the Prometheus datasource (`http://otel-collector:9464`) and loads dashboards from
  `/var/lib/grafana/dashboards`.
- **Collector configuration**: [otel-collector.yaml](./otel-collector.yaml) stores the OpenTelemetry collector
  settings used by the stack.
