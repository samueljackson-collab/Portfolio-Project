# Cloud & Infrastructure Engineering Portfolio

## Executive Summary

**Professional Focus:** Cloud Infrastructure Architecture · DevOps · Infrastructure as Code  
**Specialization:** Production-grade systems design, cost optimization, and security-first architecture  
**Experience Level:** Advanced individual contributor delivering enterprise-ready systems

---

## Portfolio Overview
This repository curates two flagship case studies that demonstrate end-to-end ownership of cloud-scale and self-hosted infrastructure. Each project includes architecture decisions, IaC patterns, and quantified business outcomes.

| Project | Scale | Investment | Business Impact |
| --- | --- | --- | --- |
| **AWS Multi-Tier Architecture (Terraform)** | Enterprise workload in AWS | $2,400–2,640 yearly OPEX | 99.95% uptime, 95% faster deployments than manual builds |
| **Self-Hosted Family Photo Platform (Immich)** | Private cloud supporting 100–420 users | $1,321 TCO over 3 years | 94% cost savings vs AWS (\~$20K), 99.7% uptime |

---

## Case Study Highlights

### Project 1 · AWS Multi-Tier Architecture with Terraform
- **Objective:** Replace manual AWS provisioning with infrastructure as code to improve reliability, security, and speed of delivery.
- **Architecture:** Multi-AZ VPC, auto-scaling application tier, RDS Multi-AZ database, ALB with health checks, and centralized logging/monitoring.
- **Tooling:** Terraform (50+ resources), Ansible for configuration, Git-based CI workflows, AWS CloudWatch/Grafana dashboards.
- **Results:**
  - Achieved **99.95% uptime** with automated failover (<60s) and zero-downtime deployments.
  - Cut deployment time from two days to **15 minutes** with repeatable IaC pipelines.
  - Reduced monthly spend by **30–40%** through right-sizing, auto-scaling policies, and reserved instance planning.
  - Passed CIS AWS Foundations Level 1 checks with zero outstanding security findings.

### Project 2 · Immich Self-Hosted Photo Platform
- **Objective:** Deliver cost-efficient, privacy-respecting family photo management with enterprise reliability across three geographic sites.
- **Architecture:** Proxmox hypervisor, TrueNAS storage with ZFS, Traefik reverse proxy, WireGuard VPN, Prometheus/Grafana/Loki observability stack, and automated backups.
- **Operations:** Documented runbooks, quarterly restore tests (RTO 2.5h, RPO 24h), intrusion detection (CrowdSec/Fail2Ban), and VLAN microsegmentation.
- **Results:**
  - Delivered **94% cost savings** vs AWS ($20,459 over three years) while maintaining 99.7% uptime.
  - Validated zero packet loss over 30-day monitoring windows and sustained 145 MB/s storage throughput.
  - Prevented three outages via predictive capacity alerts and maintained a 2.3-minute MTTD with 2.1% false positives.
  - Enabled secure remote access for 100–420 users across three sites with VPN-only administration.

---

## Competencies Demonstrated

### Infrastructure as Code & Automation
- Terraform modules for multi-tier AWS infrastructure with state management and environment separation.
- Ansible playbooks for configuration hardening and service orchestration.
- Git-based workflows with change review, versioned releases, and disaster recovery readiness.

### Cloud Architecture & Reliability Engineering
- Multi-AZ/Multi-site design patterns, auto-scaling, and performance headroom planning.
- Zero-trust networking, IAM least privilege, encryption in transit/at rest, and AWS WAF roadmap.
- Observability-first operations: Prometheus metrics, Grafana dashboards, Loki logging, Alertmanager routing.

### Cost & Risk Management
- Hybrid cloud strategy balancing AWS services with optimized self-hosted workloads.
- Power/cooling analysis and hardware reuse for on-prem deployments.
- Quantified ROI reporting with CAPEX/OPEX tracking, downtime cost avoidance, and payback periods.

---

## Quantified Impact

| Metric | AWS Project | Immich Project | Combined |
| --- | --- | --- | --- |
| **CAPEX Savings** | N/A | $655 vs $21,780 | $21,125 |
| **OPEX Savings** | 30–40% vs baseline | $666 vs $2,400/yr | $1,734/yr |
| **Deployment Time** | 15 minutes vs 2 days | 90% DBA effort eliminated | 200+ hours saved |
| **Total 3-Year Value** | $3,600 saved | $20,459 saved | **$24,059 saved** |

| Operational KPI | Target | Achieved |
| --- | --- | --- |
| **Uptime (AWS)** | 99.5% | **99.95%** |
| **Uptime (Immich)** | 99.5% | **99.7%** |
| **MTTD** | <5 minutes | **2.3 minutes** |
| **False Positive Rate** | <5% | **2.1%** |

---

## Technology Stack
- **Cloud & Virtualization:** AWS (VPC, EC2, RDS, ALB, Auto Scaling, IAM), Proxmox VE, Docker Compose, LXC
- **IaC & Automation:** Terraform, Ansible, GitHub Actions, PowerShell, Bash, SQL
- **Networking & Security:** UniFi stack, WireGuard VPN, VLAN segmentation, TLS 1.3, IAM least privilege, intrusion detection
- **Storage & Databases:** TrueNAS/ZFS, PostgreSQL 15 (RDS Multi-AZ), S3 lifecycle management
- **Observability:** Prometheus, Grafana, Loki, Alertmanager, CloudWatch Logs

---

## Roadmap & Continuous Improvement
- **Q1 2025:** Implement AWS Reserved Instances (30% cost reduction), deploy AWS WAF, launch homelab secondary site, build Kubernetes learning cluster.
- **Q2 2025:** Extend AWS deployment to multi-region failover, enable ZFS geographic replication, run chaos engineering experiments, and publish technical blog series.

---

## Connect
- **GitHub:** [github.com/sams-jackson](https://github.com/sams-jackson)
- **LinkedIn:** [linkedin.com/in/sams-jackson](https://www.linkedin.com/in/sams-jackson)
- **Email:** [contact@samsjackson.dev](mailto:contact@samsjackson.dev)

> Each case study includes architecture diagrams, Terraform/Ansible source, monitoring exports, and cost analysis worksheets for reviewers who want to dive deeper.
