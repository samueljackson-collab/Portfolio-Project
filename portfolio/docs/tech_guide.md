# Technical Guide

## Prerequisites
- Python 3.11+
- Node.js 20+
- Docker 24+
- Terraform 1.6+
- AWS CLI (for CloudFormation workflows)

## Setup
1. Clone repository and enter `portfolio/` directory.
2. Copy `.env.example` to `.env` and adjust values.
3. Run `make bootstrap` to install backend and frontend dependencies.
4. Activate pre-commit hooks with `pre-commit install` (optional but recommended).

## Development Workflow
- **Linting:** `make lint` ensures Python and TypeScript code quality.
- **Testing:** `make test` executes pytest (with coverage) and Vitest suites.
- **Formatting:** `make format` applies Ruff and Prettier formatters.
- **Running Services:** `make start-backend` and `make start-frontend` for local dev or `docker compose up --build` for containerized stack.

## Continuous Integration
GitHub Actions workflows (`.github/workflows/ci.yml`) enforce linting, testing, coverage thresholds, and security scans on every push and pull request.

## Infrastructure Management
- **Terraform:** Update variables in `tools/terraform/variables.tf` and apply via `terraform init && terraform apply`.
- **CloudFormation:** Deploy stack using `aws cloudformation deploy --template-file tools/cloudformation/template.yaml --stack-name portfolio`.

## Maintenance
- Review `ROADMAP.md` and `STATUS_BOARD.md` to track priorities.
- Update `CHANGELOG.md` for notable changes.
- Run `make security-check` monthly and after dependency updates.
