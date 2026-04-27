# ADR 0005 — Security Posture

**Status**: Accepted
**Date**: 2024-11-11
**Deciders**: Security Lead, Platform Team

## Context
Our AWS environments must comply with least-privilege principles, protect sensitive data, and provide auditable controls for deployments and runtime operations. The security posture needs to balance developer velocity with guardrails that prevent misconfigurations, while integrating with existing CI/CD pipelines and AWS Organizations governance.

## Decision
Adopt a **defense-in-depth security posture** anchored on AWS-native controls:
- Enforce **least privilege IAM** with role-based access; CloudFormation execution roles scoped to required services only.
- Use **private subnets** for RDS and application services; restrict inbound traffic to load balancers and bastion hosts only.
- Standardize **Secrets Manager** for credentials with 90-day rotation and customer-managed KMS keys.
- Enable **Config + Security Hub** across accounts with mandatory conformance packs (CIS AWS Foundations) and automated drift alerts.
- Require **CI/CD signing** of CloudFormation change sets with peer review before promotion to prod.

## Alternatives Considered
- **Third-party CSPM tooling only**: Offers richer dashboards but duplicates Security Hub signals and increases vendor footprint.
- **Self-managed Vault**: Powerful secret workflow, but adds operational complexity and overlapping capabilities with Secrets Manager/KMS.
- **Flat network with NACL-only controls**: Simpler, but fails to meet segmentation requirements and increases blast radius.

## Consequences

### Positive
- Strong alignment with AWS governance services; minimal new infrastructure to secure or patch.
- Clear audit trail via Config, CloudTrail, and signed change sets.
- Reduced credential sprawl through centralized Secrets Manager usage.

### Negative
- Increased IAM policy management overhead; requires linting and review discipline.
- Additional Config/Security Hub costs across multiple accounts.
- Rotation policies may cause short-lived credential disruptions if not coordinated with app teams.

### Mitigation
- Automate IAM linting in CI (cfn-lint + custom policy checks) and provide policy templates.
- Apply cost controls via Security Hub/Config scope and periodic review of unused checks.
- Document rotation playbooks and provide integration examples for common runtimes.
