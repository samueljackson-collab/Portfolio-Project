# AWS Three-Tier Web Application Infrastructure (Terraform)

This project provisions a production-ready three-tier web application stack on AWS using Terraform. It includes a multi-AZ VPC foundation, autoscaled compute tiers behind an Application Load Balancer, a highly available PostgreSQL RDS database, edge delivery with CloudFront, and comprehensive security/observability controls that align with the AWS Well-Architected Framework.

## Highlights
- Opinionated module library for VPC, compute, database, storage/CDN, security, monitoring, and DNS.
- Environment isolation with separate state backends for `dev`, `staging`, and `prod`.
- Secure-by-default posture: private subnets for app/data tiers, SSM access instead of SSH, encrypted storage, and WAF-ready ingress.
- Operational excellence via tagging, CloudWatch telemetry, Terratest scaffolding, and wrapper scripts for plan/apply/destroy.

Refer to the `docs/` directory for deep dives on architecture, deployment, security, operations, and disaster recovery.
