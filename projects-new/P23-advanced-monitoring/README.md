# P23 – Advanced Monitoring

Synthetic monitoring plus RUM and backend tracing to validate SLOs across regions.

## Quick start
- Stack: k6, Grafana k6 Cloud outputs, OpenTelemetry collectors, and synthetic canary scripts.
- Flow: k6 probes hit endpoints, collectors correlate traces/metrics/logs, dashboards show burn rates per region.
- Run: make lint then k6 run tests/canary.js
- Operate: Rotate API tokens, schedule canaries hourly, and refresh dashboards with new SLOs each quarter.
