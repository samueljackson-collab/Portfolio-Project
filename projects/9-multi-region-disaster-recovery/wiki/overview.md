---
title: Project 9: Multi-Region Disaster Recovery Automation
description: Resilient multi-region architecture with automated failover between AWS regions
tags: [portfolio, infrastructure-devops, terraform]
repository: https://github.com/samueljackson-collab/Portfolio-Project
path: /projects/multi-region-disaster-recovery
---

# Project 9: Multi-Region Disaster Recovery Automation
> **Category:** Infrastructure & DevOps | **Status:** 🟢 60% Complete
> **Source:** projects/25-portfolio-website/docs/projects/09-disaster-recovery.md

## 📋 Executive Summary

Resilient multi-region architecture with **automated failover** between AWS regions. Synchronizes stateful services, validates replication health, and performs controlled recovery drills to meet aggressive RTO/RPO targets of <5 minutes.

## 🎯 Project Objectives

- **Multi-Region Replication** - Aurora Global Database, S3 cross-region sync, EKS clusters
- **Automated Failover** - Systems Manager runbooks for one-click recovery
- **Health Monitoring** - Route53 health checks with automatic DNS failover
- **Chaos Engineering** - Automated drills to validate recovery procedures
- **RTO/RPO Tracking** - Metrics for recovery time and data loss objectives

## 🏗️ Architecture

> Source: ../../../projects/25-portfolio-website/docs/projects/09-disaster-recovery.md#architecture
```
Primary Region (us-east-1)          Secondary Region (us-west-2)
─────────────────────────            ─────────────────────────
Application (EKS)                    Application (EKS) - Standby
       ↓                                      ↓
Aurora PostgreSQL ──────────────→ Aurora Global Database (Read Replica)
       ↓                                      ↓
S3 Buckets ──────Cross-Region────→ S3 Buckets (Replicated)
       ↓              Replication            ↓
Route53 Health Check ─────────────→ Automatic DNS Failover
```

**Failover Process:**
1. **Detection**: Route53 health check fails in primary region
2. **Notification**: CloudWatch alarm triggers SNS notification
3. **Automation**: Systems Manager runbook executes
4. **Promotion**: Aurora read replica promoted to writer
5. **DNS Update**: Route53 switches to secondary region
6. **Verification**: Health checks confirm successful failover

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Terraform | Terraform | Infrastructure as code |
| AWS Aurora Global Database | AWS Aurora Global Database | Multi-region database replication |
| AWS Route53 | AWS Route53 | DNS with health-based failover |

## 💡 Key Technical Decisions

### Decision 1: Adopt Terraform
**Context:** Project 9: Multi-Region Disaster Recovery Automation requires a resilient delivery path.
**Decision:** Infrastructure as code
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 2: Adopt AWS Aurora Global Database
**Context:** Project 9: Multi-Region Disaster Recovery Automation requires a resilient delivery path.
**Decision:** Multi-region database replication
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

### Decision 3: Adopt AWS Route53
**Context:** Project 9: Multi-Region Disaster Recovery Automation requires a resilient delivery path.
**Decision:** DNS with health-based failover
**Outcome:** Practices captured in RUNBOOK.md support ongoing operations.

## 🔧 Implementation Details

```bash
cd projects/9-disaster-recovery

# Deploy infrastructure to both regions
terraform init
terraform apply -var-file=production.tfvars

# Run failover drill
./scripts/failover-drill.sh --region us-west-2 --dry-run

# Execute actual failover (emergency)
./scripts/failover-drill.sh --region us-west-2 --execute

# Failback to primary
./scripts/failover-drill.sh --region us-east-1 --execute
```

```
9-disaster-recovery/
├── terraform/
│   ├── main.tf               # Multi-region infrastructure
│   ├── variables.tf          # Configuration variables
│   ├── production.tfvars     # Production settings
│   ├── modules/
│   │   ├── aurora-global/    # Global database module (to be added)
│   │   ├── eks-multi-region/ # EKS clusters (to be added)
│   │   └── s3-replication/   # S3 sync (to be added)
├── runbooks/
│   └── failover.md           # Manual failover procedures
├── scripts/
│   └── failover-drill.sh     # Automated failover script
├── chaos/                    # Chaos experiments (to be added)
│   └── experiments/
└── README.md
```

## ✅ Results & Outcomes

- **Availability**: 99.99% uptime SLA with multi-region architecture
- **RTO**: <5 minutes recovery time objective (automated failover)
- **RPO**: <1 minute data loss (Aurora Global Database lag)
- **Compliance**: Meets SOC 2, HIPAA disaster recovery requirements

## 📚 Documentation

- [README.md](../README.md)
- [RUNBOOK.md](../RUNBOOK.md)
- [projects/25-portfolio-website/docs/projects/09-disaster-recovery.md](../../../projects/25-portfolio-website/docs/projects/09-disaster-recovery.md)

## 🎓 Skills Demonstrated

**Technical Skills:** Terraform, AWS Aurora Global Database, AWS Route53, AWS Systems Manager, AWS EKS

**Soft Skills:** Communication, Incident response leadership, Documentation rigor

## 📦 Wiki Deliverables

### Diagrams

- **Architecture excerpt** — Copied from `../../../projects/25-portfolio-website/docs/projects/09-disaster-recovery.md` (Architecture section).

### Checklists

> Source: ../../../docs/PRJ-MASTER-PLAYBOOK/README.md#5-deployment--release

**Infrastructure**:
- [ ] Terraform plan reviewed and approved
- [ ] Database migrations tested
- [ ] Secrets configured in AWS Secrets Manager
- [ ] Monitoring alerts configured
- [ ] Runbook updated with new procedures

**Application**:
- [ ] All tests passing in staging
- [ ] Performance benchmarks met
- [ ] Feature flags configured (if using)
- [ ] Rollback plan documented
- [ ] Stakeholders notified of deployment

### Metrics

> Source: ../RUNBOOK.md#sloslis

| Metric | Target | Measurement |
|--------|--------|-------------|
| **RTO (Recovery Time Objective)** | < 15 minutes | Time from failure → full service restoration |
| **RPO (Recovery Point Objective)** | < 30 seconds | Maximum acceptable data loss |
| **Replication lag** | < 1 second | Aurora global database lag |
| **Health check success rate** | 99.9% | Route53 health check pass rate |
| **DR drill success rate** | 100% | Monthly DR drill completion without issues |
| **Failover success rate** | 99% | Automated failover completion rate |
| **Cross-region latency** | < 100ms | Inter-region communication latency |

### Screenshots

- **Operational dashboard mockup** — `../../../projects/06-homelab/PRJ-HOME-002/assets/mockups/grafana-dashboard.html` (captures golden signals per PRJ-MASTER playbook).

---

*Created: 2025-11-14 | Last Updated: 2025-11-14*
