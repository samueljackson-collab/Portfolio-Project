# AWS Multi-Tier Production Architecture

This project codifies a production-ready AWS reference stack that mirrors the capabilities of a SaaS workload: multi-tier VPC design, autoscaling application servers, multi-AZ PostgreSQL, defense-in-depth security, monitoring, and managed backups. Terraform keeps the entire footprint reproducible while the accompanying scripts and documentation make it approachable for a single engineer.

## High-Level Topology
```
                            INTERNET
                               │
                    ┌──────────▼───────────┐
                    │   CloudFront / DNS   │
                    │   (optional)         │
                    └──────────┬───────────┘
                               │ HTTPS (443)
                    ┌──────────▼───────────┐
                    │ Application Load      │
                    │ Balancer (public)     │
                    └──────────┬───────────┘
                               │
        ┌──────────────────────┴──────────────────────┐
        │              VPC 10.0.0.0/16               │
        │                                             │
        │  ┌───────────────┐      ┌───────────────┐  │
        │  │  us-east-1a   │      │  us-east-1b   │  │
        │  │               │      │               │  │
        │  │ PUBLIC SUBNET │      │ PUBLIC SUBNET │  │
        │  │ 10.0.1.0/24   │      │ 10.0.2.0/24   │  │
        │  │   ALB + NAT   │      │   ALB + NAT   │  │
        │  └───────┬───────┘      └───────┬───────┘  │
        │          │                      │          │
        │  ┌───────▼───────┐      ┌───────▼───────┐  │
        │  │ PRIVATE APP   │      │ PRIVATE APP   │  │
        │  │ 10.0.10.0/24  │      │ 10.0.11.0/24  │  │
        │  │  Auto Scaling │      │  Auto Scaling │  │
        │  │  Group (EC2)  │      │  Group (EC2)  │  │
        │  └───────┬───────┘      └───────┬───────┘  │
        │          │                      │          │
        │  ┌───────▼───────┐      ┌───────▼───────┐  │
        │  │ DATABASE      │      │ DATABASE      │  │
        │  │ SUBNET        │      │ SUBNET        │  │
        │  │ 10.0.20.0/24  │      │ 10.0.21.0/24  │  │
        │  │  RDS (Multi-AZ)│     │  Standby      │  │
        │  └───────────────┘      └───────────────┘  │
        └─────────────────────────────────────────────┘

Security Layers:
  • Network ACLs (stateless) keep internet traffic out of private tiers
  • Security Groups (stateful) enforce ALB → App → DB flow
  • IAM roles restrict instance permissions to essentials
  • TLS 1.2+ termination on ALB, RDS encryption at rest, Secrets Manager for credentials
```

## Design Highlights

### 1. Network & Routing
- **Multi-AZ VPC** with dedicated public, application, and database subnets in each zone.
- **Per-AZ NAT gateways** maintain outbound access for the private tier without sacrificing availability.
- **Database subnets** intentionally omit a default route to keep RDS fully isolated.

### 2. Application Tier
- **Launch Template + Auto Scaling Group** provision Amazon Linux 2 instances with NGINX preinstalled. Target tracking keeps CPU around 70%, scaling from two baseline nodes up to six under load.
- **Instance metadata hardened** via IMDSv2-only access, and CloudWatch detailed monitoring is enabled for one-minute insight.
- **IAM role** grants just enough access for logs, custom metrics, and secret retrieval.

### 3. Data Tier
- **Amazon RDS for PostgreSQL 15** in Multi-AZ mode delivers automatic failover (<60s RTO) and point-in-time recovery.
- **Enhanced monitoring & Performance Insights** expose OS and query performance for troubleshooting.
- **Secrets Manager** stores connection details and rotates the generated master password in a single place.

### 4. Security Posture
- **Security groups** restrict ingress strictly: internet → ALB (80/443), ALB → ASG (app port), ASG → RDS (5432).
- **AWS CloudTrail** captures account activity centrally in a hardened, versioned S3 bucket.
- **VPC Flow Logs** stream to CloudWatch Logs for network forensics.

### 5. Observability & Operations
- **CloudWatch alarms** cover ALB health, Auto Scaling CPU saturation, and RDS storage/CPU. Alerts land in an SNS topic for on-call rotation.
- **Infrastructure dashboard** surfaces request rates, response time, CPU utilisation, connections, and free storage in a single view.
- **Helper scripts** (`scripts/verify-stack.sh`, `scripts/rds-restore-from-latest.sh`) translate runbook steps into repeatable commands.

### 6. Resilience & Backups
- **AWS Backup plan** captures daily and weekly RDS restore points with 30/90-day retention.
- **Automated RDS snapshots + PITR** provide sub-5-minute RPO while the Auto Scaling group can rehydrate the stateless web tier in minutes.

## Terraform Module Inventory
- `modules/vpc` – Builds VPC, subnets, route tables, NAT gateways across two AZs.
- `modules/security-groups` – Applies three-tier security grouping (ALB, Auto Scaling group, RDS).
- `modules/alb` – Provisions the HTTPS Application Load Balancer, target group, and listeners with HTTP→HTTPS redirects.
- `modules/autoscaling` – Launch template, IAM role, target-tracking Auto Scaling group, and baked-in user data.
- `modules/rds` – Multi-AZ PostgreSQL instance with monitoring role, parameter group, and Secrets Manager integration.
- `modules/monitoring` – SNS topic, CloudWatch alarms, dashboards, VPC flow logs, and CloudTrail configuration.
- `modules/backup` – AWS Backup vault, plan, and selection protecting the PostgreSQL instance.

The root module wires these components together via expressive variables, emphasising clarity over abstraction so future enhancements (e.g., additional target groups, WAF integration, or blue/green deployments) are straightforward.
