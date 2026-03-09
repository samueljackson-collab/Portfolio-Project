# Architecture Overview

## Logical Layers
1. **Networking** – Multi-AZ VPC with public, private-app, and private-db subnets, NAT gateways, VPC flow logs, and gateway endpoints.
2. **Security** – Segregated security groups for ALB, compute, and database tiers plus subnet-level NACLs.
3. **Compute** – Application Load Balancer in public subnets backed by EC2 Auto Scaling Group that runs the containerized web tier.
4. **Data** – Amazon RDS Multi-AZ MySQL with encrypted storage, automated backups, and performance insights.
5. **Storage** – S3 artifact bucket with versioning, encryption, and lifecycle policies.
6. **Observability** – CloudWatch alarms for CPU and ALB 5xx, VPC Flow Logs, and dashboards.

## High Availability
- Minimum of two AZs, three in staging/prod.
- Independent NAT gateway per AZ (optional single NAT for dev).
- Auto Scaling Group maintains capacity across AZs with health checks.
- RDS Multi-AZ ensures synchronous standby.

## Security Controls
- Security groups enforce tier-to-tier traffic only.
- Database subnets have no internet route.
- IAM roles/policies defined via Terraform (placeholder under `terraform/global`).
- Encryption at rest for RDS and S3; TLS termination at ALB.

## Data Flow Summary
1. Client -> Route53 -> ALB (public subnets).
2. ALB -> EC2 instances (private app subnets).
3. EC2 -> RDS over port 3306 (private DB subnets).
4. EC2 -> S3/DynamoDB via gateway endpoints for artifact retrieval or caching.
5. Monitoring services consume CloudWatch metrics/logs for alerting.

Refer to `docs/diagrams` for textual diagram callouts.
