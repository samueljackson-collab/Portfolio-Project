# Kubernetes Helm Chart

## Overview
Reusable Helm chart for deploying stateless FastAPI or Rust microservices with baked-in operational best practices (probes, autoscaling, service mesh annotations).

## Features
- Configurable deployment strategies (RollingUpdate, Blue/Green via Argo Rollouts).
- Automatic sidecar injection compatibility (Istio/Linkerd).
- PodSecurity standards (restricted profile) and resource requests/limits preconfigured.
- Optional service monitors for Prometheus scraping and log shipping annotations for Loki.

## Structure
```
charts/
  └── app/
      ├── Chart.yaml
      ├── values.yaml
      └── templates/
```
Includes helper templates for environment variables, secrets, and configmaps.

## Usage
1. Package chart: `helm dependency update charts/app`.
2. Install: `helm install backend charts/app -f values.dev.yaml`.
3. Validate: `helm test backend` running smoke tests container.
4. Publish: `helm package charts/app && helm push` to OCI registry.

## Testing & Linting
- `helm lint` executed in CI.
- Unit tests with `helm-unittest` for templating logic.
- Kind-based integration tests spin up ephemeral clusters for validation.

