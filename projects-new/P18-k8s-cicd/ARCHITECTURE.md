# Architecture

Stack: Kind, ArgoCD, kustomize, Trivy, and GitHub Actions.

Data/Control flow: CI builds container, runs tests and Trivy, pushes to registry, ArgoCD watches manifests and syncs to cluster.

Dependencies:
- Env/config: see README for required secrets and endpoints.
