# Project 3: Kubernetes CI/CD Pipeline

Declarative delivery pipeline with GitHub Actions, ArgoCD, and progressive delivery strategies.

## Contents
- GitHub Actions workflow in [`pipelines/github-actions.yaml`](pipelines/github-actions.yaml) running build, test, and manifest promotion.
- ArgoCD application manifest [`pipelines/argocd-app.yaml`](pipelines/argocd-app.yaml) wiring repo to cluster namespace.
- Argo Rollout canary example in [`manifests/rollout.yaml`](manifests/rollout.yaml).
- Progressive delivery alert rules in [`monitoring/argo-alerts.yml`](monitoring/argo-alerts.yml).
- Tests verifying pipeline manifests in [`tests/test_pipelines.py`](tests/test_pipelines.py).
- Operations guide in [`RUNBOOK.md`](RUNBOOK.md) and architecture notes in [`wiki/overview.md`](wiki/overview.md).
