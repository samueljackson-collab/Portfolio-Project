# P20: Observability Engineering

Prometheus/Grafana/Loki signals with synthetic checks and tracing stubs.

## What this pack includes
- Standard documentation set (architecture, testing, playbook, SOP, RUNBOOKS, ADRS, THREAT_MODEL, RISK_REGISTER).
- A tiny producer/job/consumer pipeline to demonstrate executable artifacts.
- Kubernetes deployment stub showing how to package the worker.

## Quick start
```bash
cd /workspace/Portfolio-Project/projects-new/P20-observability
python docker/producer/main.py --validate
python docker/producer/main.py --payload '{"event":"demo"}'
```

## Deliverables
- Evidence files land in `artifacts/` for easy inspection.
- Report templates are stored in `REPORT_TEMPLATES/`.
- Metrics guidance captured under `METRICS/`.
# P20 Observability Demo

Collects a minimal bundle of metrics, logs, and traces to demonstrate telemetry export.

## Run locally
```bash
python app.py
cat artifacts/telemetry_bundle.json
```

## Build and run with Docker
```bash
docker build -t p20-observability .
docker run --rm p20-observability
```

## Run in Kubernetes
Push your image and update `k8s-demo.yaml`, then:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/telemetry_bundle.json` contains the collected metrics, logs, and trace IDs.
