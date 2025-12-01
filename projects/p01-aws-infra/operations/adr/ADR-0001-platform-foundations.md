# ADR-0001: Platform Foundations for PRJ-AWS-001

## Status
Accepted

## Context
The project lacked a structured way to validate infrastructure and application components together. We needed a common baseline for backend, frontend, and orchestration code plus containerization assets to exercise deployments in CI/CD.

## Decision
- Introduce FastAPI backend and React/Vite frontend scaffolds under `src/` to provide integration points for AWS drift detection and environment metadata.
- Add Dockerfiles, Helm defaults, and Kubernetes manifests under `infrastructure/` to standardize container builds and cluster rollout.
- Provide observability rules and dashboards under `operations/observability` for golden-signal coverage of the new services.

## Consequences
- Developers can run end-to-end smoke tests locally and in CI using the same images.
- Observability and operations artifacts are versioned with the code, improving auditability.
- Future ADRs can extend deployment strategies (e.g., blue/green) without reworking the baseline layout.
