# Portfolio Projects Master List

**Last Updated:** November 7, 2025
**Owner:** Sam Jackson
**Status Legend:** 🟢 Complete | 🟠 In Progress | 🔵 Planned | 🔄 Recovery/Rebuild | 📝 Documentation Pending

---

## Table of Contents

1. [Current Projects (Complete)](#current-projects-complete)
2. [Current Projects (In Progress)](#current-projects-in-progress)
3. [Past Projects (Recovery)](#past-projects-recovery)
4. [Planned Projects](#planned-projects)
5. [Project Summary by Category](#project-summary-by-category)

---

## Current Projects (Complete)

### PRJ-HOME-001: Homelab & Secure Network Build
**Status:** 🟢 Complete · 📝 Documentation Pending
**Category:** Homelab & Network Infrastructure
**Technologies:** pfSense, UniFi, VLANs, Suricata IPS, OpenVPN, 802.1X

**Description:** Production-grade secure network infrastructure featuring defense-in-depth security principles, comprehensive network segmentation across 5 VLANs (Trusted, IoT, Guest, Servers, DMZ), enterprise-grade wireless access with WPA3, and integrated intrusion prevention systems.

**Key Features:**
- 5-VLAN network segmentation with pfSense firewall
- UniFi managed switching and wireless (2x U6 Pro APs)
- Suricata IPS with Emerging Threats ruleset
- WPA3 Enterprise with RADIUS authentication (FreeIPA)
- OpenVPN for secure remote access
- DNS security with Unbound and DNSSEC

**Project Directory:** `projects/06-homelab/PRJ-HOME-001/`
**Evidence Status:** Architecture diagram, configurations, and documentation pending

---

### PRJ-HOME-002: Virtualization & Core Services
**Status:** 🟢 Complete · 📝 Documentation Pending
**Category:** Homelab & Virtualization
**Technologies:** Proxmox VE, Ceph, TrueNAS, Ansible, Terraform, FreeIPA, Nginx

**Description:** Production-grade virtualization platform featuring a 3-node Proxmox cluster with high availability, distributed Ceph storage, comprehensive core services (FreeIPA, Pi-hole, Nginx, Rsyslog, NTP), and automated infrastructure management.

**Key Features:**
- 3-node HA Proxmox cluster with Corosync and automatic VM failover
- Distributed Ceph RBD storage with 3-way replication
- Multi-tier storage (Local LVM, Ceph, NFS, iSCSI, Proxmox Backup Server)
- Core infrastructure services (authentication, DNS, reverse proxy, logging, NTP)
- Ansible playbooks and Terraform for infrastructure-as-code
- Comprehensive disaster recovery with tested RTO/RPO

**Project Directory:** `projects/06-homelab/PRJ-HOME-002/`
**Evidence Status:** Configurations, playbooks, DR plan documentation pending

---

### PRJ-SDE-001: Full-Stack Database Infrastructure
**Status:** 🟢 Complete
**Category:** System Development Engineering / DevOps / Cloud Architecture
**Technologies:** Terraform, AWS (VPC, RDS, ECS, ALB), PostgreSQL, Docker

**Description:** Complete production-ready infrastructure-as-code solution deploying a full application stack on AWS with custom VPC, PostgreSQL RDS, ECS Fargate application, CloudWatch monitoring, and VPC Flow Logs.

**Key Features:**
- Custom VPC with public/private/database subnet tiers across multiple AZs
- PostgreSQL RDS with encryption, automated backups, and HA support
- ECS Fargate application with auto-scaling and load balancing
- CloudWatch monitoring with alarms and centralized logging
- Modular Terraform design (VPC, Database, ECS Application modules)
- 1,500+ lines of production-ready Terraform code

**Project Directory:** `projects/01-sde-devops/PRJ-SDE-001/`
**Evidence Status:** Complete with full documentation

---

### PRJ-SDE-002: Observability & Backups Stack
**Status:** 🟢 Complete · 📝 Documentation Pending
**Category:** System Development Engineering / DevOps
**Technologies:** Prometheus, Grafana, Loki, Alertmanager, Proxmox Backup Server

**Description:** Comprehensive monitoring, logging, and alerting stack to observe homelab infrastructure and ensure data resilience through automated backups. Implements USE and RED methods for observability.

**Key Features:**
- Prometheus for metrics collection (15-second scrape interval)
- Grafana dashboards (Infrastructure, Service Health, Alerting)
- Loki for centralized log aggregation
- Alertmanager with Slack integration and routing
- Proxmox Backup Server with deduplication and 3-2-1 backup strategy
- Recording rules for pre-computed metrics

**Project Directory:** `projects/01-sde-devops/PRJ-SDE-002/`
**Evidence Status:** Dashboard exports, configurations, and alert examples pending

---

### PRJ-CYB-BLUE-001: AWS SIEM Pipeline with OpenSearch
**Status:** 🟢 Complete
**Category:** Cybersecurity / Blue Team / Security Engineering
**Technologies:** AWS OpenSearch, Kinesis Firehose, Lambda, GuardDuty, VPC Flow Logs, CloudTrail, Python

**Description:** Production-ready Security Information and Event Management (SIEM) pipeline built on AWS, providing centralized log aggregation, real-time threat detection, and security monitoring across cloud infrastructure.

**Key Features:**
- Centralized log aggregation from GuardDuty, VPC Flow Logs, and CloudTrail
- Kinesis Firehose with Lambda transformation for log normalization
- 3-node OpenSearch cluster with encryption and fine-grained access control
- Pre-configured security dashboards and alert rules
- Automated threat detection and SNS notifications
- 2,300+ lines of production-ready Terraform and Python

**Project Directory:** `projects/03-cybersecurity/PRJ-CYB-BLUE-001/`
**Evidence Status:** Complete with full documentation

---

## Current Projects (In Progress)

### PRJ-CLOUD-001: AWS Landing Zone (Organizations + SSO)
**Status:** 🟠 In Progress
**Category:** Cloud Architecture
**Technologies:** AWS Organizations, AWS SSO, Control Tower

**Description:** AWS landing zone implementation with Organizations and SSO configuration for enterprise-grade multi-account management.

**Project Directory:** `projects/02-cloud-architecture/PRJ-CLOUD-001/`

---

### PRJ-NET-DC-001: Active Directory Design & Automation
**Status:** 🟠 In Progress
**Category:** Networking & Datacenter
**Technologies:** Active Directory, PowerShell DSC, Ansible

**Description:** Active Directory design and automation using DSC and Ansible for enterprise directory services.

**Project Directory:** `projects/05-networking-datacenter/PRJ-NET-DC-001/`

---

### Professional Resume Portfolio
**Status:** 🟠 In Progress
**Category:** Professional Documentation
**Technologies:** LaTeX, Markdown, PDF

**Description:** Tailored resume variants for different roles (SDE, Cloud, QA, Network, Cybersecurity) with ATS-friendly formatting and consistent branding.

**Target Deliverables:**
- System Development Engineer resume
- Cloud Engineer resume
- QA Engineer resume
- Network Engineer resume
- Cybersecurity Analyst resume
- Cover letter template
- Portfolio summary one-pager

**Project Directory:** `professional/resume/`

---

## Past Projects (Recovery)

### PRJ-WEB-001: Commercial E-commerce & Booking Systems
**Status:** 🔄 Recovery in Progress
**Category:** Web Development & Data Management
**Technologies:** WordPress, WooCommerce, PHP, SQL, JavaScript

**Original Scope (2015-2022):**
1. **Resort Booking Website** - Complex booking system with seasonal pricing
2. **High-SKU Flooring Store** - 10,000+ products with weekly SQL price updates
3. **Tour Operator Website** - Tours with complex variations and dynamic pricing

**Recovery Plan:**
- **Week 1:** Catalog and restore data from backup exports, reconstruct database schemas
- **Week 2:** Re-document content management processes and deployment procedures
- **Week 3:** Publish sanitized artifacts and architecture documentation

**Project Directory:** `projects/08-web-data/PRJ-WEB-001/`
**Note:** Original source code lost due to workstation retirement without proper backup

---

## Planned Projects

### 🔵 System Development & DevOps Track

#### GitOps Platform with IaC (Terraform + ArgoCD)
**Technologies:** Terraform, ArgoCD, Kubernetes, GitLab CI/CD
**Scope:** Implement GitOps workflow with infrastructure-as-code for automated deployment

#### CI/CD Pipeline with GitHub Actions
**Technologies:** GitHub Actions, Docker, Terraform, AWS
**Scope:** Complete CI/CD automation with infrastructure testing and deployment

#### Container Orchestration with Kubernetes
**Technologies:** Kubernetes, Helm, Prometheus, Istio
**Scope:** Multi-node K8s cluster with service mesh and advanced networking

---

### 🔵 Cloud Architecture Track

#### Multi-Region Disaster Recovery
**Technologies:** AWS, Terraform, Route 53, RDS Cross-Region
**Scope:** Active-active or active-passive multi-region architecture

#### Serverless Application Architecture
**Technologies:** AWS Lambda, API Gateway, DynamoDB, Step Functions
**Scope:** Complete serverless application with event-driven architecture

#### Hybrid Cloud Networking
**Technologies:** AWS Direct Connect, VPN, Transit Gateway
**Scope:** Connect on-premises to AWS with hybrid networking

#### Cost Optimization & FinOps
**Technologies:** AWS Cost Explorer, CloudHealth, Terraform
**Scope:** Cost analysis, right-sizing recommendations, reserved instance planning

#### Cloud Migration Strategy
**Technologies:** AWS Migration Hub, Database Migration Service
**Scope:** Documented migration strategy from on-prem to cloud

---

### 🔵 Cybersecurity Track

#### PRJ-CYB-OPS-002: Incident Response Playbook
**Status:** 🔵 Planned
**Technologies:** IR frameworks, documentation templates
**Scope:** Clear IR guidance for ransomware and common threats

**Project Directory:** `projects/03-cybersecurity/PRJ-CYB-OPS-002/`

#### PRJ-CYB-RED-001: Adversary Emulation
**Status:** 🔵 Planned
**Technologies:** MITRE ATT&CK, Atomic Red Team, Caldera
**Scope:** Validate detections via safe ATT&CK TTP emulation (purple team)

**Project Directory:** `projects/03-cybersecurity/PRJ-CYB-RED-001/`

#### Vulnerability Management Program
**Technologies:** Nessus, OpenVAS, vulnerability tracking
**Scope:** Automated vulnerability scanning and remediation tracking

#### Zero Trust Architecture
**Technologies:** BeyondCorp, Okta, Cloudflare Access
**Scope:** Implement zero trust principles for network security

#### Security Audit & Compliance
**Technologies:** AWS Config, Security Hub, compliance frameworks
**Scope:** CIS benchmarks, SOC 2, and security audit automation

---

### 🔵 QA & Testing Track

#### PRJ-QA-001: Web App Login Test Plan
**Status:** 🔵 Planned
**Technologies:** Test case design, Jira, TestRail
**Scope:** Functional, security, and performance test design

**Project Directory:** `projects/04-qa-testing/PRJ-QA-001/`

#### PRJ-QA-002: Selenium + PyTest CI
**Status:** 🔵 Planned
**Technologies:** Selenium, PyTest, GitHub Actions
**Scope:** Automate UI sanity runs in GitHub Actions

**Project Directory:** `projects/04-qa-testing/PRJ-QA-002/`

#### Load Testing Strategy
**Technologies:** JMeter, Locust, k6
**Scope:** Performance testing framework with baseline and stress testing

#### API Testing with Postman/Newman
**Technologies:** Postman, Newman, CI/CD integration
**Scope:** Automated API testing with collection runs

#### Test Data Management
**Technologies:** Database seeding, faker libraries
**Scope:** Test data generation and management strategy

---

### 🔵 Homelab Expansion Track

#### PRJ-HOME-003: Multi-OS Lab
**Status:** 🔵 Planned
**Technologies:** Kali Linux, Ubuntu, Windows, Docker
**Scope:** Kali, Slackware/Puppy, Ubuntu lab for comparative analysis

**Project Directory:** `projects/06-homelab/PRJ-HOME-003/`

---

### 🔵 AI/ML & Automation Track

#### PRJ-AIML-001: Document Packaging Pipeline
**Status:** 🔵 Planned
**Technologies:** Python, AI APIs, document generation
**Scope:** One-click generation of Docs/PDFs/XLSX from AI prompts

**Project Directory:** `projects/07-aiml-automation/PRJ-AIML-001/`

---

### 🔵 Process Documentation Track

#### IT Playbook (E2E Lifecycle)
**Scope:** Unifying playbook from intake to operations covering SDLC and operational excellence

#### Engineer's Handbook (Standards/QA Gates)
**Scope:** Practical standards and quality bars for engineering practices

---

## Project Summary by Category

### System Development & DevOps
- **Complete:** PRJ-SDE-001 (Full-Stack DB Infrastructure), PRJ-SDE-002 (Observability)
- **Planned:** GitOps Platform, CI/CD Pipeline, Container Orchestration

### Cloud Architecture
- **In Progress:** PRJ-CLOUD-001 (AWS Landing Zone)
- **Planned:** Multi-Region DR, Serverless Architecture, Hybrid Cloud, FinOps, Cloud Migration

### Cybersecurity
- **Complete:** PRJ-CYB-BLUE-001 (AWS SIEM Pipeline)
- **Planned:** PRJ-CYB-OPS-002 (Incident Response), PRJ-CYB-RED-001 (Adversary Emulation), Vulnerability Management, Zero Trust, Security Audit

### QA & Testing
- **Planned:** PRJ-QA-001 (Test Plan), PRJ-QA-002 (Selenium CI), Load Testing, API Testing, Test Data Management

### Homelab & Infrastructure
- **Complete:** PRJ-HOME-001 (Secure Network), PRJ-HOME-002 (Virtualization)
- **Planned:** PRJ-HOME-003 (Multi-OS Lab)

### Networking & Datacenter
- **In Progress:** PRJ-NET-DC-001 (Active Directory)

### Web Development & Data
- **Recovery:** PRJ-WEB-001 (E-commerce & Booking Systems)

### AI/ML & Automation
- **Planned:** PRJ-AIML-001 (Document Pipeline)

### Professional Documentation
- **In Progress:** Resume Portfolio

---

## Project Statistics

**Total Projects:** 29+
- **Complete (🟢):** 5 projects
- **In Progress (🟠):** 3 projects
- **Recovery (🔄):** 1 project
- **Planned (🔵):** 20+ projects

**Projects with Documentation Pending (📝):** 4 projects

**Lines of Code (Production-Ready):**
- Terraform: 3,800+ lines
- Python: 2,300+ lines
- Ansible: 500+ lines (estimated)
- Total: 6,600+ lines

---

## Implementation Priority (2025-2026)

### Q4 2025 (Current)
1. Complete documentation for PRJ-HOME-001, PRJ-HOME-002, PRJ-SDE-002
2. Finish PRJ-CLOUD-001 (AWS Landing Zone)
3. Create 2-3 resume variants
4. Begin PRJ-WEB-001 recovery (Phase 1)

### Q1 2026
1. Complete resume portfolio (all 5 variants)
2. Implement PRJ-QA-001 and PRJ-QA-002
3. Complete PRJ-NET-DC-001 (Active Directory)
4. Start PRJ-CYB-OPS-002 (Incident Response Playbook)

### Q2 2026
1. GitOps Platform implementation
2. CI/CD Pipeline with GitHub Actions
3. PRJ-CYB-RED-001 (Adversary Emulation)
4. Multi-Region DR architecture

### Q3 2026
1. Container Orchestration (Kubernetes)
2. Serverless Architecture
3. PRJ-HOME-003 (Multi-OS Lab)
4. Load Testing Strategy

---

## Related Documentation

- [Main Portfolio README](./README.md)
- [Project Completion Checklist](./PROJECT_COMPLETION_CHECKLIST.md)
- [Comprehensive Implementation Guide](./docs/COMPREHENSIVE_PORTFOLIO_IMPLEMENTATION_GUIDE.md)
- [Quick Start Guide](./QUICK_START_GUIDE.md)
- [Missing Documents Analysis](./MISSING_DOCUMENTS_ANALYSIS.md)

---

**Author:** Sam Jackson
**GitHub:** [samueljackson-collab/Portfolio-Project](https://github.com/samueljackson-collab/Portfolio-Project)
**LinkedIn:** [linkedin.com/in/sams-jackson](https://www.linkedin.com/in/sams-jackson)

---

*This master list is actively maintained and reflects the current state of the portfolio. Projects move from Planned → In Progress → Complete as work progresses.*
