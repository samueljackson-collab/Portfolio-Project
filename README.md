# Portfolio Export Overview

This repository captures the exported structure of Sam Jackson's systems engineering portfolio. It provides runnable infrastructure-as-code, deployment automation, monitoring rules, and security guardrails alongside narrative documentation that explains how each component fits together.

The goal of this export is twofold:

- **Demonstrate reproducible engineering workflows.** Terraform and Kubernetes manifests define an environment that can be re-created quickly, while Bash utilities codify day-two operations.
- **Share practitioner-focused documentation.** Architecture narratives, deployment runbooks, API references, and security policies document how the platform is designed, deployed, and defended.

## Repository Layout

| Path | Description |
| --- | --- |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Deep dive into system architecture, design decisions, and component responsibilities. |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Deployment runbooks that cover Terraform provisioning, Kubernetes rollouts, and rollback strategies. |
| [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) | HTTP API contract, request/response schemas, and example payloads. |
| [SECURITY.md](./SECURITY.md) | Security posture, governance checklist, and references to policy artifacts. |
| [infrastructure/](./infrastructure/) | IaC assets split between Terraform modules and Kubernetes manifests. |
| [scripts/](./scripts/) | Operational Bash scripts for deployment, smoke testing, and teardown. |
| [monitoring/](./monitoring/) | Prometheus configuration, alert rules, and golden-signal dashboards. |
| [security/](./security/) | Baseline policies for IAM, Kubernetes, and supply-chain controls. |
| [documentation/](./documentation/) | Human-readable guides: runbooks, onboarding notes, and decision records. |
| [examples/](./examples/) | Copy-paste ready examples that demonstrate API usage and infrastructure overrides. |

## Quick Start

1. **Install prerequisites** – Terraform ≥ 1.5, kubectl ≥ 1.27, Helm ≥ 3.0, and jq for JSON parsing.
2. **Provision infrastructure** – Use [`./scripts/deploy.sh`](./scripts/deploy.sh) to run Terraform, configure Kubernetes contexts, and apply manifests.
3. **Verify health** – Run [`./scripts/smoke-test.sh`](./scripts/smoke-test.sh) to execute API readiness and Prometheus scrape checks.
4. **Tear down** – When finished, run [`./scripts/teardown.sh`](./scripts/teardown.sh) to destroy Terraform-managed resources safely.

> **Tip:** Each script accepts `--dry-run` to preview actions without mutating infrastructure. Refer to the inline help (`-h`) for full CLI usage.

## Architecture Snapshot

The service is composed of a public-facing API backed by a stateless application tier, a PostgreSQL data store, and an asynchronous worker queue. Networking and security controls are described in detail inside [ARCHITECTURE.md](./ARCHITECTURE.md), including diagrams and capacity planning notes. The Terraform stack in [`infrastructure/terraform/`](./infrastructure/terraform/) provisions VPC networking, managed databases, and IAM roles that align with the documented design.

## Deployment Workflows

Day-zero provisioning and day-two rollouts follow a GitOps-friendly pipeline. [DEPLOYMENT.md](./DEPLOYMENT.md) explains each stage, from workspace configuration and remote state management to blue/green deployments handled through the manifests in [`infrastructure/kubernetes/`](./infrastructure/kubernetes/). The scripts in [`scripts/`](./scripts/) orchestrate these steps locally or in CI.

## API Overview

Developers integrating with the Portfolio API should start with [API_DOCUMENTATION.md](./API_DOCUMENTATION.md). It covers authentication, versioning conventions, and endpoint-level examples. The [`examples/`](./examples/) directory contains ready-to-run HTTP requests and SDK snippets that mirror the documented flows.

## Security & Compliance

A defense-in-depth posture is captured in [SECURITY.md](./SECURITY.md). It references the IAM policies located under [`security/policies/`](./security/policies/), Kubernetes network boundaries, and continuous compliance checks. The monitoring rules in [`monitoring/`](./monitoring/) surface suspicious activity through alerting tied to these controls.

## Additional Documentation

Supplemental guides live in [`documentation/`](./documentation/) and include:

- Onboarding walkthroughs for new contributors.
- Runbooks describing incident response and backup drills.
- Architecture decision records that track trade-offs over time.

## Portfolio Narrative

The following section retains the original portfolio narrative that accompanied this repository export.

<details>
<summary><strong>Original Portfolio README</strong></summary>

