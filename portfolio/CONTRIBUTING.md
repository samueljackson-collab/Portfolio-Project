# Contributing Guide

## Workflow
1. Fork the repository and create feature branches from `main`.
2. Run `make fmt` and `make test` before submitting a pull request.
3. Ensure coverage remains above 80% for backend Python tests.
4. Update documentation and changelog entries for user-visible changes.

## Commit Standards
- Use conventional commits (e.g., `feat: add project endpoint`).
- Keep commits focused and include relevant tests.

## Pull Requests
- Link related issues and provide screenshots for UI updates.
- CI must pass before review.

## Code Style
- Python: enforced with Ruff and Bandit.
- TypeScript: linted with ESLint and formatted via Prettier.
- Terraform: validated with `terraform fmt`, `tflint`, and `tfsec`.
