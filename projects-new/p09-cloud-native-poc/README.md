# Cloud-Native PoC (Incubating)

This incubating pack tracks operational assets for the cloud-native proof of concept before promotion into the main portfolio.

## SOP Library
- [`SOP/deployment-validation-and-rollback.md`](./SOP/deployment-validation-and-rollback.md) — validation workflow and rollback steps for each rollout.

## Scheduled Jobs
- [`jobs/health-probe.cron.yaml`](./jobs/health-probe.cron.yaml) — Kubernetes `CronJob` that runs [`health_probe.py`](./jobs/health_probe.py) every 5 minutes to verify the service health endpoint and latency budget.

### Running the health probe locally
```bash
PROBE_URL=http://localhost:8080/healthz \
MAX_LATENCY_MS=500 \
python projects-new/p09-cloud-native-poc/jobs/health_probe.py
```

Apply the scheduled job to a cluster:
```bash
kubectl apply -f projects-new/p09-cloud-native-poc/jobs/health-probe.cron.yaml
```
