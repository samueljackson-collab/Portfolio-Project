# P15: Cloud Cost Optimization

CUR-backed analytics with tagging compliance and savings plan insights.

## What this pack includes
- Standard documentation set (architecture, testing, playbook, SOP, RUNBOOKS, ADRS, THREAT_MODEL, RISK_REGISTER).
- A tiny producer/job/consumer pipeline to demonstrate executable artifacts.
- Kubernetes deployment stub showing how to package the worker.

## Quick start
```bash
cd /workspace/Portfolio-Project/projects-new/P15-cost-optimization
python docker/producer/main.py --validate
python docker/producer/main.py --payload '{"event":"demo"}'
```

## Deliverables
- Evidence files land in `artifacts/` for easy inspection.
- Report templates are stored in `REPORT_TEMPLATES/`.
- Metrics guidance captured under `METRICS/`.
# P15 Cost Optimization Demo

Calculates projected savings from rightsizing and spot instances to illustrate a FinOps playbook.

## Run locally
```bash
python app.py
cat artifacts/cost_report.json
```

## Build and run with Docker
```bash
docker build -t p15-cost-optimization .
docker run --rm p15-cost-optimization
```

## Run in Kubernetes
Push the image, set `image:` in `k8s-demo.yaml`, then apply:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/cost_report.json` lists the spend baseline and calculated net savings.
