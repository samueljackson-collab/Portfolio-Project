# ADR-001: Cloud Platform and Infrastructure-as-Code Strategy

- **Status:** Accepted
- **Date:** 2025-05-14

## Context
We require a reliable, compliant, and automatable environment to host the application stack with minimal manual intervention. Standardizing on a single cloud provider and IaC tool reduces drift, accelerates delivery, and simplifies governance.

## Decision
- Use **AWS** as the target cloud for all environments (dev/stage/prod).
- Manage infrastructure with **Terraform** using modular design and remote state stored in an S3 bucket with DynamoDB locking.
- Enforce **workspaces** per environment, with shared modules for VPC, ECS, RDS, ALB, and IAM roles.
- Integrate Terraform into CI/CD with plan/apply stages and policy-as-code gates (OPA/Conftest, tfsec).

## Consequences
- ✅ Consistent, repeatable deployments across environments.
- ✅ Easier drift detection via remote state and policy checks.
- ⚠️ Dependency on AWS-specific services; multi-cloud portability reduced.
- ⚠️ Requires disciplined state management and access controls for Terraform operators.
