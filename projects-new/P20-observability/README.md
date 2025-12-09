# P20 Observability Demo

Collects a minimal bundle of metrics, logs, and traces to demonstrate telemetry export.

## Run locally
```bash
python app.py
cat artifacts/telemetry_bundle.json
```

## Build and run with Docker
```bash
docker build -t p20-observability .
docker run --rm p20-observability
```

## Run in Kubernetes
Push your image and update `k8s-demo.yaml`, then:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/telemetry_bundle.json` contains the collected metrics, logs, and trace IDs.
