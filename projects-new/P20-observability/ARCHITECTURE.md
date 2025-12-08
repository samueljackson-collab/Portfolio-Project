# Architecture

Stack: Docker Compose with Prometheus, Grafana, Loki, Promtail, and Alertmanager.

Data/Control flow: Promtail ships logs, Prometheus scrapes app/infra metrics, dashboards visualize SLOs, Alertmanager routes incidents.

Dependencies:
- Docker Compose with Prometheus, Grafana, Loki, Promtail, and Alertmanager.
- Env/config: see README for required secrets and endpoints.