# Hi, I'm Sam Jackson!
**[System Development Engineer](https://github.com/sams-jackson)** · **[DevOps & QA Enthusiast](https://www.linkedin.com/in/sams-jackson)** · **Freelance Full-Stack Web Developer**

***Building reliable systems, documenting clearly, and sharing what I learn. I turn ambiguous requirements into runbooks, dashboards, and repeatable processes.***

**Status key:** 🟢 Done · 🟠 In Progress · 🔵 Planned · 🔄 Recovery/Rebuild

---
## 🎯 Summary
System-minded engineer specializing in building, securing, and operating infrastructure and data-heavy web systems. Hands-on with homelab → production-like setups (wired rack, UniFi network, VPN, NAS), virtualization/services (Proxmox/TrueNAS), and observability/backups. Commercial experience shipping and maintaining booking/e-commerce sites with tens of thousands of SKUs and weekly price updates via SQL-driven workflows.

<details><summary><strong>Alternate summaries for tailoring</strong></summary>

**DevOps-forward** DevOps-leaning systems engineer who builds and operates reliable services end-to-end: homelab→production patterns (networking, virtualization, reverse proxy + TLS, backups), metrics/alerts (Prometheus/Grafana/Loki/Alertmanager), and automation with PowerShell/Bash/SQL. Experienced with data-heavy e-commerce/booking systems and operational runbooks.

**QA-forward** Quality-driven systems engineer turning ambiguous requirements into testable runbooks, acceptance criteria, and regression checklists. Builds monitoring dashboards for golden signals, designs reliable backup/restore procedures, and uses SQL/automation to validate data integrity across high-SKU catalogs and booking systems.
</details>

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
## 🟢 Completed Projects

### Homelab & Secure Network Build
**Description** Designed and wired a home network from scratch: rack-mounted gear, VLAN segmentation, and secure Wi-Fi for isolated IoT, guest, and trusted networks.
**Links**: [Repo/Folder](./projects/06-homelab/PRJ-HOME-001/) · [Evidence/Diagrams](./projects/06-homelab/PRJ-HOME-001/assets)

### Virtualization & Core Services
**Description** Proxmox/TrueNAS host running Wiki.js, Home Assistant, and Immich behind a reverse proxy with TLS.
**Links**: [Repo/Folder](./projects/06-homelab/PRJ-HOME-002/) · [Backup Logs](./projects/06-homelab/PRJ-HOME-002/assets)

### Observability & Backups Stack
**Description** Monitoring/alerting stack using Prometheus, Grafana, Loki, and Alertmanager, integrated with Proxmox Backup Server.
**Links**: [Repo/Folder](./projects/01-sde-devops/PRJ-SDE-002/) · [Dashboards](./projects/01-sde-devops/PRJ-SDE-002/assets)

---
## 🔄 Past Projects Requiring Recovery

Older commercial efforts live in cold storage while I recreate code, processes, and documentation that were lost when a retired workstation took the original knowledge base with it. Fresh assets will be posted as I rehydrate each workflow from backups and operational notes.

### Commercial E-commerce & Booking Systems (Rebuild in Progress)
**Status** 🔄 Recovering artifacts from backup exports and recreating runbooks.
**Description** Previously built and managed: resort booking site; high-SKU flooring store; tours site with complex variations. Code and process docs are being rebuilt for publication.
**Links**: [Repo/Folder](./projects/08-web-data/PRJ-WEB-001/) · [Evidence](./projects/08-web-data/PRJ-WEB-001/assets) *(placeholder while recovery completes)*

> **Recovery plan & timeline:** Catalog and restore SQL workflows and automation scripts (Week 1), re-document content management processes and deployment steps (Week 2), publish refreshed artifacts and narratives (Week 3).

---
## 🟠 In-Progress Projects (Milestones)
- **GitOps Platform with IaC (Terraform + ArgoCD)** · [Repo/Folder](./projects/01-sde-devops/PRJ-SDE-001/)
- **AWS Landing Zone (Organizations + SSO)** · [Repo/Folder](./projects/02-cloud-architecture/PRJ-CLOUD-001/)
- **Active Directory Design & Automation (DSC/Ansible)** · [Repo/Folder](./projects/05-networking-datacenter/PRJ-NET-DC-001/)
- **Resume Set (SDE/Cloud/QA/Net/Cyber)** · [Folder](./professional/resume/)

---
## 🔵 Planned Projects (Roadmaps)
- **SIEM Pipeline**: Sysmon → Ingest → Detections → Dashboards · ([Repo/Folder](./projects/03-cybersecurity/PRJ-CYB-BLUE-001/))
- **Adversary Emulation**: Validate detections via safe ATT&CK TTP emulation · ([Repo/Folder](./projects/03-cybersecurity/PRJ-CYB-RED-001/))
- **Incident Response Playbook**: Clear IR guidance for ransomware · ([Repo/Folder](./projects/03-cybersecurity/PRJ-CYB-OPS-002/))
- **Web App Login Test Plan**: Functional, security, and performance test design · ([Repo/Folder](./projects/04-qa-testing/PRJ-QA-001/))
- **Selenium + PyTest CI**: Automate UI sanity runs in GitHub Actions · ([Repo/Folder](./projects/04-qa-testing/PRJ-QA-002/))
- **Multi-OS Lab**: Kali, SlackoPuppy, Ubuntu lab for comparative analysis · ([Repo/Folder](./projects/06-homelab/PRJ-HOME-003/))
- **Document Packaging Pipeline**: One-click generation of Docs/PDFs/XLSX from prompts · ([Repo/Folder](./projects/07-aiml-automation/PRJ-AIML-001/))
- **IT Playbook (E2E Lifecycle)**: Unifying playbook from intake to operations · ([Folder](./docs/PRJ-MASTER-PLAYBOOK/))
- **Engineer’s Handbook (Standards/QA Gates)**: Practical standards and quality bars · ([Folder](./docs/PRJ-MASTER-HANDBOOK/))

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
[GitHub](https://github.com/sams-jackson) · [LinkedIn](https://www.linkedin.com/in/sams-jackson)

</details>

