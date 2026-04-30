# Portfolio Monorepo

Welcome to the **portfolio** monorepo. This project bundles a FastAPI backend, a React + Vite frontend, Terraform infrastructure, containerization assets, observability tooling, and CI/CD automation. The repo is intentionally lightweight yet runnable, providing a production-ready skeleton with batteries included.

## Features
- **Backend**: FastAPI 3.11 async stack with JWT auth, SQLAlchemy, Alembic migrations, and pytest coverage.
- **Frontend**: React 18 + TypeScript + Tailwind with routing, API hooks, and a simple dashboard UI.
- **Infrastructure**: Terraform with remote state, modular VPC, Docker Compose, and a Helm chart skeleton for Kubernetes deployments.
- **Security & Quality**: Ruff, Bandit, ESLint, Prettier, tfsec, tflint, trivy, and npm audit integration.
- **CI/CD**: GitHub Actions pipeline covering linting, testing, building, security scanning, container publishing, Helm-based staging deploy, k6 performance testing, and production release tagging.
- **Observability**: Prometheus/Grafana/Loki placeholders with dashboard templates.
- **Runbooks**: Day-to-day operational guides, backup/restore playbooks, and an incident response checklist.

## Getting Started
1. **Install prerequisites**
   - Python 3.11+
   - Node.js 18+
   - Docker & Docker Compose
   - Terraform 1.6+
2. **Bootstrap tooling**
   ```bash
   make dev
   ```
3. **Run tests**
   ```bash
   make test
   ```
4. **Format code**
   ```bash
   make fmt
   ```

For more detailed instructions see the documents under `docs/` and runbooks within `docs/runbooks/`.

## Repository Layout
```
portfolio/
├─ backend/        # FastAPI service
├─ frontend/       # React SPA
├─ infra/          # Terraform modules and remote state config
├─ compose/        # Docker Compose orchestrations
├─ tools/          # Observability, Helm chart, performance scripts
├─ docs/           # Architecture docs and runbooks
└─ scripts/        # Automation helpers
```

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for workflow and coding standards.
