# Runbook: Deploy Cloud-Native POC

1. **Build Image**: `docker build -t poc-api:latest -f docker/Dockerfile ..`
2. **Apply K8s Manifests**: `kubectl apply -f k8s/base.yaml`
3. **Wait for Readiness**: `kubectl wait --for=condition=ready pod -l app=poc-api --timeout=120s`
4. **Smoke Test**: `python consumer/checks.py --base-url http://localhost:8000` (port-forward if needed).
5. **Rollback**: `kubectl rollout undo deploy/poc-api` if health/latency fails.
