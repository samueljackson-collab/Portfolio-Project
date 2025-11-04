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

**Format:** PNG

---

## Quick Upload Guide

See [QUICK_START_GUIDE.md](../../../../QUICK_START_GUIDE.md) for instructions on how to upload your files to GitHub.

## Security Reminder

Before uploading:
- [ ] Replace real domains with example.com
- [ ] Remove real IPs, passwords, API keys
- [ ] Check screenshots for sensitive information
- [ ] Blur or crop personal data
