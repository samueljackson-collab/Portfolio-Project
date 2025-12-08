# P15 Cost Optimization Demo

Calculates projected savings from rightsizing and spot instances to illustrate a FinOps playbook.

## Run locally
```bash
python app.py
cat artifacts/cost_report.json
```

## Build and run with Docker
```bash
docker build -t p15-cost-optimization .
docker run --rm p15-cost-optimization
```

## Run in Kubernetes
Push the image, set `image:` in `k8s-demo.yaml`, then apply:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/cost_report.json` lists the spend baseline and calculated net savings.
