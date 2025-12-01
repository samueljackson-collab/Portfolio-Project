# PRJ-HOME-002 Assets

Supporting materials for the Virtualization & Core Services project (Proxmox, TrueNAS, and core application stack). All examples are sanitized.

## Navigation
- [Diagrams](./diagrams/) — Architecture, data flow, network topology, monitoring, and DR visuals.
- [Configs](./configs/) — Docker Compose definitions, Proxmox baselines, sanitized Nginx Proxy Manager export, and TrueNAS layouts.
- [Docs](./docs/) — Deployment, backup strategy, disaster recovery, troubleshooting, and lessons learned.
- [Proxmox](./proxmox/) — Cluster, storage, networking, backup policies, and VM templates.
- [Screenshots](./screenshots/) — Sanitized captures of services and infrastructure dashboards.
- [Logs](./logs/) — Sample operational and backup logs.
- [Runbooks](./runbooks/) — Operations references for backups, Proxmox cluster care, and service management.
- [Recovery](./recovery/) — DR/BCP procedures and offline artifacts.
- [Services](./services/) — Service-level details and inventories.

## What Goes Here
### 📊 diagrams/
Architecture and design diagrams:
- Service architecture (Proxmox, VMs, containers)
- Data flow diagrams (user → proxy → services)
- Network connectivity diagrams
- Monitoring and DR flows

**Format:** Mermaid (`.md`, `.mmd`) with conversion scripts for PNG.

### ⚙️ configs/
Service configuration files:
- Docker Compose files (Wiki.js, Home Assistant, Immich, PostgreSQL, full-stack)
- Proxmox VM/LXC configurations and cloud-init templates
- Nginx Proxy Manager configs (sanitized)
- TrueNAS dataset/share configurations

**Format:** YAML, JSON, MD

### 📝 docs/
Written documentation:
- Deployment guide and operational checklist
- Backup strategy, retention, and verification notes
- Disaster recovery plan and troubleshooting guide
- Lessons learned from DR drills and day-2 operations

### 📷 screenshots/
Visual evidence:
- Proxmox dashboard and HA groups
- Core service interfaces (Wiki.js, Home Assistant, Immich)
- Backup/monitoring dashboards

---

## Security Reminder
Before uploading:
- [ ] Replace real domains with example.com
- [ ] Remove real IPs, passwords, API keys
- [ ] Check screenshots for sensitive information
- [ ] Blur or crop personal data
