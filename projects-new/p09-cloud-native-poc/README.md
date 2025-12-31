# P09 Cloud-Native POC Pack

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../DOCUMENTATION_INDEX.md).


Artifacts for demonstrating a minimal FastAPI service with cloud-native patterns. Includes architecture docs, testing plans, operational guides, and runnable manifests mirroring the P06 prompt-pack layout.

## Scope
- FastAPI service exposing health and todo endpoints.
- Container/Docker Compose and Kubernetes manifests.
- Observability hooks (metrics, logs) and deployment runbooks.

## Quickstart
```bash
python producer/app.py --port 8000
python consumer/checks.py --base-url http://localhost:8000
```

Compose:
```bash
docker compose -f docker/compose.poc.yaml up --build
```

K8s:
```bash
kubectl apply -f k8s/base.yaml --dry-run=client
```
