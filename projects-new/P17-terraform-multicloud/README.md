# P17: Terraform Multi-Cloud

Modular Terraform targeting AWS/Azure with shared variables and CI validation.

## What this pack includes
- Standard documentation set (architecture, testing, playbook, SOP, RUNBOOKS, ADRS, THREAT_MODEL, RISK_REGISTER).
- A tiny producer/job/consumer pipeline to demonstrate executable artifacts.
- Kubernetes deployment stub showing how to package the worker.

## Quick start
```bash
cd /workspace/Portfolio-Project/projects-new/P17-terraform-multicloud
python docker/producer/main.py --validate
python docker/producer/main.py --payload '{"event":"demo"}'
```

## Deliverables
- Evidence files land in `artifacts/` for easy inspection.
- Report templates are stored in `REPORT_TEMPLATES/`.
- Metrics guidance captured under `METRICS/`.
