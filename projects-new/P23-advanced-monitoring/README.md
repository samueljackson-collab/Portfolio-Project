# P23: Advanced Monitoring

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


SLO-first monitoring stack with anomaly detection hooks.

## What this pack includes
- Standard documentation set (architecture, testing, playbook, SOP, RUNBOOKS, ADRS, THREAT_MODEL, RISK_REGISTER).
- A tiny producer/job/consumer pipeline to demonstrate executable artifacts.
- Kubernetes deployment stub showing how to package the worker.

## Quick start
```bash
cd /workspace/Portfolio-Project/projects-new/P23-advanced-monitoring
python docker/producer/main.py --validate
python docker/producer/main.py --payload '{"event":"demo"}'
```

## Deliverables
- Evidence files land in `artifacts/` for easy inspection.
- Report templates are stored in `REPORT_TEMPLATES/`.
- Metrics guidance captured under `METRICS/`.
# P23 Advanced Monitoring Demo

Evaluates metric thresholds to generate alert summaries for CPU and error-rate anomalies.

## Run locally
```bash
python app.py
cat artifacts/alert_summary.json
```

## Build and run with Docker
```bash
docker build -t p23-advanced-monitoring .
docker run --rm p23-advanced-monitoring
```

## Run in Kubernetes
Push your image, update `k8s-demo.yaml`, then apply:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/alert_summary.json` lists triggered alerts and the total count.
