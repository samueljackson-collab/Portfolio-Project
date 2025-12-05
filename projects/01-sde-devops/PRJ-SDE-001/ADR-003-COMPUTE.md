# ADR-003: Compute & Container Orchestration

## Context
We need to run stateless services with consistent scaling, security isolation, and minimal ops overhead. The platform must integrate with existing AWS networking and IAM patterns.

## Decision
- Use **AWS ECS on Fargate** for compute to avoid managing worker nodes while keeping AWS-native networking and IAM integration.
- Deploy services behind **ALB** with target group stickiness optional; health checks drive autoscaling decisions.
- Enforce **task IAM roles** for least-privilege access to Secrets Manager, S3, and other dependencies.
- Standardize **Docker build patterns** (non-root, small base images) with CI scans and SBOM generation.
- Support **horizontal autoscaling** on CPU/Memory and custom metrics (request rate, queue depth) with max caps per env.

## Consequences
- Reduced operational burden compared to self-managed Kubernetes; limited flexibility for advanced scheduling.
- Fargate cost may be higher for large sustained workloads; mitigated by rightsizing and scheduling non-peak scale-downs.
- Native integration simplifies IAM and networking; ALB features (WAF, target weights) support safe rollouts.

## Status
Accepted
