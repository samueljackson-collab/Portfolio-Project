# Major Update Report

## Version 1.4.0 – September 30, 2025

### Summary
This major release consolidates previously independent samples into a single portfolio monorepo with shared tooling and governance. All services are production-aligned with Dockerized deployment, environment-specific Terraform, and CI/CD automation.

### Breaking Changes
- Repository structure has been rebuilt to house backend, frontend, infrastructure, monitoring, and testing services at the root level.
- Legacy `portfolio/` directory has been removed in favor of the multi-service architecture defined in the specification.

### Migration Guidance
1. Clone the new repository structure.
2. Review updated environment variables in `backend/.env.example` and `frontend/.env.example`.
3. Apply database migrations using Alembic before deploying services.
4. Reinitialize Terraform state files by following the steps in `docs/deployment.md`.

### Follow-Up Work
- Populate additional project case studies as separate branches.
- Expand automated load testing scenarios for peak-traffic projections.
