# P18: CI/CD + Kubernetes

GitOps-style deployment pipeline with container builds and manifest promotion.

## What this pack includes
- Standard documentation set (architecture, testing, playbook, SOP, RUNBOOKS, ADRS, THREAT_MODEL, RISK_REGISTER).
- A tiny producer/job/consumer pipeline to demonstrate executable artifacts.
- Kubernetes deployment stub showing how to package the worker.

## Quick start
```bash
cd /workspace/Portfolio-Project/projects-new/P18-k8s-cicd
python docker/producer/main.py --validate
python docker/producer/main.py --payload '{"event":"demo"}'
```

## Deliverables
- Evidence files land in `artifacts/` for easy inspection.
- Report templates are stored in `REPORT_TEMPLATES/`.
- Metrics guidance captured under `METRICS/`.
# P18 Kubernetes CI/CD Demo

Simulates a pipeline that builds, tests, pushes an image, and applies Kubernetes manifests.

## Run locally
```bash
python app.py
cat artifacts/pipeline_run.txt
```

## Build and run with Docker
```bash
docker build -t p18-k8s-cicd .
docker run --rm p18-k8s-cicd
```

## Run in Kubernetes
Push your image, set it in `k8s-demo.yaml`, then apply:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/pipeline_run.txt` shows each pipeline stage with timestamps.
