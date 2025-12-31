# P24: Report Generator Platform

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


Composable reporting jobs with templated outputs and schedulable runs.

## What this pack includes
- Standard documentation set (architecture, testing, playbook, SOP, RUNBOOKS, ADRS, THREAT_MODEL, RISK_REGISTER).
- A tiny producer/job/consumer pipeline to demonstrate executable artifacts.
- Kubernetes deployment stub showing how to package the worker.

## Quick start
```bash
cd /workspace/Portfolio-Project/projects-new/P24-report-generator
python docker/producer/main.py --validate
python docker/producer/main.py --payload '{"event":"demo"}'
```

## Deliverables
- Evidence files land in `artifacts/` for easy inspection.
- Report templates are stored in `REPORT_TEMPLATES/`.
- Metrics guidance captured under `METRICS/`.
# P24 Report Generator Demo

Renders a concise executive summary with key metrics to mimic a templated report workflow.

## Run locally
```bash
python app.py
cat artifacts/summary_report.txt
```

## Build and run with Docker
```bash
docker build -t p24-report-generator .
docker run --rm p24-report-generator
```

## Run in Kubernetes
Push the image, set it in `k8s-demo.yaml`, then apply:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/summary_report.txt` contains the generated report contents.
