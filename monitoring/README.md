# Monitoring Service

FastAPI-based Prometheus exporter that surfaces synthetic metrics for the portfolio system. Pair with Prometheus and Grafana for end-to-end observability.

## Commands
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 9090
```

## Endpoints
- `GET /metrics` – Prometheus metrics endpoint.
- `GET /health` – Exporter health probe.

Grafana dashboards are located in `grafana/dashboards/` and Prometheus scrape configuration is under `prometheus/`.
