# Contributing Guide

Thank you for your interest in contributing to the Portfolio Monorepo! This document outlines the development workflow, coding standards, and expectations for pull requests.

## Workflow
1. Fork the repository and create a feature branch from `main`.
2. Install dependencies and pre-commit hooks:
   ```bash
   pip install -r requirements.txt
   npm install
   pre-commit install
   ```
3. Implement changes following the coding standards below.
4. Run the full test suite:
   ```bash
   make test
   ```
5. Open a pull request with a clear summary, testing evidence, and related issue references.

## Coding Standards
- Python code must follow `ruff` formatting and linting rules.
- TypeScript/JavaScript code must pass `eslint` and `prettier` with the repository configuration.
- Terraform code must pass `tflint` and `tfsec` checks.
- Write meaningful docstrings and inline comments to explain complex logic.
- Prefer dependency injection and configuration-driven design for testability.

## Testing Expectations
- Backend changes require updated or new pytest coverage with async fixtures.
- Frontend components must include unit tests (vitest) for rendered states and interactions.
- Infrastructure modifications should include `terraform validate` and plan outputs in the PR description.
- Update the Postman collection or k6 scripts when API contracts change.

## Documentation
- Update relevant documentation under `docs/` when behavior or workflows change.
- Include diagrams or Mermaid snippets where useful to illustrate architecture.

## Commit Messages
- Use Conventional Commit prefixes (`feat:`, `fix:`, `docs:`, `chore:`) when possible.
- Keep messages concise but descriptive.

## Communication
For questions or clarifications, open a discussion or reach out via email at `hello@samsjackson.dev`.
