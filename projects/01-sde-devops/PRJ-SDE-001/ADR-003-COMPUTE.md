# ADR-003: ECS Fargate for Application Compute

- **Status:** Accepted
- **Date:** 2025-05-14

## Context
We need container orchestration without managing worker nodes, with native AWS integration for networking, IAM, and autoscaling. Workloads are stateless and suited for managed serverless containers.

## Decision
- Run application services on **ECS Fargate** with AWSVPC networking.
- Use **Application Load Balancer** for ingress with health checks and path-based routing.
- Configure **autoscaling policies** on CPU/Memory and custom CloudWatch metrics.
- Store images in **Amazon ECR** with lifecycle policies and vulnerability scanning.

## Consequences
- ✅ Reduced operational overhead (no EC2 hosts to patch/scale).
- ✅ Tight integration with IAM roles for tasks and VPC networking.
- ⚠️ Some Kubernetes ecosystem tools not available; if required, reassess for EKS.
- ⚠️ Cost model based on vCPU/Memory per task; requires rightsizing and scaling policies.
