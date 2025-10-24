# CI/CD Pipeline for Backend API

## Overview
GitLab CI pipeline-as-code for the FastAPI backend. Demonstrates reusable stages, security scanning, and deployment automation across environments.

## Pipeline Stages
1. **Prepare** – Checkout, install dependencies, cache artifacts.
2. **Lint & Type Check** – Run `ruff`, `black --check`, `mypy`.
3. **Unit Tests** – Execute `pytest` with coverage thresholds enforced.
4. **Integration Tests** – Spin up Postgres & Kafka using docker compose for contract tests.
5. **Security Scans** – Run Bandit, Trivy image scan, dependency review.
6. **Build & Package** – Build Docker image, push to registry with semantic tags.
7. **Deploy** – Trigger Argo CD sync or Helm release via GitOps manifest updates.
8. **Post-Deploy Verification** – Run smoke tests and health checks.

## Key Files
- `.gitlab-ci.yml` – Entry pipeline referencing templates under `.ci/templates/`.
- `scripts/` – Helper scripts for migrations, seed data, rollback.
- `environments/` – Variables and manifests per environment.

## Governance
- Merge request template enforces deployment checklist.
- Approval rules require Security + QA sign-off for staging/prod.
- Pipeline metrics exported to Grafana via GitLab API integration.

