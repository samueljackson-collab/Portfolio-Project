# Contributing Guide

Thank you for investing in this portfolio project. This guide outlines how to propose changes, run tests, and collaborate effectively.

## Development Workflow
1. Fork the repository and create a feature branch (`git checkout -b feat/awesome-change`).
2. Install tooling by running `./setup.sh`.
3. Implement your change with accompanying tests and documentation updates.
4. Run `make ci` to execute linting, tests, and type checks.
5. Submit a pull request referencing related issues and screenshots if applicable.

## Commit Convention
Use [Conventional Commits](https://www.conventionalcommits.org/) where possible:
- `feat: add refresh token rotation`
- `fix: correct JWT audience validation`
- `docs: expand deployment runbook`

## Pull Request Checklist
- [ ] Tests pass locally (`pytest`, `vitest`, `k6`, Postman smoke).
- [ ] Lint checks pass (`ruff`, `eslint`, `tflint`).
- [ ] Security scans pass (`pip-audit`, `npm audit`, `snyk`, `tfsec`).
- [ ] Documentation updated (README, docs/, runbooks).
- [ ] Screenshots/recordings attached for UI changes.

## Communication
- Open issues using templates in `.github/ISSUE_TEMPLATE/`.
- Join the project Slack (#portfolio-engineering) for asynchronous collaboration.
- Major decisions should be captured as ADRs in `docs/adr/` or service-specific ADR directories.

