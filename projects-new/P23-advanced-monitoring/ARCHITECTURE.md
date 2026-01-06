# Architecture

Stack: k6, Grafana k6 Cloud outputs, OpenTelemetry collectors, and synthetic canary scripts.

Data/Control flow: k6 probes hit endpoints, collectors correlate traces/metrics/logs, dashboards show burn rates per region.

Dependencies:
- k6 v0.45+ for load generation and synthetic monitoring scripts.
- Grafana k6 Cloud account with API token for cloud outputs and result aggregation.
- OpenTelemetry Collector v0.88+ with OTLP receivers for trace/metric/log correlation.
- Grafana Cloud or self-hosted Grafana instance for dashboard visualization.
- Env/config: see README for required secrets and endpoints.
