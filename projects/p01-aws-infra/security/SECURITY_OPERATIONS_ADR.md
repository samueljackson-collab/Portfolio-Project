# ADR-0002: Security & Operations Controls

## Status
Accepted

## Context
PRJ-AWS-001 now includes backend/frontend services and supporting infrastructure assets. We need documented security and operational controls to gate deployments and codify guardrails for IAM, secrets, and observability data.

## Decision
- Enforce least privilege by scoping CloudFormation execution roles to the project resources and pinning AWS region via environment variables.
- Require secrets to be sourced from AWS Secrets Manager and injected at runtime; no plaintext secrets are permitted in CI/CD or Docker images.
- Expose health/status endpoints only; postpone business endpoints until authentication and rate limiting middleware are added.
- Ship Prometheus alert rules and Grafana dashboards with runbook links to reduce MTTR for drift detection and API errors.

## Consequences
- Pipelines must provide AWS credentials with IAM policies limited to stack resources.
- Any new endpoint or Helm value must include threat modeling for authn/z and logging before merge.
- Operations can rely on versioned alert rules and dashboards to validate deployments in new clusters.
