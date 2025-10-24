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
## 📈 Project Context & Operations

### Team & Ownership
| Role | Primary Responsibilities | Required Skills | Est. Weekly Hours | Backup |
| --- | --- | --- | --- | --- |
| **Content Lead** | Own editorial roadmap, on-page SEO, and cross-channel messaging; coordinate subject-matter interviews. | SEO strategy, content ops tooling, CMS publishing, stakeholder facilitation. | 15 | Ads/Automation Lead for publishing cadence; Executive Sponsor for approvals. |
| **Video Lead** | Plan storyboards, capture/edit footage, publish to YouTube/shorts, repurpose for socials. | Video production, motion graphics, audio sweetening, platform analytics. | 12 | Content Lead handles scripts & narration; Ads/Automation Lead can assist with edits. |
| **Ads & Automation Lead** | Manage paid campaigns, lifecycle automations, and marketing ops integrations (UTM, CRM, email). | Paid media strategy, marketing automation platforms, API/Zapier workflow design. | 18 | Analytics Engineer maintains automations; Content Lead pauses/spins up campaigns. |
| **Analytics Engineer** | Build dashboards, maintain data pipelines, track KPIs, and surface insights for iteration. | SQL, BI tooling, ETL orchestration, experimentation frameworks. | 10 | Ads & Automation Lead keeps key dashboards updated; Executive Sponsor prioritizes insights. |
| **Executive Sponsor** | Define strategic goals, unblock resources, approve scope pivots, and align stakeholders. | Portfolio oversight, budgeting, stakeholder management, risk mitigation. | 5 | Content Lead briefs interim sponsor; Analytics Engineer supplies status snapshots. |

### RACI Matrix
| Role \ Workstream | SEO | Video | Advertising | Automation | Competitor Intelligence |
| --- | --- | --- | --- | --- | --- |
| Content Lead | **A/R** | C | C | I | **A** |
| Video Lead | C | **A/R** | I | I | C |
| Ads & Automation Lead | C | C | **A/R** | **A/R** | C |
| Analytics Engineer | R | C | C | R | **R** |
| Executive Sponsor | I | I | I | I | I |

### Sprint Cadence & Communications
- **Daily stand-up:** 15 minutes at 09:30 PT (Zoom + shared agenda doc). Focus on yesterday/today/blockers with the Analytics Engineer logging action items. Asynchronous check-in thread in Slack `#21d-sprint` posted by 10:00 PT for anyone who cannot attend.
- **Escalations:** Blockers >12 hours old escalated in Slack to the Ads & Automation Lead (operations owner). If still unresolved within 24 hours, the Content Lead pings the Executive Sponsor via email + Slack DM for resource decisions.
- **Response SLAs:**
  - Critical production/ads outage — acknowledge in ≤30 minutes during business hours, mitigate within 4 hours.
  - Content/video blockers — acknowledge in ≤2 hours, mitigation plan within same day.
  - Analytics/data discrepancies — acknowledge in ≤4 hours, resolution or workaround within 1 business day.

### Onboarding & Cross-Training
- **Knowledge base:** Maintain role playbooks in Notion with checklists for campaign launches, video publishing, and analytics refreshes. Each owner updates their guide at the close of every sprint.
- **Pairing rotations:** Weekly 1-hour shadow sessions (Content ↔ Video, Ads ↔ Analytics) ensure backups can execute essentials like CMS publishes, basic video edits, or dashboard refreshes.
- **Emergency coverage drills:** Once per sprint, rehearse a 24-hour absence scenario where backups execute the top-priority tasks and document gaps for remediation.
- **Access management:** Store credentials and API keys in shared vault folders with role-based permissions to ensure backups can assume responsibilities without delays.

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
