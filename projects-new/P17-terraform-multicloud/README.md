# P17: Terraform Multi-Cloud

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


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
# P17 Terraform Multi-Cloud Demo

Mocks a Terraform plan/apply across AWS and Azure resources to demonstrate workflow orchestration.

## Run locally
```bash
python app.py
cat artifacts/terraform_plan.json
```

## Build and run with Docker
```bash
docker build -t p17-terraform-multicloud .
docker run --rm p17-terraform-multicloud
```

## Run in Kubernetes
Push the image, set `image:` in `k8s-demo.yaml`, then:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/terraform_plan.json` contains the mock plan and apply summary with the resource count.
