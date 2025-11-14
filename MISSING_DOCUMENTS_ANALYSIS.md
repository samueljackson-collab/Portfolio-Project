# Missing Documents & Improvement Analysis

**Updated:** 19 November 2025  
**Purpose:** Provide a truthful gap assessment covering (1) artefacts that still need to be captured, (2) polish work that will raise storytelling quality, and (3) dependencies blocking recovery of legacy assets.

---

## 1. Executive Summary

- ✅ **Homelab, core services, and observability stacks are fully documented** with diagrams, configs, and runbooks already checked in.
- 🟠 **Infrastructure expansion and professional collateral need additional deliverables** (Terraform modules, resumes, executive summaries).
- 🔄 **Commercial e-commerce recovery is still blocked on offline backups**, so directories remain mostly placeholders until data is sanitised and re-imported.

Use the tables and project notes below to plan uploads and prioritise effort.

---

## 2. Status Matrix

| Project / Workstream | README | Assets | Supporting Docs | Primary Gaps |
|----------------------|--------|--------|-----------------|--------------|
| **PRJ-HOME-001 · Homelab Network** | ✅ Complete | ✅ Populated | ✅ Complete | Visual polish (photos, heatmaps) |
| **PRJ-HOME-002 · Virtualisation & Core Services** | ✅ Complete | ✅ Populated | ✅ Complete | Service UI screenshots, Ceph performance note |
| **PRJ-SDE-002 · Observability & Backups** | ✅ Complete | ✅ Populated | ✅ Complete | Dashboard screenshots, optional demo compose |
| **PRJ-SDE-001 · Database IaC** | ✅ Complete | 🟡 Partial | 🟡 Partial | Additional Terraform modules, CI/CD, diagrams |
| **PRJ-WEB-001 · Commercial Recovery** | ✅ Recovery plan | 🟥 Placeholder | 🟥 Placeholder | Artefacts still offline; rebuild required |
| **Resume Portfolio** | ✅ Structure | 🟥 Placeholder | 🟥 Placeholder | Five resumes, cover letter, one-pager |

Legend: 🟡 Partial = some artefacts exist but expansion needed. 🟥 Placeholder = directory ready, content missing.

---

## 3. Project-Level Findings

### PRJ-HOME-001 · Homelab & Secure Network Build
- **What’s already committed:**
  - Sanitised pfSense + UniFi exports: `assets/pfsense/pfsense-config.xml`, `assets/unifi/unifi-config.json`.
  - Firewall/IP matrices and VLAN documentation under `assets/configs/`.
  - Physical/logical diagrams (`assets/diagrams/*.mermaid`) and policy documentation (`assets/documentation/`).
  - Day-to-day and emergency runbooks (`RUNBOOK.md`, `assets/runbooks/`).
- **Missing / improvements:**
  - Add optional Wi-Fi heatmap or signal-strength screenshots.
  - Capture rack photos once redaction workflow is final.
  - Produce a one-page “Homelab Quick Reference” for non-technical reviewers.

### PRJ-HOME-002 · Virtualisation & Core Services
- **What’s already committed:** Docker Compose bundles, Proxmox/Ceph configs, Ansible automation, DR rehearsals, and diagrams describing service flows and backup strategy.
- **Missing / improvements:** Screenshot collection (Wiki.js, Immich, Home Assistant), plus a brief Ceph benchmark summary or capacity snapshot.

### PRJ-SDE-002 · Observability & Backups Stack
- **What’s already committed:** Prometheus/Alertmanager/Loki configs, Grafana dashboard JSON, PBS verification scripts, alert runbooks, and architecture diagrams.
- **Missing / improvements:** Sanitised dashboard screenshots and an optional “quick start” compose bundle for demos.

### PRJ-SDE-001 · Database Infrastructure Module
- **What’s already committed:** RDS Terraform module with README and usage notes.
- **Missing / improvements:**
  - Additional modules (VPC, application layer, monitoring integration).
  - Architecture diagram describing module interactions.
  - GitHub Actions workflow for `terraform fmt`, `terraform validate`, and `tfsec`.
  - Example deployment scenario linking all modules together.

### PRJ-WEB-001 · Commercial E-commerce & Booking Systems
- **Current reality:** Asset directories exist but only contain `.gitkeep`; recovery plan documented in project README.
- **Blocking dependencies:** Original SQL dumps, plugin snippets, and process documentation live offline; sanitisation required before commit.
- **Next actions:**
  1. Catalog restored artefacts and log progress in `PROJECT_COMPLETION_CHECKLIST.md`.
  2. Rebuild architectural diagrams and ERDs from recovered data.
  3. Draft anonymised case studies and operational runbooks.

### Professional Resume Portfolio
- **Current reality:** Directory skeleton only.
- **Next actions:**
  - Draft System Development Engineer resume referencing homelab accomplishments first.
  - Produce tailored Cloud/QA/Networking/Security variants.
  - Add cover letter template and one-page portfolio synopsis referencing [reports/homelab-outcome-report.md](./reports/homelab-outcome-report.md).

---

## 4. Completed Foundations
- Linked README references to populated evidence folders (see `reports/readme-link-report.md`).
- Uploaded comprehensive homelab artefacts covering configs, diagrams, runbooks, and verification scripts.
- Delivered outcome report tying programme proposal → implementation → observability proof.

---

## 5. Active Gaps & Opportunities

| Category | Description | Recommended Follow-up |
|----------|-------------|------------------------|
| Visual collateral | Lack of screenshots/photos across completed projects | Schedule photo/screenshot capture session; sanitise and upload |
| Recruiter collateral | No resume set or quick-reference packet | Draft resume variants; compile 1–2 page executive summary |
| Infrastructure depth | Terraform story limited to RDS | Build out VPC/app/monitoring modules + CI guardrails |
| Legacy evidence | Commercial artefacts offline | Follow recovery plan, prioritise SQL + automation scripts |
| Storytelling | Few direct metrics surfaced in docs | Add KPI summaries to project READMEs or outcome report appendices |

---

## 6. Keeping This Report Current
1. **After every upload**, update the status matrix above to keep stakeholders aligned.
2. **When optional polish is complete**, move the item into “Completed Foundations” so improvements are visible.
3. **Cross-link new artefacts** from project READMEs and the main portfolio README to maintain traceability.
4. **Log recovery progress** for PRJ-WEB-001 and the resume set so work doesn’t stall unnoticed.

Maintaining this document ensures the portfolio remains transparent about strengths, gaps, and in-flight work.
