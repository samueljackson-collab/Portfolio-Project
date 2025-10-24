# Contributing Guide

Thank you for your interest in contributing! This monorepo intentionally mirrors production-style practices so contributors can demonstrate operational rigor.

## Development Workflow

1. Fork the repository and create a feature branch with a descriptive name (`feature/content-crud`).
2. Install dependencies via `make bootstrap` (or manually follow README instructions).
3. Ensure code quality with `make fmt` and `make test` before submitting a pull request.
4. Open a PR targeting `main` and link related issues. Describe changes and testing performed.

## Commit Messages

- Use [Conventional Commits](https://www.conventionalcommits.org/) (e.g., `feat: add content endpoint`).
- Keep messages concise and meaningful. Describe *why* changes were made when not obvious.

## Code Standards

- Python code must pass `ruff`, `black`, `isort`, and `bandit` checks.
- TypeScript code must satisfy `eslint` (strict TypeScript rules) and `prettier` formatting.
- Terraform changes should pass `tflint` and `tfsec`.
- Tests should include coverage for new functionality and keep overall coverage >= 80%.

## Testing

- Backend tests live in `backend/tests`. Add asynchronous fixtures where relevant.
- Frontend tests use Vitest within the `frontend` package (lightweight snapshots and hooks).
- Infrastructure validations rely on Terraform plan outputs and linting.

## Documentation

Every feature should include relevant documentation updates:
- Update README sections if user-facing behavior changes.
- Extend architecture diagrams or dashboard definitions if new components are added.
- Note runbook changes in the incident log or backup procedures when necessary.

## Pull Request Checklist

- [ ] Tests added/updated
- [ ] Linting and formatting pass locally
- [ ] Documentation updated
- [ ] CI pipeline green

## Contact

Reach out via issues or `maintainers@portfolio.local` for support.

