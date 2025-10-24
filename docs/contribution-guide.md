# Contribution Guide

This document expands on the root `CONTRIBUTING.md` with deeper context for reviewers and maintainers.

## Branching Strategy
- `main`: protected branch, always deployable.
- Feature branches: `feature/<short-description>`.
- Hotfix branches: `hotfix/<issue-id>`.

## Pull Request Requirements
- Reference an issue or describe the motivation clearly.
- Include screenshots for UI changes and terraform plans for infrastructure updates.
- Update tests and documentation affected by the change.
- Provide a summary of manual verification steps.

## Coding Standards
### Python
- Follow type hints across modules.
- Use dependency injection for database sessions and background tasks.
- Keep functions small and single purpose; prefer services for complex logic.

### TypeScript
- Enable strict TypeScript settings; do not use `any`.
- Components should be functional with React hooks.
- Keep API interactions inside dedicated clients.

### Terraform
- Declare variables with descriptions and sensible defaults.
- Output key resource identifiers for downstream modules.
- Tag resources with `project`, `environment`, and `owner`.

## Review Checklist
- [ ] Code compiles and tests pass locally.
- [ ] Security implications considered (secrets, auth, network exposure).
- [ ] Observability updated (metrics, logging, dashboards).
- [ ] Documentation updated with new behavior.
- [ ] Rollback plan articulated if change fails.

## Release Process
1. Merge PR into `main`.
2. Tag release `vX.Y.Z` and push tag to trigger the release workflow.
3. Approve the manual gate after staging validation.
4. Monitor production deployment and Grafana dashboards for regressions.

## Incident Response
- Use runbooks stored in `docs/` (to be expanded) for recovery steps.
- Capture post-incident notes in `MAJOR_UPDATE_REPORT.md` or dedicated docs.

## Community
- Respect the Code of Conduct.
- Collaborate via GitHub Discussions for roadmap proposals.
