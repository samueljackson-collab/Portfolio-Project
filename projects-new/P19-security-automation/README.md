# P19 Security Automation Demo

Runs a few compliance checks (CIS controls and GuardDuty enablement) and reports pass/fail counts.

## Run locally
```bash
python app.py
cat artifacts/compliance_report.json
```

## Build and run with Docker
```bash
docker build -t p19-security-automation .
docker run --rm p19-security-automation
```

## Run in Kubernetes
Push the image, update `k8s-demo.yaml`, then apply:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/compliance_report.json` records which checks failed and the total pass count.
