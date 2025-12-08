# Architecture

Stack: k6, Grafana k6 Cloud outputs, OpenTelemetry collectors, and synthetic canary scripts.

Data/Control flow: k6 probes hit endpoints, collectors correlate traces/metrics/logs, dashboards show burn rates per region.

Dependencies:
- k6, Grafana k6 Cloud outputs, OpenTelemetry collectors, and synthetic canary scripts.
- Env/config: see README for required secrets and endpoints.
