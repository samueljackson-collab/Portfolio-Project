# Portfolio Monorepo

The Portfolio Monorepo packages five production-ready services, shared infrastructure-as-code, and comprehensive documentation showcasing the systems development engineering work of **Samuel Jackson**. It is designed as a reference implementation for secure, observable, and automated cloud-native delivery.

## Services

| Service | Stack | Description |
|---------|-------|-------------|
| `backend` | FastAPI, PostgreSQL, JWT | REST API with authentication, content management, and Alembic migrations. |
| `frontend` | React, Vite, Tailwind CSS | Single-page application that consumes the backend API with protected routes. |
| `e2e-tests` | Postman, k6, OWASP ZAP | Automated end-to-end, load, and security testing assets. |
| `infra` | Terraform 1.5+, AWS | Multi-environment infrastructure modules with network, compute, and storage stacks. |
| `monitoring` | FastAPI, Prometheus, Grafana | Metrics exporter and dashboards for observability. |

The repository also contains reusable tooling (`tools/`), packaging scripts (`scripts/`), and extensive documentation (`docs/`) for onboarding, deployment, and architecture.

## Quickstart

1. **Clone the repository**
   ```bash
   git clone https://github.com/sams-jackson/portfolio-monorepo.git
   cd portfolio-monorepo
   ```
2. **Install tooling**
   ```bash
   pip install -r requirements.txt
   npm install
   pre-commit install
   ```
3. **Launch the dev environment**
   ```bash
   make dev
   ```
   The command starts the backend, frontend, monitoring exporter, Prometheus, Grafana, and PostgreSQL using Docker Compose.

See [`docs/onboarding.md`](./docs/onboarding.md) for detailed environment setup and [`docs/deployment.md`](./docs/deployment.md) for release guidance.

## Repository Layout

```
backend/      FastAPI application, migrations, tests
frontend/     React SPA with Tailwind styling
infra/        Terraform modules and environments
monitoring/   Metrics exporter and observability configuration
e2e-tests/    End-to-end, load, and security suites
scripts/      Packaging and setup helpers
tools/        Automation utilities for manifests, status, and versioning
docs/         Architecture, onboarding, deployment, and contribution guides
.github/      CI/CD pipelines and issue templates
```

## Contributing

Contributions are welcome! Review [`CONTRIBUTING.md`](./CONTRIBUTING.md) for coding standards, branching strategy, and pull request expectations. All commits must pass linting, formatting, security scanning, and unit/integration tests enforced by the CI pipeline.

## License

This project is licensed under the MIT License. See [`LICENSE`](./LICENSE) for details.
