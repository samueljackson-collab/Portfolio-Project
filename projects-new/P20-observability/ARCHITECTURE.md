# Observability Engineering Architecture

- **Pattern:** Prometheus/Grafana/Loki signals with synthetic checks and tracing stubs.
- **Data flow:** Producer writes artifacts, job stage enriches them, and consumer prints a digest.
- **Execution:** Run `python docker/producer/main.py` to emit an event and process it locally.
- **Kubernetes:** `k8s/deployment.yaml` shows a minimal worker Deployment for demo purposes.
