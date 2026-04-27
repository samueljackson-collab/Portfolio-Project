# ADR 0001 — Initial Technical Direction

**Status**: Accepted
**Date**: 2024-11-07
**Deciders**: Platform Team, SRE Lead

## Context
Need to establish infrastructure-as-code approach for AWS environment provisioning. Must support multi-environment deployments (dev/stage/prod), disaster recovery, and compliance auditing.

## Decision
Use **AWS CloudFormation** as primary IaC tool for AWS resource provisioning with the following patterns:
- VPC with 3 AZs (public + private subnets)
- Multi-AZ RDS for high availability
- Least-privilege IAM roles per service
- Automated DR testing via scripted RDS failovers

## Consequences

### Positive
- Native AWS integration (no third-party state management)
- Built-in drift detection via AWS Config
- CloudFormation StackSets for multi-account deployments
- Free tier (no licensing costs)

### Negative
- CloudFormation DSL less expressive than Terraform HCL
- Limited multi-cloud support (AWS-only)
- Rollback limitations (some resources require manual intervention)

### Mitigation
- Use Python scripts for complex orchestration
- Document rollback procedures in RUNBOOK.md
- Evaluate Terraform for future multi-cloud requirements (future ADR)

## Alternatives Considered
- **Terraform**: Better multi-cloud support, but requires state management (S3 + DynamoDB locking)
- **AWS CDK**: More expressive (Python/TypeScript), but adds build complexity
- **Pulumi**: Modern approach, but smaller community/ecosystem
