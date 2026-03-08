---
title: Project 1: AWS Infrastructure Automation
description: Production-ready AWS environment demonstrating infrastructure-as-code fluency across three IaC tools: Terraform, AWS CDK, and Pulumi
tags: [aws, cloud, documentation, infrastructure, infrastructure-devops, portfolio, terraform]
path: portfolio/1-aws-infrastructure-automation/overview
created: 2026-03-08T22:19:13.151088+00:00
updated: 2026-03-08T22:04:38.493902+00:00
---

-

# Project 1: AWS Infrastructure Automation
> **Category:** Infrastructure & DevOps | **Status:** 🟢 75% Complete
> **Source:** projects/25-portfolio-website/docs/projects/01-aws-infrastructure.md

## 📋 Executive Summary

Production-ready AWS environment demonstrating infrastructure-as-code fluency across **three IaC tools**: Terraform, AWS CDK, and Pulumi. This project provisions a complete multi-tier architecture suitable for hosting microservices applications.

## 🎯 Project Objectives

- **Multi-AZ VPC** with private, public, and database subnet tiers
- **Amazon EKS cluster** with managed node groups and autoscaling
- **RDS PostgreSQL** with automated backups and performance insights
- **Multi-tool implementation** - same infrastructure in Terraform, CDK, and Pulumi

## 🏗️ Architecture

> Source: ../../../projects/25-portfolio-website/docs/projects/01-aws-infrastructure.md#architecture
The infrastructure includes:
- **Network Layer**: 3 AZ VPC (10.0.0.0/16) with NAT gateways, route tables, and security groups
- **Compute Layer**: EKS 1.28 with t3.medium nodes (Spot/On-Demand mix), cluster autoscaler tags
- **Data Layer**: PostgreSQL 15 with 7-day backup retention, performance insights enabled
- **Deployment**: Environment-specific configs (dev, staging, production)

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Terraform | Terraform | (HCL) - Primary IaC with community modules |
| AWS CDK | AWS CDK | (Python) - Programmatic infrastructure definition |
| Pulumi | Pulumi | (Python) - Multi-cloud friendly authoring |

## 💡 Key Technical Decisions

### Decision 1: Adopt Terraform
**Context:** Project 1: AWS Infrastructure Automation requires a resilient delivery path.
**Decision:** (HCL) - Primary IaC with community modules
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 2: Adopt AWS CDK
**Context:** Project 1: AWS Infrastructure Automation requires a resilient delivery path.
**Decision:** (Python) - Programmatic infrastructure definition
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 3: Adopt Pulumi
**Context:** Project 1: AWS Infrastructure Automation requires a resilient delivery path.
**Decision:** (Python) - Multi-cloud friendly authoring
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

## 🔧 Implementation Details

### Deploy with Terraform
```bash
cd projects/1-aws-infrastructure-automation
./scripts/deploy-terraform.sh dev
```

### Deploy with CDK
```bash
./scripts/deploy-cdk.sh
```

### Deploy with Pulumi
```bash
./scripts/deploy-pulumi.sh
```

```
1-aws-infrastructure-automation/
├── terraform/          # Primary Terraform implementation
│   ├── main.tf        # VPC, EKS, RDS modules
│   ├── variables.tf   # Input variables
│   ├── outputs.tf     # Resource outputs
│   ├── dev.tfvars     # Dev environment config
│   └── production.tfvars
├── cdk/               # AWS CDK implementation
│   ├── app.py         # CDK application
│   └── cdk.json       # CDK configuration
├── pulumi/            # Pulumi implementation
│   └── __main__.py    # Pulumi program
└── scripts/           # Deployment automation
    ├── deploy-terraform.sh
    ├── deploy-cdk.sh
    ├── deploy-pulumi.sh
    └── validate.sh
```

## ✅ Results & Outcomes

- **Provisioning Speed**: Infrastructure deploys in 15-20 minutes (vs 2+ hours manual)
- **Multi-Tool Fluency**: Demonstrates IaC expertise across industry-standard tools
- **Cost Optimization**: Spot instance strategy reduces compute costs by ~60%
- **Resilience**: Multi-AZ architecture provides 99.95% availability SLA

## 📚 Documentation

- [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md)
- [PRE_DEPLOYMENT_CHECKLIST.md](../PRE_DEPLOYMENT_CHECKLIST.md)
- [README.md](../README.md)
- [RUNBOOK.md](../RUNBOOK.md)
- [projects/25-portfolio-website/docs/projects/01-aws-infrastructure.md](../../../projects/25-portfolio-website/docs/projects/01-aws-infrastructure.md)

## 🎓 Skills Demonstrated

**Technical Skills:** Terraform, AWS CDK, Pulumi, Bash, AWS Services

**Soft Skills:** Communication, Incident response leadership, Documentation rigor

## 📦 Wiki Deliverables

### Diagrams

- **Architecture excerpt** — Copied from `../../../projects/25-portfolio-website/docs/projects/01-aws-infrastructure.md` (Architecture section).

### Checklists

> Source: ../PRE_DEPLOYMENT_CHECKLIST.md

- [ ] AWS account created and accessible
- [ ] Billing alerts configured
- [ ] Cost budget set (recommended: $200/month for dev)
- [ ] Root account MFA enabled
- [ ] IAM admin user created (not using root)
- [ ] IAM user MFA enabled
- [ ] **Terraform installed** (>= 1.4)
- [ ] **AWS CLI installed** (>= 2.0)

### Metrics

> Source: ../RUNBOOK.md#sloslis

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Infrastructure deployment success rate** | 99% | Terraform/CDK/Pulumi apply success responses |
| **EKS control plane availability** | 99.95% | EKS API server reachability |
| **RDS availability** | 99.95% (Multi-AZ) | CloudWatch `DatabaseConnections` > 0 |
| **Node autoscaling response time** | < 5 minutes | Time from high CPU → new nodes Running |
| **RDS failover time (RTO)** | < 2 minutes | Time from failover initiate → RDS available |
| **Infrastructure drift detection** | < 5 minutes | Terraform/CDK drift check latency |

### Screenshots

- **Operational dashboard mockup** — `../../../projects/06-homelab/PRJ-HOME-002/assets/mockups/grafana-dashboard.html` (captures golden signals per PRJ-MASTER playbook).

---

*Created: 2025-11-14 | Last Updated: 2025-11-14*
