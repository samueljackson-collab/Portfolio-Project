# ADR-002: Networking & Connectivity

## Context
The application needs internet-facing access via HTTPS while keeping services and data private. We require multi-AZ resiliency, minimal blast radius, and controlled egress.

## Decision
- Implement a **custom VPC** with public, private, and database subnets across at least two AZs.
- Place **ALB + WAF** in public subnets; ECS tasks and supporting services in private subnets; RDS in isolated DB subnets.
- Use **NAT gateways per AZ** for outbound traffic; restrict security groups to ALB → ECS and ECS → RDS flows.
- Enable **VPC Flow Logs** to S3/CloudWatch and GuardDuty for anomaly detection.
- Prefer **PrivateLink** or VPC endpoints for AWS service access where available (e.g., S3, ECR, Secrets Manager).

## Consequences
- Strong isolation reduces exposure; WAF and SG patterns become reusable.
- NAT per AZ increases cost but improves resilience; cost levers documented in business value narrative.
- Requires disciplined SG reviews; policy checks must block overly permissive rules.

## Status
Accepted
