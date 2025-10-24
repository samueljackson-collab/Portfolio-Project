# Architecture Overview

The portfolio platform is implemented as a service-oriented monorepo with shared tooling.

- **Backend:** FastAPI application that surfaces project metadata via REST endpoints.
- **Frontend:** React + Vite single-page application consuming backend APIs and rendering showcase components.
- **Infrastructure:** Terraform and CloudFormation templates provision runtime environments. Docker Compose and Kubernetes manifests enable local and cluster deployments.
- **Observability:** Health probes, logging configuration, and integration points for metrics exporters.

## Component Diagram
```
[Browser] --HTTP--> [Frontend SPA] --REST--> [FastAPI Backend] --IaC--> [Cloud Infrastructure]
```

## Data Flow
1. Frontend requests `/api/projects` from the backend.
2. Backend returns curated project metadata (seeded from `data/seed_projects.json`).
3. Frontend renders responsive tiles and integrates with telemetry endpoints defined via environment variables.

## Quality Gates
- Ruff enforces Python styling.
- ESLint + Prettier enforce TypeScript styling.
- Pytest and Vitest ensure 80% coverage.
- GitHub Actions workflows orchestrate linting, testing, and security scans (bandit, npm audit, trivy hooks).
