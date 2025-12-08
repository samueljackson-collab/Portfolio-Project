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
