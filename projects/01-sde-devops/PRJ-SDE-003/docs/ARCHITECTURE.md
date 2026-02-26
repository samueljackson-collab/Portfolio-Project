# Architecture Deep Dive

This document explains the three-tier AWS reference architecture, covering VPC design, network segmentation, scaling approach, and managed services used for presentation, application, and data tiers.

## Layers
- **Web tier**: Public ALB terminating TLS and forwarding to web/application Auto Scaling groups in private subnets.
- **Application tier**: Stateless EC2 instances using SSM for access and NAT/Endpoints for outbound dependencies.
- **Data tier**: Multi-AZ PostgreSQL on Amazon RDS with option for read replicas and encrypted storage.

## Cross-Cutting Concerns
- **Security**: WAF, least-privilege security groups, encrypted storage, Secrets Manager for credentials.
- **Reliability**: Multi-AZ subnets, NAT per AZ, health checks, automated backups and snapshots.
- **Performance**: CloudFront for static assets, autoscaling policies, VPC endpoints to reduce latency.
- **Cost**: Toggleable endpoints/NAT strategy per environment; tags for allocation.
