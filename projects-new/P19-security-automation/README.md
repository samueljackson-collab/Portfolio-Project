# P19: Cloud Security Automation

CIS scanning, drift detection, and remediation hooks.

## What this pack includes
- Standard documentation set (architecture, testing, playbook, SOP, RUNBOOKS, ADRS, THREAT_MODEL, RISK_REGISTER).
- A tiny producer/job/consumer pipeline to demonstrate executable artifacts.
- Kubernetes deployment stub showing how to package the worker.

## Quick start
```bash
cd /workspace/Portfolio-Project/projects-new/P19-security-automation
python docker/producer/main.py --validate
python docker/producer/main.py --payload '{"event":"demo"}'
```

## Deliverables
- Evidence files land in `artifacts/` for easy inspection.
- Report templates are stored in `REPORT_TEMPLATES/`.
- Metrics guidance captured under `METRICS/`.
# P19 Security Automation Demo

Runs a few compliance checks (CIS controls and GuardDuty enablement) and reports pass/fail counts.

## Run locally
```bash
python app.py
cat artifacts/compliance_report.json
```

## Build and run with Docker
```bash
docker build -t p19-security-automation .
docker run --rm p19-security-automation
```

## Run in Kubernetes
Push the image, update `k8s-demo.yaml`, then apply:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/compliance_report.json` records which checks failed and the total pass count.
