# ADR 0003 — Deployment Topology

**Status**: Accepted
**Date**: 2024-11-09
**Deciders**: Platform Team, SRE Lead

## Context
We must deploy infrastructure across multiple environments (dev, stage, prod) with clear separation of blast radius, predictable promotion paths, and minimal cross-environment coupling. Compliance requires isolated accounts for prod data, and the networking model must support public edge services while keeping databases private. The topology should align with CloudFormation StackSets and CI/CD workflows already in use.

## Decision
Use a **multi-account, multi-AZ topology**:
- Dedicated AWS accounts per environment (dev, stage, prod) managed via AWS Organizations.
- Single region (us-east-1) with **three Availability Zones** for high availability.
- VPC per account with public and private subnets; RDS and application services reside in private subnets only.
- Shared CI/CD account assumes cross-account roles to deploy stacks via CloudFormation StackSets.

## Alternatives Considered
- **Single-account with multiple VPCs**: Simpler to manage but higher blast radius and weaker compliance isolation for production data.
- **Multi-region active/active**: Improves resilience but increases cost/complexity beyond current requirements; revisit after traffic growth milestones.
- **Hybrid on-prem + AWS**: Not required for current workloads and would add VPN/Direct Connect dependencies.

## Consequences

### Positive
- Clear environment isolation for compliance and incident containment.
- High availability via three AZs without multi-region complexity.
- CI/CD can reuse templates across accounts using StackSets, reducing drift risk.

### Negative
- Cross-account role management adds IAM complexity and onboarding overhead.
- Single-region strategy still concentrates risk from regional outages.
- Additional NAT Gateway costs per account.

### Mitigation
- Automate IAM role provisioning with CloudFormation and periodic `aws iam` audits.
- Document regional evacuation playbooks and run annual failover drills.
- Use centralized cost dashboards to monitor NAT/data transfer spend across accounts.
