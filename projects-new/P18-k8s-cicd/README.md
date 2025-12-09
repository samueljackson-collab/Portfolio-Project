# P18 Kubernetes CI/CD Demo

Simulates a pipeline that builds, tests, pushes an image, and applies Kubernetes manifests.

## Run locally
```bash
python app.py
cat artifacts/pipeline_run.txt
```

## Build and run with Docker
```bash
docker build -t p18-k8s-cicd .
docker run --rm p18-k8s-cicd
```

## Run in Kubernetes
Push your image, set it in `k8s-demo.yaml`, then apply:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/pipeline_run.txt` shows each pipeline stage with timestamps.
