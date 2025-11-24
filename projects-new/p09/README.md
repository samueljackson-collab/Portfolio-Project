# P09 Cloud-Native POC
Blueprint for rapidly proving out cloud-native services with GitOps-friendly manifests, observability defaults, and security guardrails.

## Highlights
- Containerized reference app (producer/consumer) with IaC-ready manifests.
- Runbooks, SOPs, threat model, and risk register for production readiness.

## Quick start
```sh
docker compose -f docker/docker-compose.yml up --build
kubectl apply -f k8s/ -n cloud-poc
```
