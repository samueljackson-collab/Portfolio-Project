# P22 Autonomous DevOps Demo

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


Detects a mock incident and triggers an automated remediation to represent closed-loop operations.

## Run locally
```bash
python app.py
cat artifacts/self_heal.log
```

## Build and run with Docker
```bash
docker build -t p22-autonomous-devops .
docker run --rm p22-autonomous-devops
```

## Run in Kubernetes
Publish your image, set it in `k8s-demo.yaml`, then:
```bash
kubectl apply -f k8s-demo.yaml
kubectl logs job/demo-job
```

Artifacts: `artifacts/self_heal.log` shows the detected issue and remediation action.
