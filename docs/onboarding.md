# Onboarding Guide

Welcome to the portfolio monorepo! This document walks through environment setup, service overviews, and day-one productivity tips.

## 1. Prerequisites
- macOS, Linux, or Windows (WSL2 recommended).
- Docker Desktop 4.x or Docker Engine 24+.
- Python 3.11 with `pip`.
- Node.js 20 LTS (ships with npm 10).
- Terraform 1.6+.
- AWS CLI v2 configured with appropriate credentials.

## 2. Setup Steps

```bash
git clone git@github.com:samuelsre/portfolio-monorepo.git
cd portfolio-monorepo
./setup.sh
```

The setup script installs Python/Node dependencies, configures pre-commit hooks, and scaffolds local environment files.

## 3. Running the Stack Locally

```bash
make dev
```

This command launches PostgreSQL, the backend API, the frontend SPA, and the monitoring stack. Visit:
- Backend: http://localhost:8000/docs
- Frontend: http://localhost:5173
- Grafana: http://localhost:3000 (default creds `admin` / `admin`)

## 4. Environment Configuration

- Copy `.env.example` files to `.env` in service directories for local overrides.
- Update `DATABASE_URL` if you prefer running PostgreSQL outside Docker.
- Configure AWS credentials for Terraform operations with `aws configure`.

## 5. Development Workflow

1. Create a feature branch using Conventional Commit keywords.
2. Write code alongside documentation and ADR updates.
3. Execute `make ci` before pushing to catch lint/test failures early.
4. Open a pull request and request review from `@platform-leads`.

## 6. Troubleshooting

| Symptom | Resolution |
| --- | --- |
| Backend cannot connect to DB | Ensure Docker container `db` is running and credentials match `.env`. |
| Frontend fails to fetch API | Check `VITE_API_URL` environment variable and confirm backend port mapping. |
| Terraform init fails | Verify AWS credentials and bucket/prefix permissions. |
| Pre-commit takes too long | Use `SKIP=checkov pre-commit run --all-files` for quicker iteration. |

## 7. Additional Resources
- [`docs/architecture.md`](architecture.md) – detailed diagrams and design rationales.
- [`docs/deployment.md`](deployment.md) – runbooks for staging/production deployments.
- [`docs/testing.md`](testing.md) – test pyramid and execution instructions.

