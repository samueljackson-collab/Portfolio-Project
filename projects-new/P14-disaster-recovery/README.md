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
