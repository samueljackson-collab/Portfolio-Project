# Architecture

Stack: k6, Grafana k6 Cloud outputs, OpenTelemetry collectors, and synthetic canary scripts.

Data/Control flow: k6 probes hit endpoints, collectors correlate traces/metrics/logs, dashboards show burn rates per region.

Dependencies:
- k6 0.45+ for load testing and synthetic monitoring.
- Grafana k6 Cloud account OR self-hosted Grafana for visualization.
- OpenTelemetry Collector 0.88+ for trace/metric correlation.
- Docker Compose or Kubernetes for collector deployment.
- Env/config: see README for required secrets and endpoints.
