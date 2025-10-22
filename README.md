# Hi, I'm Sam Jackson!
**[System Development Engineer](https://github.com/sams-jackson)** · **[DevOps & QA Enthusiast](https://www.linkedin.com/in/sams-jackson)** · **Freelance Full-Stack Web Developer**

***Building reliable systems, documenting clearly, and sharing what I learn. I turn ambiguous requirements into runbooks, dashboards, and repeatable processes.***

## 📘 Featured Project: Reportify Pro – Enterprise Report Toolkit
`Reportify Pro` combines a Python-powered Word generator with an analyst-friendly cybersecurity UI so I can assemble executive-ready documentation with consistent structure and branding.

### Why I built it
- Ship polished assessment reports (security, DevOps, cloud, compliance, analytics) without rebuilding formatting every engagement.
- Keep a reusable catalog of 21 opinionated templates that highlight the sections clients expect for each discipline.
- Give analysts a lightweight UI that captures findings, tags, and guidance before handing content off for final document production.

### What’s inside
- **Python generator** (`reportify_pro.py`): Provides a `DocumentGenerator` helper plus a rich template database spanning eight IT domains. It handles cover pages, headings, KPI tables, lists, and appendices with a consistent visual style.
- **Template catalog**: 21 pre-defined report shells covering vulnerability assessments, incident response, project proposals, operational reports, and more. Each includes icons, recommended sections, and optional defaults.
- **Cybersecurity Report Arsenal UI** (`cybersecurity_report_arsenal.html`): Tailwind-powered single page app for role-based template selection, findings capture, tag management, and JSON save/load workflows.
- **Desktop GUI** (`reportify_gui.py`): Tkinter-based three-panel workspace for analysts who prefer a native app to browse templates, enter report content, manage tags/lists, and export DOCX files without leaving the desktop.

### Quick start
```bash
# Install dependency for DOCX creation
pip install python-docx
```

```python
from pathlib import Path
from reportify_pro import DocumentGenerator, REPORT_TEMPLATES, ReportData

data = ReportData(
    template_key="vulnerability_assessment",
    category="Security",
    title="Q3 Vulnerability Assessment",
    author="Sam Jackson",
    executive_summary="High-level summary of the assessment findings.",
    objectives=["Identify vulnerabilities", "Provide remediation guidance"],
    methodology="Automated scanning plus manual validation.",
    findings=["Critical SQL injection in login flow", "Outdated OpenSSL on web tier"],
    recommendations=["Patch web server", "Harden authentication flows"],
)

template = REPORT_TEMPLATES[data.template_key]
DocumentGenerator.generate_report(data, template, Path("reports/q3_assessment.docx"))
```

Open `cybersecurity_report_arsenal.html` in a browser to draft findings, gather guidance, and export a JSON skeleton that you can map onto the Python generator. Prefer a desktop workflow? Run `python reportify_gui.py` for the Tkinter-powered GUI and use the built-in save/export actions.

**Status key:** 🟢 Done · 🟠 In Progress · 🔵 Planned

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

### Commercial E-commerce & Booking Systems
**Description** Built and managed: resort booking site; high-SKU flooring store; tours site with complex variations.
**Links**: [Repo/Folder](./projects/08-web-data/PRJ-WEB-001/) · [Evidence](./projects/08-web-data/PRJ-WEB-001/assets)

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
