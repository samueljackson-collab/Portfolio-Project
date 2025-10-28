# PRJ-HOME-002: Virtualization & Core Services

**Status:** 🟢 Completed (Documentation Pending)
**Category:** Homelab & Virtualization
**Technologies:** Proxmox, TrueNAS, Docker, Nginx Proxy Manager, Let's Encrypt

---

## Overview

Built a virtualization platform hosting multiple self-hosted services with reverse proxy, TLS encryption, and automated backups.

## Core Technologies

### Proxmox VE
- Type-1 hypervisor for virtual machines and containers
- Web-based management interface
- High availability clustering support (single-node setup)
- Snapshot and backup management

### TrueNAS
- Network-attached storage for media, backups, and shared data
- ZFS filesystem for data integrity
- Automated snapshot scheduling
- SMB/NFS shares for cross-platform access

## Hosted Services

### 1. Wiki.js
- Knowledge base and documentation platform
- Markdown-based content
- Version control integration
- Full-text search

### 2. Home Assistant
- Home automation hub
- IoT device integration
- Automation rules and scenes
- Energy monitoring

### 3. Immich
- Self-hosted photo and video backup
- Mobile app for automatic uploads
- Facial recognition and smart search
- Alternative to Google Photos

### 4. Reverse Proxy (Nginx Proxy Manager)
- Centralized SSL/TLS termination
- Let's Encrypt certificate automation
- Access control and authentication
- Custom domain routing

## Security & Access

- **TLS Encryption** - All services accessible via HTTPS
- **Internal DNS** - Local domain resolution (homelab.local or similar)
- **Authentication** - Service-level logins with MFA where supported
- **Network Isolation** - Services on separate VLAN from IoT and guest networks
- **Regular Updates** - Automated security patches for host and guests

## Backup Strategy

### Local Backups
- Proxmox Backup Server (PBS) for VM/container backups
- Daily incremental, weekly full backups
- Retention policy: 7 daily, 4 weekly, 3 monthly

### Offsite Backups
- Critical data backed up to cloud storage (encrypted)
- 3-2-1 backup rule: 3 copies, 2 different media, 1 offsite

## Skills Demonstrated

- Virtualization platform management
- Service deployment and orchestration
- Reverse proxy configuration
- Certificate management and automation
- Backup and recovery procedures
- Storage management (ZFS)

## Documentation Status

📝 **Pending:** Architecture diagrams, service configurations, and backup logs are being organized and will be added to the `assets/` directory.

## Lessons Learned

- Start with backups before experimenting
- Document configurations before making changes
- Use infrastructure as code where possible
- Plan storage capacity ahead of time
- Network segmentation is critical for security

---

**Last Updated:** October 28, 2025
