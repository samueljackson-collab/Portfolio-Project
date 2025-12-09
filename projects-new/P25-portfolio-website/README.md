# P25 Portfolio Website Demo

Builds a tiny JSON snapshot of site pages to represent a static site generation step.

## Run locally
```bash
python app.py
cat artifacts/site_snapshot.json
```

## Build and run with Docker
```bash
docker build -t p25-portfolio-website .
docker run --rm p25-portfolio-website
```

## Run in Kubernetes
Push your image, update `k8s-demo.yaml`, then:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/site_snapshot.json` captures the generated pages and deployment flag.
