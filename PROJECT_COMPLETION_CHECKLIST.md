# Project Completion Checklist

_Last updated: 19 November 2025_

Use this checklist to track what is already live in the repository and which follow-up items remain for each workstream. Items are grouped by **Core Evidence** (must-have), **Polish** (nice-to-have storytelling upgrades), and **Operational Hygiene** (sanitisation, links, automation).

---

## PRJ-HOME-001 · Homelab & Secure Network Build
**Status:** 🟢 Complete – ✅ Evidence Pack Published

### Core Evidence
- [x] Project README documents network design and validation steps
- [x] Sanitised pfSense export committed (`assets/pfsense/pfsense-config.xml`)
- [x] Sanitised UniFi export committed (`assets/unifi/unifi-config.json`)
- [x] Firewall/IP matrices documented (`assets/configs/`)
- [x] Physical & logical diagrams available (`assets/diagrams/*.mermaid`)
- [x] Deployment & operations runbooks published (`RUNBOOK.md`, `assets/runbooks/`)

### Polish & Storytelling
- [ ] Wi-Fi heatmap or coverage screenshots (optional)
- [ ] Rack photos with sensitive elements redacted (optional)
- [ ] One-page “Homelab Quick Reference” for recruiters

### Operational Hygiene
- [x] Sensitive data sanitised prior to upload
- [x] README links validated from root portfolio
- [ ] Visual assets reviewed for metadata before publishing

---

## PRJ-HOME-002 · Virtualisation & Core Services
**Status:** 🟢 Complete – ✅ Evidence Pack Published

### Core Evidence
- [x] Project README explains architecture, Ceph tiers, and service layout
- [x] Docker Compose bundles committed (`assets/configs/`)
- [x] Proxmox/Ceph configuration exports stored (`assets/proxmox/`, `assets/services/`)
- [x] Automation scripts/playbooks added (`assets/automation/`)
- [x] Backup & recovery runbooks/logs available (`assets/runbooks/`, `assets/recovery/`)
- [x] Architecture & backup diagrams published (`assets/diagrams/`)

### Polish & Storytelling
- [ ] Screenshot gallery (Wiki.js, Immich, Home Assistant)
- [ ] Ceph performance snapshot or benchmark notes
- [ ] “Services map” infographic summarising platform surface area

### Operational Hygiene
- [x] Sensitive data sanitised prior to upload
- [x] README links validated from root portfolio
- [ ] Screenshots and media sanitised (EXIF/PII) before commit

---

## PRJ-SDE-002 · Observability & Backups Stack
**Status:** 🟢 Complete – ✅ Evidence Pack Published

### Core Evidence
- [x] Project README outlines monitoring scope and golden signals
- [x] Prometheus configuration committed (`assets/configs/prometheus.yml`)
- [x] Alertmanager + alert rules committed (`assets/alertmanager/`)
- [x] Loki & Promtail configuration committed (`assets/loki/`)
- [x] Grafana dashboards exported as JSON (`assets/grafana/`)
- [x] PBS verification scripts and logs included (`assets/scripts/`, `assets/logs/`)
- [x] Alert response runbooks documented (`assets/runbooks/`)

### Polish & Storytelling
- [ ] Sanitised dashboard screenshots for quick review
- [ ] Optional docker-compose quickstart bundle for demo environments

### Operational Hygiene
- [x] Sensitive data sanitised prior to upload
- [x] README links validated from root portfolio
- [ ] Monitoring artefacts referenced in resume/portfolio summaries

---

## PRJ-SDE-001 · Database Infrastructure Module
**Status:** 🟠 In Progress – Core RDS Module Delivered

### Core Evidence
- [x] Terraform RDS module committed with README and usage instructions
- [ ] VPC module implemented and documented
- [ ] Application/service module implemented and documented
- [ ] Monitoring/observability module implemented and documented

### Polish & Storytelling
- [ ] Architecture diagram showing module interactions
- [ ] Example environment tying all modules together
- [ ] Cost, security, and scaling considerations captured in README

### Operational Hygiene
- [ ] GitHub Actions workflow running `terraform fmt`, `terraform validate`, and `tfsec`
- [ ] Example CI plan/apply process documented
- [x] Links validated from portfolio README

---

## PRJ-WEB-001 · Commercial E-commerce & Booking Systems
**Status:** 🔄 Recovery – Artefacts Offline

### Recovery Phase 1 · Catalog & Restore
- [ ] Locate and sanitise SQL/database exports
- [ ] Reconstruct ERD and data-flow diagrams
- [ ] Recover automation scripts (cron, import/export)
- [ ] Identify reusable code snippets for publication

### Recovery Phase 2 · Document & Narrate
- [ ] Rebuild operational runbooks (CMS workflows, deployments)
- [ ] Capture architectural decisions and lessons learned
- [ ] Draft anonymised case studies with key metrics

### Recovery Phase 3 · Publish
- [ ] Commit sanitised SQL/code samples
- [ ] Upload diagrams and screenshots (metadata scrubbed)
- [ ] Update README with recovered artefacts and links

### Operational Hygiene
- [ ] Recovery log updated in `MISSING_DOCUMENTS_ANALYSIS.md`
- [ ] Sensitive client data removed/redacted prior to commit
- [ ] Portfolio README status updated once artefacts land

---

## Professional Resume Portfolio
**Status:** 🟠 In Progress – Structure Only

### Core Deliverables
- [ ] System Development Engineer resume (Markdown + PDF)
- [ ] Cloud Engineer resume (Markdown + PDF)
- [ ] QA Engineer resume (Markdown + PDF)
- [ ] Network Engineer resume (Markdown + PDF)
- [ ] Cybersecurity Analyst resume (Markdown + PDF)
- [ ] Cover letter template linked to homelab outcomes
- [ ] One-page portfolio summary referencing evidence packs

### Polish & Storytelling
- [ ] Tailor skills/metrics per role with direct repo links
- [ ] Prepare recruiter outreach email template referencing new artefacts

### Operational Hygiene
- [ ] Check formatting with ATS validator prior to commit
- [ ] Ensure personal/contact data accurate and up to date
- [ ] Confirm README + navigation docs link to resume files

---

## Global Checklist

### Security & Privacy
- [ ] No real IP addresses, passwords, domains, or client identifiers in committed artefacts
- [ ] Screenshots scrubbed for EXIF/metadata and sensitive UI elements
- [ ] `.gitignore` updated when new tooling introduces secret-bearing files

### Documentation Maintenance
- [ ] Update `COMPLETION_SUMMARY.md` after major uploads
- [ ] Update `MISSING_DOCUMENTS_ANALYSIS.md` when gaps close
- [ ] Verify portfolio README links whenever new artefacts are added

### Automation & Quality
- [ ] Run lint/validation scripts for Terraform, Markdown, and YAML before commits
- [ ] Track recovery tasks and resume progress in issue tracker or task list
- [ ] Capture changelog entries for significant documentation updates

Stay disciplined about checking items off in Git; the history becomes a record of progress for collaborators and hiring managers alike.
