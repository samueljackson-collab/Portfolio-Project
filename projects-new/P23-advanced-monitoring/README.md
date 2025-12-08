# P23 Advanced Monitoring Demo

Evaluates metric thresholds to generate alert summaries for CPU and error-rate anomalies.

## Run locally
```bash
python app.py
cat artifacts/alert_summary.json
```

## Build and run with Docker
```bash
docker build -t p23-advanced-monitoring .
docker run --rm p23-advanced-monitoring
```

## Run in Kubernetes
Push your image, update `k8s-demo.yaml`, then apply:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/alert_summary.json` lists triggered alerts and the total count.
