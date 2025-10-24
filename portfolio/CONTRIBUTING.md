# Contributing Guide

Thank you for your interest in contributing! Follow these steps to get started:

1. Fork the repository and create a feature branch.
2. Install dependencies with `make bootstrap`.
3. Run `make lint` and `make test` before opening a pull request.
4. Ensure coverage stays above 80% for backend and frontend tests.
5. Submit a pull request with a clear summary and reference relevant issues.

## Development Standards
- Follow the coding style enforced by ruff, eslint, and prettier.
- Keep documentation up to date with any code changes.
- Use feature flags for experimental functionality.

## Commit Convention
Use Conventional Commits (`type(scope): message`). Example: `feat(api): add project search`.
