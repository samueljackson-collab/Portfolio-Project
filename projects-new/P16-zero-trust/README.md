# P16 Zero-Trust Policy Demo

Evaluates a simple access request against role, MFA, and network criteria to illustrate a zero-trust gateway decision.

## Run locally
```bash
python app.py
cat artifacts/policy_evaluation.json
```

## Build and run with Docker
```bash
docker build -t p16-zero-trust .
docker run --rm p16-zero-trust
```

## Run in Kubernetes
Push your image and update `k8s-demo.yaml` before applying:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/policy_evaluation.json` records the evaluated attributes and final allow/deny decision.
