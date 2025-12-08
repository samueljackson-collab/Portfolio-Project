# PRJ-HOME-002 Assets

This directory contains supporting materials for the Virtualization & Core Services project.

## Links
- [Diagrams](./diagrams/README.md)
- [Project Overview](../README.md)

## What Goes Here

### 📊 diagrams/
Architecture and design diagrams:
- Service architecture (Proxmox, VMs, containers)
- Data flow diagrams (user → proxy → services)
- Network connectivity diagrams

**Format:** PNG, SVG, Mermaid (`.mmd`), Markdown overlays

### ⚙️ configs/
Service configuration files:
- Docker Compose bundles (Wiki.js, Home Assistant, Immich, PostgreSQL)
- Proxmox VM/LXC definitions and backup policies
- Nginx Proxy Manager configs (sanitized)
- TrueNAS dataset/share configurations

**Format:** YAML, JSON, TXT, MD

**Important:** Sanitize domain names, IPs, and credentials

### 📝 docs/
Written documentation:
- Deployment and DR playbooks
- Backup strategy and retention notes
- Troubleshooting and lessons learned

**Format:** Markdown (.md)

### 📷 screenshots/
Visual evidence:
- Proxmox dashboard
- Service interfaces
- Backup logs/status
- Monitoring views

**Format:** PNG (descriptions tracked in `service-screenshots.md`)

## Security Reminder

Before uploading:
- [ ] Replace real domains with example.com
- [ ] Remove real IPs, passwords, API keys
- [ ] Check screenshots for sensitive information
- [ ] Blur or crop personal data
