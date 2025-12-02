# P08 Backend API Testing Pack

Complete artifact bundle for API regression and contract testing. Designed to align with the P06 prompt-pack layout and ready for Postman/Newman CI, Kubernetes smoke tests, and on-call operations.

## Scope
- OpenAPI-driven contract checks and schema drift detection.
- Postman collections with Newman runners and synthetic data loaders.
- K8s/Compose harness for ephemeral environments.
- Operational documentation, risk/threat coverage, and metrics.

## Quickstart
```bash
npm install -g newman
newman run producer/collections/core.postman_collection.json -e producer/env/local.postman_environment.json
python consumer/report.py --input out/newman-report.json
```

Compose harness:
```bash
docker compose -f docker/compose.api.yaml up --build
```

Kubernetes dry run:
```bash
kubectl apply -k k8s/overlays/dev --dry-run=client
```
