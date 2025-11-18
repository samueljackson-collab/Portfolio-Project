# Security Overview

## Authentication
- JWT access tokens using HS256 with 30-minute expiry.
- Passwords hashed with bcrypt via Passlib.
- OAuth2 password flow for token issuance.

## Authorization
- Content endpoints require valid bearer token.
- Future enhancements: role-based policies for admin/editor roles.

## Data Protection
- Database connections require TLS (configure via environment variables in production).
- Secrets never stored in source control; `.env.example` documents required variables.
- Alembic migrations tracked for auditability.

## Secure Development Lifecycle
- `bandit`, `ruff`, `black`, and `isort` run during CI and pre-commit.
- `eslint` + `prettier` maintain consistent frontend quality.
- Terraform linting with `tflint` and static analysis with `tfsec`.
- Container images scanned with `trivy` as part of CI.

## Incident Response
- Refer to [Incident Checklist](./runbooks/incident_checklist.md) and [Backup & Restore](./runbooks/backup_restore.md).
- Observability stack surfaces alerts for error rates and latency (prometheus alertmanager integration stubbed).

## Compliance Targets
- Coverage threshold ensures high confidence in auth and CRUD operations.
- Logging and metrics instrumentation is designed to support SOC2-style traceability once extended.

