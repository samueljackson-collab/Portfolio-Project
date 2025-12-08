# P24 Report Generator Demo

Renders a concise executive summary with key metrics to mimic a templated report workflow.

## Run locally
```bash
python app.py
cat artifacts/summary_report.txt
```

## Build and run with Docker
```bash
docker build -t p24-report-generator .
docker run --rm p24-report-generator
```

## Run in Kubernetes
Push the image, set it in `k8s-demo.yaml`, then apply:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/summary_report.txt` contains the generated report contents.
