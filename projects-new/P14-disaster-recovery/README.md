# P14: Disaster Recovery

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


Backup/restore workflows with automated failover drills.

## What this pack includes
- Standard documentation set (architecture, testing, playbook, SOP, RUNBOOKS, ADRS, THREAT_MODEL, RISK_REGISTER).
- A tiny producer/job/consumer pipeline to demonstrate executable artifacts.
- Kubernetes deployment stub showing how to package the worker.

## Quick start
```bash
cd /workspace/Portfolio-Project/projects-new/P14-disaster-recovery
python docker/producer/main.py --validate
python docker/producer/main.py --payload '{"event":"demo"}'
```

## Deliverables
- Evidence files land in `artifacts/` for easy inspection.
- Report templates are stored in `REPORT_TEMPLATES/`.
- Metrics guidance captured under `METRICS/`.
# P14 Disaster Recovery Drill Demo

Shows a backup → restore → verification sequence with a mock RTO value.

## Run locally
```bash
python app.py
cat artifacts/dr_runbook.txt
```

## Build and run with Docker
```bash
docker build -t p14-disaster-recovery .
docker run --rm p14-disaster-recovery
```

## Run in Kubernetes
Push your image, update `k8s-demo.yaml`, then:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/dr_runbook.txt` captures the drill log, including backup name and verification.
