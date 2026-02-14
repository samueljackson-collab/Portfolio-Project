# ADR-002: Three-Tier VPC Networking

- **Status:** Accepted
- **Date:** 2025-05-14

## Context
The platform hosts internet-facing services, application workloads, and databases with differing exposure and performance requirements. We need clear isolation to limit blast radius and enforce least privilege.

## Decision
- Implement a **three-tier VPC** with public, private, and database subnets across at least two AZs.
- Place **ALB and NAT Gateways** in public subnets; **ECS tasks** in private subnets; **RDS** in isolated database subnets with no internet route.
- Use **security groups** to restrict flows: ALB → ECS (HTTP/HTTPS), ECS → RDS (5432), and outbound via NAT only.
- Enable **VPC Flow Logs** to CloudWatch/S3 for audit and anomaly detection.

## Consequences
- ✅ Clear separation of concerns and reduced attack surface.
- ✅ Network telemetry supports security investigations.
- ⚠️ Additional cost for NAT gateways and flow logs; mitigate with per-AZ vs. shared NAT decisions.
- ⚠️ Slightly more complex routing rules requiring automation and documentation.
