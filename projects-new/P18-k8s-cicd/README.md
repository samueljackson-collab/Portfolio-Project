# P18 – Kubernetes CI/CD

GitHub Actions pipelines building images, scanning, and deploying to a kind dev cluster with ArgoCD sync.

## Quick start
- Stack: Kind, ArgoCD, kustomize, Trivy, and GitHub Actions.
- Flow: CI builds container, runs tests and Trivy, pushes to registry, ArgoCD watches manifests and syncs to cluster.
- Run: make lint then make test
- Operate: Rotate registry credentials, prune old images, and monitor ArgoCD health sync status.
