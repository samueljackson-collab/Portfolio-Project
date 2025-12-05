# ADR-001: Cloud & Infrastructure-as-Code Strategy

## Context
We need a consistent, auditable approach to provisioning network, compute, data, and security resources for PRJ-SDE-001 across dev/stage/prod. Manual changes create drift and slow delivery. Multi-team contributions require a standard pattern with controls.

## Decision
- Use **Terraform** as the primary IaC tool with remote state (S3 + DynamoDB lock) per environment.
- Adopt **module-first** architecture: VPC, ALB/WAF, ECS service, RDS, and observability modules with documented inputs/outputs.
- Enforce **policy as code** using OPA/Conftest and tfsec in CI; block non-compliant plans (public DB, missing encryption, single-AZ).
- Standardize **naming/tagging**: `prj-sde-001-<env>-<component>` with required tags (`Project`, `Owner`, `Env`, `CostCenter`).
- Manage CI workflows in GitHub Actions with reusable workflows for lint/plan/apply and cost estimation.

## Consequences
- Faster environment spin-up with reusable modules; reduced drift via remote state and policy gates.
- Increased upfront effort to maintain modules and policies; requires CI runners with security tooling installed.
- Clear traceability of changes through state, plans, and reports supporting audits.

## Status
Accepted
