# Hi, I'm Sam Jackson!
**[System Development Engineer](https://github.com/samueljackson-collab)** · **[DevOps & QA Enthusiast](https://www.linkedin.com/in/sams-jackson)** · **Freelance Full-Stack Web Developer**

[![CI](https://github.com/samueljackson-collab/Portfolio-Project/workflows/CI/badge.svg?branch=main)](https://github.com/samueljackson-collab/Portfolio-Project/actions/workflows/ci.yml)

***Building reliable systems, documenting clearly, and sharing what I learn. I turn ambiguous requirements into runbooks, dashboards, and repeatable processes.***

**Status key:** 🟢 Done · 🟠 In Progress · 🔵 Planned · 🔄 Recovery/Rebuild · 📝 Documentation Pending

> **Portfolio Note:** This repository is actively being built. Projects marked 🟢 are technically complete but documentation/evidence is being prepared (📝). Projects marked 🔵 are planned roadmap items, and 🔄 indicates recovery/rebuild efforts are underway.

> **Note:** Some project directories referenced below contain planning documentation and structure but are awaiting evidence/asset uploads. Check individual project READMEs for current status.

> 📚 **New:** [Missing Documents Analysis](./MISSING_DOCUMENTS_ANALYSIS.md) | [Quick Start Guide](./QUICK_START_GUIDE.md) | [Completion Checklist](./PROJECT_COMPLETION_CHECKLIST.md) | [Enterprise Project Quick Start](./projects-new/QUICK_START_GUIDE.md)

---
## 🧭 Reviewer Fast Reference

- **Reviewer Checklist:** For a detailed validation checklist covering top metrics, interview workflow, and file map, please see [**PORTFOLIO_VALIDATION.md**](./PORTFOLIO_VALIDATION.md). This file serves as the single source of truth for validation runs.

---
## 🎯 Summary
System-minded engineer specializing in building, securing, and operating infrastructure and data-heavy web systems. Hands-on with homelab → production-like setups (wired rack, UniFi network, VPN, backup/restore drills), and pragmatic DevOps/QA practices.

<details><summary><strong>Alternate summaries for tailoring</strong></summary>

**DevOps-forward** DevOps-leaning systems engineer who builds and operates reliable services end-to-end: homelab→production patterns (networking, virtualization, reverse proxy + TLS, backups), monitoring (golden signals), and CI/CD automation.

**QA-forward** Quality-driven systems engineer turning ambiguous requirements into testable runbooks, acceptance criteria, and regression checklists. Builds monitoring dashboards for golden signals and SLOs.
</details>

---
## 📘 Guides

- [Wiki.js Setup Guide](./docs/wiki-js-setup-guide.md) — Complete walkthrough to deploy, harden, and populate a Wiki.js instance for portfolio documentation.

## 💻 UI Components

- [EnterpriseWiki](./src/components/EnterpriseWiki.tsx) — React component that renders interactive learning paths for SDE, DevOps, QA, and architecture roles.

## 📦 Portfolio Blueprints

> **Canonical directories:** Standardized enterprise projects (P01–P20) now live in `./projects-new/`. The historical `./projects/` tree continues to host homelab and commercial recovery work.

- [P01: AWS Infrastructure Automation](./projects-new/P01-aws-infra) — Automates AWS networking, ECS, load balancers, and RDS provisioning with Terraform-first workflows.
- [P02: Kubernetes Cluster Management](./projects-new/P02-k8s-cluster) — Operates EKS clusters end-to-end, including node groups, RBAC, and Helm-based workloads.
- [P03: CI/CD Pipeline Implementation](./projects-new/P03-cicd-pipeline) — Multi-stage GitHub Actions with automated testing, deployment gates, and security scanning.
- [P04: Operational Monitoring Stack](./projects-new/P04-monitoring-stack) — Prometheus, Grafana, and Alertmanager bundle with curated golden-signal dashboards.
- [P05: Database Performance Optimization](./projects-new/P05-db-optimization) — Python toolkit for slow-query analysis, index tuning, and benchmarking workflows.
- [P06: Web Application Testing Framework](./projects-new/P06-web-testing) — Playwright + pytest suite covering E2E, API, and visual regression testing.
- [P07: Security Compliance Automation](./projects-new/P07-security-compliance) — CIS/OWASP profiling with automated evidence capture and compliance reporting.
- [P08: Cost Optimization Tooling](./projects-new/P08-cost-optimization) — AWS Cost Explorer automation for idle-resource detection and savings recommendations.
- [P09: Disaster Recovery Orchestration](./projects-new/P09-dr-orchestration) — DR drill automation, failover orchestration, and backup verification pipelines.
- [P10: Log Aggregation System](./projects-new/P10-log-aggregation) — ELK stack deployment with ingestion pipelines, retention policies, and Kibana dashboards.
- [P11: API Gateway Configuration](./projects-new/P11-api-gateway) — Terraform-driven API Gateway provisioning with authentication, rate limiting, and observability hooks.
- [P12: Container Registry Management](./projects-new/P12-container-registry) — ECR lifecycle automation with vulnerability scanning and publish workflows.
- [P13: Secrets Management System](./projects-new/P13-secrets-management) — Secrets rotation, RBAC, and audit logging using AWS Secrets Manager.
- [P14: Network Configuration Automation](./projects-new/P14-network-automation) — Network baselines, routing policies, and guardrails codified in Terraform modules.
- [P15: Incident Response Automation](./projects-new/P15-incident-response) — Automated incident detection, aggregation, remediation, and post-mortem templates.
- [P16: Backup Verification System](./projects-new/P16-backup-verification) — Scheduled restore tests, integrity validation, and compliance-ready reporting.
- [P17: Performance Load Testing](./projects-new/P17-load-testing) — k6-powered HTTP/WebSocket load harness with performance analytics.
- [P18: Service Mesh Implementation](./projects-new/P18-service-mesh) — Istio deployment patterns for secure service-to-service traffic management.
- [P19: Observability Dashboard](./projects-new/P19-observability-dashboard) — Unified metrics/logs/traces dashboards via OpenTelemetry.
- [P20: Multi-Cloud Orchestration](./projects-new/P20-multi-cloud) — Cloud-agnostic orchestration, inventory, and cost comparisons across AWS, Azure, and GCP.
- [Project 21: Quantum-Safe Cryptography](./projects/21-quantum-safe-cryptography) — Hybrid Kyber + ECDH key exchange prototype.
- [Project 22: Autonomous DevOps Platform](./projects/22-autonomous-devops-platform) — Event-driven remediation workflows and runbooks-as-code.
- [Project 23: Advanced Monitoring & Observability](./projects/23-advanced-monitoring) — Grafana dashboards, alerting rules, and distributed tracing config.
- [Project 24: Portfolio Report Generator](./projects/24-report-generator) — Automated report templating with Jinja2.
- [Project 25: Portfolio Website & Documentation Hub](./projects/25-portfolio-website) — VitePress-powered portal aggregating all documentation and guides.

---
## 🛠️ Core Skills
- **Systems & Infra:** Linux/Windows, networking, VLANs, VPN, UniFi, NAS, Active Directory
- **Virtualization/Services:** Proxmox/TrueNAS, reverse proxy + TLS, RBAC/MFA, backup/restore drills
- **Automation & Scripting:** PowerShell, Bash, SQL (catalog ops, reporting), Git
- **Web & Data:** WordPress, e-commerce/booking systems, schema design, large-catalog data ops
- **Observability & Reliability:** Prometheus, Grafana, Loki, Alertmanager, golden signals, SLOs, PBS
- **Cloud & Tools:** AWS/Azure (baseline), GitHub, Docs/Sheets, Visio/diagramming
- **Quality & Process:** runbooks, acceptance criteria, regression checklists, change control

---
## 🟢 Completed Projects (📝 Documentation in Progress)

### Homelab & Secure Network Build
**Status:** 🟢 Complete · 📝 Docs pending
**Description** Designed and wired a home network from scratch: rack-mounted gear, VLAN segmentation, and secure Wi-Fi for isolated IoT, guest, and trusted networks.
**Links**: [Project README](./projects/06-homelab/PRJ-HOME-001/) · [Evidence/Diagrams](./projects/06-homelab/PRJ-HOME-001/assets) *(being prepared)*

### Virtualization & Core Services
**Status:** 🟢 Complete · 📝 Docs pending
**Description** Proxmox/TrueNAS host running Wiki.js, Home Assistant, and Immich behind a reverse proxy with TLS.
**Links**: [Project README](./projects/06-homelab/PRJ-HOME-002/) · [Backup Logs](./projects/06-homelab/PRJ-HOME-002/assets) *(being prepared)*

### Observability & Backups Stack
**Status:** 🟢 Complete · 📝 Docs pending
**Description** Monitoring/alerting stack using Prometheus, Grafana, Loki, and Alertmanager, integrated with Proxmox Backup Server.
**Links**: [Project README](./projects/01-sde-devops/PRJ-SDE-002/) · [Dashboards](./projects/01-sde-devops/PRJ-SDE-002/assets)

---
## 🔄 Past Projects Requiring Recovery

Older commercial efforts live in cold storage while I recreate code, processes, and documentation that were lost when a retired workstation took the original knowledge base with it. Fresh assets will be published as they’re rebuilt.

### Commercial E-commerce & Booking Systems (Rebuild in Progress)
**Status:** 🔄 Recovery in progress
**Description** Previously built and managed: resort booking site; high-SKU flooring store; tours site with complex variations. Code and process docs are being rebuilt for publication.
**Links**: [Project README & Recovery Plan](./projects/08-web-data/PRJ-WEB-001/) · [Evidence](./projects/08-web-data/PRJ-WEB-001/assets) *(pending recovery)*

> **Recovery plan & timeline:** Catalog and restore SQL workflows and automation scripts (Week 1), re-document content management processes and deployment steps (Week 2), publish refreshed artifacts (Week 3+).

---
## 🟠 In-Progress Projects (Milestones)
- **Database Infrastructure Module (Terraform RDS)** · [Project README](./projects/01-sde-devops/PRJ-SDE-001/) · ✅ Module complete, expanding to full-stack
- **Resume Set (SDE/Cloud/QA/Net/Cyber)** · [Project README](./professional/resume/) · 📝 Structure created, content in progress

### 🔵 Planned Infrastructure Projects
- **GitOps Platform with IaC (Terraform + ArgoCD)** · *Roadmap defined*
- **AWS Landing Zone (Organizations + SSO)** · *Research phase*
- **Active Directory Design & Automation (DSC/Ansible)** · *Planning phase*

---
## 🔵 Planned Projects (Roadmaps)

### Cybersecurity Projects
- **SIEM Pipeline**: Sysmon → Ingest → Detections → Dashboards · *Blue team defense*
- **Adversary Emulation**: Validate detections via safe ATT&CK TTP emulation · *Purple team testing*
- **Incident Response Playbook**: Clear IR guidance for ransomware · *Operations readiness*

### QA & Testing Projects
- **Web App Login Test Plan**: Functional, security, and performance test design · *Test strategy*
- **Selenium + PyTest CI**: Automate UI sanity runs in GitHub Actions · *Test automation*

### Infrastructure Expansion
- **Multi-OS Lab**: Kali, SlackoPuppy, Ubuntu lab for comparative analysis · *Homelab expansion*

### Automation & Tooling
- **Document Packaging Pipeline**: One-click generation of Docs/PDFs/XLSX from prompts · *Documentation automation*

### Process Documentation
- **IT Playbook (E2E Lifecycle)**: Unifying playbook from intake to operations · *Operational excellence*
- **Engineer's Handbook (Standards/QA Gates)**: Practical standards and quality bars · *Quality framework*

---
## 💼 Experience
**Desktop Support Technician — 3DM (Redmond, WA) · Feb 2025–Present**  
**Freelance IT & Web Manager — Self-employed · 2015–2022**  
**Web Designer, Content & SEO — IPM Corp. (Cambodia) · 2013–2014**

---
## 🎓 Education & Certifications
**B.S., Information Systems** — Colorado State University (2016–2024)  

---
## 🤳 Connect
[GitHub](https://github.com/samueljackson-collab) · [LinkedIn](https://www.linkedin.com/in/sams-jackson) 
[![GitHub Profile](https://img.shields.io/badge/GitHub-Portfolio-181717?style=flat&logo=github)](https://github.com/samueljackson-collab)