# P09 Cloud-Native POC Pack

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
# Create secrets first (see k8s/SECRETS.md for details)
./k8s/setup-k8s-auth.sh

# Then apply base configuration
kubectl apply -k k8s/
```
