# Project 3: Kubernetes CI/CD Pipeline

Declarative delivery pipeline with GitHub Actions, ArgoCD, and progressive delivery strategies.

## Contents
- `pipelines/github-actions.yaml` — build/test/deploy workflow.
- `pipelines/argocd-app.yaml` — GitOps application manifest.

## Phase 1 Architecture Diagram

![Kubernetes CI/CD – Phase 1](render locally to PNG; output is .gitignored)

- **Context**: Source commits trigger GitHub Actions builds, Trivy image scans, and artifact publishing before ArgoCD promotes tags across dev, staging, and production clusters.
- **Decision**: Keep developer workspaces, pipeline services, and runtime clusters in distinct trust boundaries with health feedback closing the loop before promotion.
- **Consequences**: Progressive delivery stays guarded by environment-specific signals, and the registry remains the single promotion artifact source. Update the [Mermaid source](assets/diagrams/architecture.mmd) when flows or environments change.
