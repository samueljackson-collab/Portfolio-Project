# Contributing Guide

Thank you for your interest in contributing! This repository demonstrates production-ready workflows; please take a moment to review the standards below.

## Development Environment
1. Install Python 3.11, Node.js 18+, Docker, Docker Compose, and Terraform 1.6+.
2. Create and activate a Python virtual environment.
3. Install dependencies with `make setup-py` and `npm install` inside `projects/frontend`.
4. Copy `.env.example` files to `.env` and adjust secrets for your environment.

## Branching & Workflow
- Use feature branches prefixed with `feat/`, `fix/`, or `chore/`.
- Submit pull requests with a clear summary, linked issues, and updated documentation/tests when applicable.
- Ensure CI passes before requesting review.

## Coding Standards
- Python: `ruff`, `black`, and `isort` enforce linting/formatting.
- JavaScript/TypeScript: `eslint` and `prettier` ensure consistency.
- Terraform: `terraform fmt`, `tflint`, and `tfsec` maintain infrastructure quality.
- Shell/PowerShell scripts should be idempotent and shellcheck compliant.

## Testing Expectations
- Write unit and integration tests for new functionality.
- Maintain or exceed 80% coverage for the backend service.
- Include frontend component tests for UI logic.

## Documentation
- Update README, runbooks, and architecture diagrams when behavior changes.
- Record notable updates in `CHANGELOG.md`.

By contributing, you agree to abide by the [Code of Conduct](./CODE_OF_CONDUCT.md).
