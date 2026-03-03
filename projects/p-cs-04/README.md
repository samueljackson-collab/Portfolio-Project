# Secrets Management Unification

- **Role Category:** Cloud Security
- **Status:** In Progress

## Executive Summary
Consolidating secrets storage across clouds and CI/CD with automated rotation and least-privilege access.

## Scenario & Scope
AWS, Azure, and GitHub Actions workloads consuming shared secrets.

## Responsibilities
- Inventory existing secrets and owners
- Migrated credentials into managed vaults
- Automated rotation and audit logging

## Tools & Technologies
- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault
- GitHub OIDC
- Terraform

## Architecture Notes
Federated OIDC access for CI; apps retrieve secrets via short-lived tokens with per-service namespaces.

## Process Walkthrough
- Mapped secrets to services and lifecycle
- Provisioned vault namespaces and policies
- Implemented rotation jobs and alerting
- Removed plaintext secrets from repos

## Outcomes & Metrics
- Eliminated long-lived CI secrets
- Rotated 100% of high-risk credentials
- Added audit trails and owner metadata

## Evidence Links
- runbooks/p-cs-04/secrets-unification.md

## Reproduction Steps
- Deploy Vault with the provided helm chart
- Configure GitHub OIDC roles for CI
- Migrate application secrets and test rotation

## Interview Points
- Choosing between cloud-native and Vault
- Designing least privilege for secrets
- Automating rotation without downtime
