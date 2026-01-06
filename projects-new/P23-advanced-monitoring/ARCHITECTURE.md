# Architecture

Stack: k6, Grafana k6 Cloud outputs, OpenTelemetry collectors, and synthetic canary scripts.

Data/Control flow: k6 probes hit endpoints, collectors correlate traces/metrics/logs, dashboards show burn rates per region.

Dependencies:
- k6 v0.45+ for load testing and synthetic monitoring scripts.
- Grafana k6 Cloud account and API token for cloud outputs and distributed testing.
- OpenTelemetry Collector 0.88+ configured with trace, metrics, and log receivers.
- Node.js 18+ runtime for JavaScript-based canary scripts and custom k6 extensions.
- Docker Compose for local OTEL collector and backend simulation.
- Grafana 10+ with dashboards for SLO burn rate visualization and alerting.
- Env/config: see README for required secrets and endpoints.
