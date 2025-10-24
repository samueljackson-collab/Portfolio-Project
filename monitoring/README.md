# Monitoring Service

Lightweight FastAPI application exposing Prometheus metrics for portfolio services.

## Metrics
- `request_count` – total requests handled by the backend.
- `request_duration_seconds` – histogram of request latency.
- `active_users` – gauge reflecting current authenticated sessions.

## Run Locally

```bash
uvicorn app.main:app --reload --port 9100
```

## Grafana
Dashboards are stored under `grafana/dashboards/` and can be imported into Grafana to visualize core SLOs.

