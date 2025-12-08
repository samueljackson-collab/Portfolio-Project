# P20 – Observability Stack

Prometheus/Grafana/Loki stack with Alertmanager and dashboard exports.

## Quick start
- Stack: Docker Compose with Prometheus, Grafana, Loki, Promtail, and Alertmanager.
- Flow: Promtail ships logs, Prometheus scrapes app/infra metrics, dashboards visualize SLOs, Alertmanager routes incidents.
- Run: make lint-config then make test-rules
- Operate: Refresh scrape targets weekly, rotate Alertmanager receivers tokens, and backup Grafana via API.
