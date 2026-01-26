# P13: High-Availability Web App

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


NGINX front-end with replicated app tier and resilient session handling.

## What this pack includes
- Standard documentation set (architecture, testing, playbook, SOP, RUNBOOKS, ADRS, THREAT_MODEL, RISK_REGISTER).
- A tiny producer/job/consumer pipeline to demonstrate executable artifacts.
- Kubernetes deployment stub showing how to package the worker.

## Quick start
```bash
cd /workspace/Portfolio-Project/projects-new/P13-ha-webapp
python docker/producer/main.py --validate
python docker/producer/main.py --payload '{"event":"demo"}'
```

## Deliverables
- Evidence files land in `artifacts/` for easy inspection.
- Report templates are stored in `REPORT_TEMPLATES/`.
- Metrics guidance captured under `METRICS/`.
# P13 High-Availability Web App Demo

Emulates a primary/replica pair and shows a failover when the primary is unhealthy.

## Run locally
```bash
python app.py
cat artifacts/ha_healthcheck.txt
```

## Build and run with Docker
```bash
docker build -t p13-ha-webapp .
docker run --rm p13-ha-webapp
```

## Run in Kubernetes
Set your pushed image in `k8s-demo.yaml` and apply:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/ha_healthcheck.txt` records the failover decision and promotion steps.
