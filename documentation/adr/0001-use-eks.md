# ADR 0001: Use Amazon EKS for Kubernetes Control Plane

- **Status:** Accepted
- **Date:** 2024-11-04

## Context

The portfolio platform requires a managed Kubernetes control plane to host API and worker workloads. Options considered: self-managed Kubernetes on EC2, Amazon ECS, and Amazon EKS.

## Decision

Adopt Amazon EKS to provide managed control-plane upgrades, integration with AWS IAM, and compatibility with existing Terraform modules.

## Consequences

- **Positive:** Reduced operational overhead for master nodes; native support for IRSA; straightforward integration with ALB ingress.
- **Negative:** Additional per-cluster costs; version availability lag behind upstream Kubernetes.
- **Follow-up:** Document upgrade cadence in [`documentation/runbooks/cluster-upgrades.md`](../runbooks/cluster-upgrades.md) and monitor AWS roadmap for region support.
