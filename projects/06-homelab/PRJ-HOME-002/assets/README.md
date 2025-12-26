# Virtualization & Core Services

**Status:** 🟢 Done (evidence captured)

## Description

Proxmox/TrueNAS host running Wiki.js, Home Assistant, and Immich behind a reverse proxy with TLS.

## Links

- [Evidence/Diagrams](./assets)
- [Parent Documentation](../README.md)

## Evidence Added

- **Diagrams:** Cluster + storage topology in `diagrams/` (PNG/SVG with editable sources).
- **Observability:** Prometheus/Grafana/Loki excerpts in `configs/monitoring/observability-evidence.md`.
- **Backups:** PBS nightly report in `configs/truenas/pbs-backup-report.md`.
- **Screenshots:** Sanitized Proxmox, TrueNAS, and service proxy snapshots stored in `screenshots/`.
- **Logs:** Sanitized cluster health and PBS backup summaries stored in `logs/`.

## Contact

For questions about this project, please reach out via [GitHub](https://github.com/sams-jackson) or [LinkedIn](https://www.linkedin.com/in/sams-jackson).

---
## Code Generation Prompts
- [x] Asset catalog scaffold produced from the [Evidence and assets prompt](../../../../AI_PROMPT_LIBRARY.md#evidence--assets-catalog).
- [x] Upload/validation checklist aligned to the [Prompt Execution Framework workflow](../../../../AI_PROMPT_EXECUTION_FRAMEWORK.md#prompt-execution-workflow).

---
*Documentation is live; ongoing updates will expand recovery and automation sections.*
# PRJ-HOME-002 Assets

This directory contains supporting materials for the Virtualization & Core Services project.

## What Goes Here

### 📊 diagrams/
Architecture and design diagrams:
- Service architecture (Proxmox, VMs, containers)
- Data flow diagrams (user → proxy → services)
- Network connectivity diagrams

**Format:** PNG, SVG (with editable source files)

### ⚙️ configs/
Service configuration files:
- Docker Compose files (Wiki.js, Home Assistant, Immich)
- Proxmox VM/LXC configurations
- Nginx Proxy Manager configs (sanitized)
- TrueNAS dataset/share configurations

**Format:** YAML, JSON, TXT, MD

**Important:** Sanitize domain names, IPs, and credentials

### 📝 docs/
Written documentation:
- Backup strategy document
- Service deployment runbook
- Disaster recovery procedures
- Restore testing results

**Format:** Markdown (.md)

### 📷 screenshots/
Visual evidence:
- Proxmox dashboard
- Service interfaces
- Backup logs/status
- Monitoring views

---

## Quick Upload Guide

See [QUICK_START_GUIDE.md](../../../../QUICK_START_GUIDE.md) for instructions on how to upload your files to GitHub.

## Security Reminder

Before uploading:
- [ ] Replace real domains with example.com
- [ ] Remove real IPs, passwords, API keys
- [ ] Check screenshots for sensitive information
- [ ] Blur or crop personal data
