# Architecture Overview

## Application Layers
- **Frontend**: React 18 application served via Vite during development and Nginx in production. Communicates with the backend via REST APIs.
- **Backend**: FastAPI application using async SQLAlchemy for data access, JWT authentication for security, and Alembic for schema management.
- **Database**: PostgreSQL 16 running in Docker Compose locally; production deployments assume a managed Postgres service.

## Infrastructure
- **Terraform**: Provides remote state storage (S3 + DynamoDB) and a reusable VPC module with public/private subnets, NAT gateway, and outputs for compute services.
- **CI/CD**: GitHub Actions orchestrate linting, testing, container image build/publish, SBOM generation, and deployment stubs.
- **Observability**: Placeholder dashboards capture host-level and service-level metrics for future integration with Grafana or similar tools.

## Security Controls
- JWT access tokens expire in 30 minutes and rely on environment-supplied secrets.
- Dependency scanning via npm audit, trivy, tfsec, tflint, ruff, bandit, and eslint/prettier.
- Code style enforced through pre-commit hooks and Makefile commands.

## Deployment Flow
1. Developers push to feature branches triggering lint/test workflows.
2. Successful builds generate container images and SBOM artifacts.
3. Deployment stubs document future stages for staging/prod pipelines.
4. Terraform modules manage environment provisioning via remote state.
