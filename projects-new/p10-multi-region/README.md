# P10 Multi-Region Architecture Pack

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


End-to-end documentation and runnable samples for active/passive AWS deployment demonstrations. Mirrors the P06 prompt-pack structure with architecture, testing, operations, and governance artifacts.

## Scope
- Region-paired stacks with Route 53 health checks and failover.
- Sample Terraform-style manifests (stubbed) and failover drills.
- Operational runbooks, SOPs, and risk/threat coverage.

## Quickstart
```bash
python producer/failover_sim.py --primary us-east-1 --secondary us-west-2
python consumer/validate.py --report out/failover.json
```

Compose harness for local demo DNS switch:
```bash
docker compose -f docker/compose.multi.yaml up --build
```

K8s manifests for regional services:
```bash
kubectl apply -f k8s/base.yaml --dry-run=client
```
