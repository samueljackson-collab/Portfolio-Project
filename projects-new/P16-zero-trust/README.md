# P16: Zero-Trust Architecture

Policy-driven access controls with mutual TLS enforcement and service posture checks.

## What this pack includes
- Standard documentation set (architecture, testing, playbook, SOP, RUNBOOKS, ADRS, THREAT_MODEL, RISK_REGISTER).
- A tiny producer/job/consumer pipeline to demonstrate executable artifacts.
- Kubernetes deployment stub showing how to package the worker.

## Quick start
```bash
cd /workspace/Portfolio-Project/projects-new/P16-zero-trust
python docker/producer/main.py --validate
python docker/producer/main.py --payload '{"event":"demo"}'
```

## Deliverables
- Evidence files land in `artifacts/` for easy inspection.
- Report templates are stored in `REPORT_TEMPLATES/`.
- Metrics guidance captured under `METRICS/`.
# P16 Zero-Trust Policy Demo

Evaluates a simple access request against role, MFA, and network criteria to illustrate a zero-trust gateway decision.

## Run locally
```bash
python app.py
cat artifacts/policy_evaluation.json
```

## Build and run with Docker
```bash
docker build -t p16-zero-trust .
docker run --rm p16-zero-trust
```

## Run in Kubernetes
Push your image and update `k8s-demo.yaml` before applying:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/policy_evaluation.json` records the evaluated attributes and final allow/deny decision.
