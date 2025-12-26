# P25: Portfolio Website Experience

Static+API hybrid site with content build pipeline and uptime probes.

## What this pack includes
- Standard documentation set (architecture, testing, playbook, SOP, RUNBOOKS, ADRS, THREAT_MODEL, RISK_REGISTER).
- A tiny producer/job/consumer pipeline to demonstrate executable artifacts.
- Kubernetes deployment stub showing how to package the worker.

## Quick start
```bash
cd /workspace/Portfolio-Project/projects-new/P25-portfolio-website
python docker/producer/main.py --validate
python docker/producer/main.py --payload '{"event":"demo"}'
```

## Deliverables
- Evidence files land in `artifacts/` for easy inspection.
- Report templates are stored in `REPORT_TEMPLATES/`.
- Metrics guidance captured under `METRICS/`.
# P25 Portfolio Website Demo

Builds a tiny JSON snapshot of site pages to represent a static site generation step.

## Run locally
```bash
python app.py
cat artifacts/site_snapshot.json
```

## Build and run with Docker
```bash
docker build -t p25-portfolio-website .
docker run --rm p25-portfolio-website
```

## Run in Kubernetes
Push your image, update `k8s-demo.yaml`, then:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/site_snapshot.json` captures the generated pages and deployment flag.
