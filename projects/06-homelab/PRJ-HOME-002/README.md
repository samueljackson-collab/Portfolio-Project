# Virtualization & Core Services

## Documentation
For cross-project documentation, standards, and runbooks, see the [Portfolio Documentation Hub](../../../DOCUMENTATION_INDEX.md).


**Status:** 🟢 Done

## Description

Proxmox/TrueNAS host running Wiki.js, Home Assistant, and Immich behind a reverse proxy with TLS.

## Links

- [Parent Documentation](../../../README.md)
- [Evidence Assets](./assets)

## Next Steps

- Cross-check PBS job definitions with the latest backup report under `assets/configs/monitoring/pbs-backup-report.md`.
- Rotate sanitized screenshots quarterly to reflect patch levels and storage utilization trends.
- Expand observability rules as new services land on the cluster.

## Contact

For questions about this project, please reach out via [GitHub](https://github.com/sams-jackson) or [LinkedIn](https://www.linkedin.com/in/sams-jackson).

---

## Code Generation Prompts

- [x] README scaffold produced from the [Project README generation prompt](../../../AI_PROMPT_LIBRARY.md#project-readme-baseline).
- [x] Virtualization evidence checklist aligned to the [Prompt Execution Framework workflow](../../../AI_PROMPT_EXECUTION_FRAMEWORK.md#prompt-execution-workflow).

---

## Evidence Artifacts
- **Backup & Observability Logs:** `assets/configs/monitoring/pbs-backup-report.md` and `observability-snapshots.md` document PBS, Prometheus, Grafana, and Loki excerpts.
- **Service Mapping:** See `assets/configs/monitoring/observability-snapshots.md` for cluster-level health thresholds tied to FreeIPA, Pi-hole, and Nginx reverse proxy.
- **Screenshots:** `assets/screenshots/` includes sanitized Proxmox, TrueNAS, and service proxy captures.
- **Logs:** `assets/logs/` provides sanitized cluster health and PBS backup summaries.

# PRJ-HOME-002: Virtualization & Core Services

**Status:** ✅ Completed  
**Category:** Homelab & Virtualization  
**Technologies:** Proxmox VE, Ceph, TrueNAS, Ansible, Terraform, FreeIPA, Nginx  
**Complexity:** Advanced  

---

## Overview

Production-grade virtualization platform featuring a 3-node Proxmox cluster with high availability, distributed Ceph storage, comprehensive core services, and automated infrastructure management. Demonstrates enterprise virtualization skills, infrastructure-as-code practices, and complete operational readiness.

This project showcases advanced systems administration, automation, disaster recovery planning, and production service deployment in a homelab environment.

## Architecture Highlights

- **3-Node HA Cluster:** Proxmox VE with Corosync and automatic VM failover
- **Distributed Storage:** Ceph RBD with 3-way replication for data redundancy
- **Multi-Tier Storage:** Local LVM, Ceph, NFS, iSCSI, and Proxmox Backup Server
- **Core Infrastructure Services:** FreeIPA, Pi-hole, Nginx, centralized syslog, NTP
- **Automation:** Ansible playbooks and Terraform for infrastructure-as-code
- **Comprehensive DR:** Documented disaster recovery procedures with tested RTO/RPO

## Cluster Architecture

```
3-Node Proxmox Cluster (192.168.40.10-12)
    ↓
├─ Local Storage: LVM-thin on each node (fast VM disks)
├─ Distributed Storage: Ceph RBD (HA VMs, live migration)
├─ Network Storage: TrueNAS NFS/iSCSI (backups, bulk data)
└─ Backup Storage: Proxmox Backup Server (deduplicated backups)

Core Services (VMs on VLAN 40):
├─ FreeIPA (192.168.40.25) - Authentication & RADIUS
├─ Pi-hole (192.168.40.35) - DNS & Ad Blocking  
├─ Nginx (192.168.40.40) - Reverse Proxy & SSL
└─ Syslog (192.168.40.30) - Centralized Logging
```

## Core Infrastructure Services

### 1. FreeIPA - Identity Management

- **Purpose:** Centralized authentication and RADIUS for 802.1X wireless
- **Features:** LDAP directory, Kerberos, internal CA, 2FA support
- **Integration:** Provides RADIUS authentication for WPA3 Enterprise wireless
- **IP:** 192.168.40.25

### 2. Pi-hole - DNS & Ad Blocking

- **Purpose:** Network-wide DNS resolution and advertisement blocking
- **Features:** Custom DNS records, DNSSEC, conditional forwarding, statistics
- **Integration:** Primary DNS for all VLANs, local domain (homelab.local)
- **IP:** 192.168.40.35

### 3. Nginx - Reverse Proxy

- **Purpose:** SSL termination and reverse proxy for internal services
- **Features:** Let's Encrypt automation, load balancing, access control
- **Services Proxied:** Wiki.js, Home Assistant, Proxmox, Grafana, etc.
- **IP:** 192.168.40.40

### 4. Rsyslog - Centralized Logging

- **Purpose:** Aggregate logs from all infrastructure components
- **Features:** Remote syslog (TCP/UDP 514), log retention, organized storage
- **Sources:** pfSense, Proxmox nodes, VMs, switches, access points
- **IP:** 192.168.40.30

### 5. NTP - Time Synchronization

- **Purpose:** Stratum 2 NTP server for accurate time across homelab
- **Upstream:** pool.ntp.org, time.cloudflare.com
- **Clients:** All infrastructure and VMs

## Storage Configuration

### Tier 1 - Local LVM (Performance)

- **Location:** Local SSD/NVMe on each Proxmox node
- **Use Case:** High-performance VM boot disks, non-HA workloads
- **Features:** Thin provisioning, snapshots, fast I/O

### Tier 2 - Ceph RBD (High Availability)

- **Configuration:** 3-node cluster, 3-way replication
- **Use Case:** HA VMs requiring live migration
- **Features:** Distributed, self-healing, automatic replication

### Tier 3 - TrueNAS Storage (Capacity)

- **NFS:** Backups, ISO images, templates, shared files
- **iSCSI:** High-performance block storage for specific workloads
- **ZFS:** Data integrity, snapshots, compression

### Backup Storage - Proxmox Backup Server

- **Features:** Deduplication, compression, incremental backups
- **Retention:** 7 daily, 4 weekly, 12 monthly
- **Verification:** Automated integrity checking

## High Availability Features

### Cluster Configuration

- **Nodes:** 3 (proxmox-01, proxmox-02, proxmox-03)
- **Quorum:** Corosync with automatic quorum
- **HA Groups:** Resource placement preferences and failover policies

### Automatic Failover

- **HA Resources:** Critical VMs (FreeIPA, Pi-hole, Nginx, Syslog)
- **Watchdog:** Hardware watchdog for automatic node recovery
- **Fencing:** Watchdog-based fencing (IPMI optional)
- **Migration:** Automatic VM migration on node failure

### Live Migration

- **Zero Downtime:** Migrate running VMs between nodes
- **Requirements:** Shared storage (Ceph), network connectivity
- **Use Cases:** Maintenance, load balancing, hardware upgrades

## Automation & Infrastructure-as-Code

### Ansible Automation

**Location:** `assets/automation/ansible/playbooks/`

- **provision-infrastructure.yml** - Initialize Proxmox nodes, configure base system
- **deploy-services.yml** - Deploy and configure core services
- **maintenance-updates.yml** - System patching and updates
- **backup-operations.yml** - Automated backup procedures
- **security-hardening.yml** - Apply security controls

### Terraform Infrastructure

**Location:** `assets/automation/terraform/`

- **main.tf** - Proxmox provider and VM resource definitions
- **variables.tf** - Configurable parameters
- **outputs.tf** - Resource outputs (IPs, etc.)
- **backend.tf** - State management

### Operational Scripts

**Location:** `assets/automation/scripts/`

- **backup-verify.sh** - Verify backup completion and integrity
- **health-check.sh** - Check status of all core services
- **security-scan.sh** - Vulnerability scanning
- **disaster-recovery.sh** - DR procedure automation

## Disaster Recovery

### Recovery Objectives

- **Critical Services (P0):** RTO 1 hour, RPO 24 hours
- **Core Services (P1):** RTO 4 hours, RPO 24 hours
- **Standard Apps (P2):** RTO 24 hours, RPO 7 days

### Backup Strategy (3-2-1 Rule)

1. **Production:** VMs running on Ceph/LVM
2. **Local Backup:** Proxmox Backup Server (daily)
3. **Secondary Backup:** TrueNAS NFS (weekly)
4. **Offsite Backup:** Remote rsync (weekly)

### DR Testing

- **Frequency:** Quarterly
- **Last Test:** November 1, 2025
- **Next Test:** February 1, 2026
- **Scenarios:** Service restoration, node failure, complete rebuild

## VM Template System

### Cloud-Init Templates

- **Base Image:** Ubuntu 22.04 LTS
- **Features:** QEMU guest agent, automatic disk expansion, SSH key injection
- **Security:** Hardened with fail2ban, UFW, automatic updates
- **Customization:** Cloud-init for per-VM configuration

### Template Creation

```bash
./assets/proxmox/vm-templates/create-ubuntu-template.sh
```

Creates production-ready VM template (ID 9000) with:

- UEFI boot, TPM 2.0, virtio drivers
- Cloud-init integration
- Security hardening applied
- QEMU guest agent pre-installed

## Project Artifacts

### Proxmox Configuration

- [`cluster.conf`](assets/proxmox/cluster.conf) - 3-node cluster with HA
- [`storage.cfg`](assets/proxmox/storage.cfg) - Multi-tier storage configuration
- [`network-interfaces`](assets/proxmox/network-interfaces) - VLAN-aware networking with bonding
- [`backup-config.json`](assets/proxmox/backup-config.json) - Comprehensive backup strategy
- [`vm-inventory.md`](assets/proxmox/vm-inventory.md) - Sanitized VM list with HA groups and storage tiers
- [`vm-templates/`](assets/proxmox/vm-templates/) - Automated template creation

### Core Services Configuration

- [`pihole/`](assets/services/pihole/) - DNS server with custom records
- [`freeipa/`](assets/services/freeipa/) - Identity management and RADIUS
- [`ntp/`](assets/services/ntp/) - Time synchronization server
- [`nginx/`](assets/services/nginx/) - Reverse proxy and SSL termination
- [`rsyslog/`](assets/services/rsyslog/) - Centralized logging
- [`nginx-proxy-manager`](assets/configs/nginx-proxy-manager/proxy-hosts.yml) - Sanitized reverse-proxy entries

### Storage Layout
- [`dataset-layout.md`](assets/configs/truenas/dataset-layout.md) - TrueNAS dataset purposes and retention
- [`share-definitions.yml`](assets/configs/truenas/share-definitions.yml) - NFS/iSCSI target definitions

### Automation

- [`ansible/playbooks/`](assets/automation/ansible/playbooks/) - 5 playbooks for infrastructure management
- [`terraform/`](assets/automation/terraform/) - IaC for VM provisioning
- [`scripts/`](assets/automation/scripts/) - Operational automation scripts

### Disaster Recovery

- [`disaster-recovery-plan.md`](assets/recovery/disaster-recovery-plan.md) - Comprehensive DR plan with RTO/RPO
- [`recovery-procedures/`](assets/recovery/recovery-procedures/) - Step-by-step recovery guides
- [`disaster-recovery.md`](assets/docs/disaster-recovery.md) - Executable scenarios for node, storage, and site recovery

### Documentation & Operations
- [`deployment.md`](assets/docs/deployment.md) - End-to-end deployment sequence across Proxmox, TrueNAS, and services
- [`troubleshooting.md`](assets/docs/troubleshooting.md) - Common failure domains and fixes
- [`lessons-learned.md`](assets/docs/lessons-learned.md) - Operational insights captured post-deployment
- [`backup-strategy.md`](assets/docs/backup-strategy.md) - Cadence, verification, and responsibilities
- [`logging-and-retention.md`](assets/docs/logging-and-retention.md) - Centralized logging and retention policy
- [`backup-job-log.md`](assets/logs/backup-job-log.md) - Sanitized PBS job history and verification results

### Visuals & Evidence
- [`service-screenshots.md`](assets/screenshots/service-screenshots.md) - Descriptions of captured Proxmox/NPM/TrueNAS views
- [`reverse-proxy-dataflow.mmd`](assets/diagrams/reverse-proxy-dataflow.mmd) - TLS ingress and backend flow for core services

### Config Exports
- [`vm-export-manifest.md`](assets/proxmox/exports/vm-export-manifest.md) - Proxmox VM export inventory
- [`lxc-export-manifest.md`](assets/proxmox/exports/lxc-export-manifest.md) - Proxmox LXC export inventory
- [`npm-config-summary.md`](assets/configs/nginx-proxy-manager/npm-config-summary.md) - Nginx Proxy Manager config summary
- [`system-config-summary.md`](assets/configs/truenas/system-config-summary.md) - TrueNAS system config summary

### Backup Evidence
- [`backup-strategy.md`](assets/docs/backup-strategy.md) - 3-2-1 backup strategy and verification cadence
- [`backup-sample-logs.md`](assets/logs/backup-sample-logs.md) - Sanitized backup/replication log excerpts
- [`restore-test-results.md`](assets/logs/restore-test-results.md) - Quarterly restore test results

### Runbooks
- [`service-deployment-runbook.md`](assets/runbooks/service-deployment-runbook.md) - Service deployment steps
- [`disaster-recovery-runbook.md`](assets/runbooks/disaster-recovery-runbook.md) - DR execution checklist

### Demo & Visualizations

- [`demo/home-assistant-dashboard.html`](demo/home-assistant-dashboard.html) - Interactive Home Assistant dashboard mockup
  - Demonstrates smart home integration with homelab services
  - Features: Climate control, lighting, security monitoring, energy tracking, media player, and service status
  - Live React version available in portfolio frontend at `/home-assistant`
- [`demo/wiki-infrastructure-overview.html`](demo/wiki-infrastructure-overview.html) - Wiki.js infrastructure documentation mockup
- See [`demo/README.md`](demo/README.md) for detailed information about all demo files

## Skills Demonstrated

### Virtualization

- Proxmox VE cluster deployment and management
- High availability configuration
- Live VM migration
- Resource allocation and optimization
- Virtual networking (VLANs, bridges, bonding)

### Storage Management

- Ceph distributed storage configuration
- ZFS administration
- Multi-tier storage strategy
- NFS and iSCSI configuration
- Storage performance tuning

### Automation & IaC

- Ansible playbook development
- Terraform resource provisioning
- Bash scripting for operations
- CI/CD principles
- Configuration management

### Core Services

- LDAP/Kerberos (FreeIPA)
- DNS server administration (Pi-hole)
- Reverse proxy configuration (Nginx)
- Centralized logging (Rsyslog)
- Time synchronization (NTP)

### Disaster Recovery

- DR planning and documentation
- Backup strategy design (3-2-1 rule)
- RTO/RPO definition
- Recovery procedure development
- DR testing and validation

### Security

- Certificate management
- Access control
- Network segmentation
- Security hardening
- Vulnerability management

## Deployment Guide

### Prerequisites

1. 3 physical servers or capable hardware
2. Network infrastructure configured (PRJ-HOME-001)
3. Proxmox VE 8.x installed on all nodes
4. TrueNAS system available for storage

### Initial Cluster Setup

1. Install Proxmox VE on all three nodes
2. Configure networking per `network-interfaces`
3. Create cluster: `pvecm create homelab-cluster`
4. Join nodes: `pvecm add 192.168.40.10`
5. Configure storage per `storage.cfg`

### Core Services Deployment

1. Create VM template: `./vm-templates/create-ubuntu-template.sh`
2. Deploy VMs with Terraform: `terraform apply`
3. Configure services with Ansible: `ansible-playbook playbooks/deploy-services.yml`
4. Verify services: `./scripts/health-check.sh`

### Backup Configuration

1. Deploy Proxmox Backup Server
2. Configure backup jobs per `backup-config.json`
3. Test backup and restore procedures
4. Set up offsite backup sync

## Operational Procedures

### Daily Operations

- Monitor cluster health via web interface
- Review backup completion reports
- Check service availability
- Review centralized logs

### Weekly Maintenance

- Security updates: `ansible-playbook maintenance-updates.yml`
- Backup verification: `./scripts/backup-verify.sh`
- Storage capacity check
- Log review and cleanup

### Monthly Maintenance

- Full security scan: `./scripts/security-scan.sh`
- VM snapshot cleanup
- Documentation updates
- Capacity planning review

### Quarterly Maintenance

- DR testing and validation
- Full cluster maintenance window
- Major version updates
- Security audit

## Monitoring Integration

### Metrics Collection

- Proxmox built-in metrics
- Custom Prometheus exporters
- Service health checks
- Storage utilization

### Alerting

- Email notifications for failures
- Prometheus Alertmanager integration
- Service uptime monitoring
- Backup failure alerts

## Future Enhancements

- [ ] Expand to 5-node cluster for better fault tolerance
- [ ] Implement S3-compatible backup target
- [ ] Deploy Kubernetes cluster on Proxmox
- [ ] Add GPU passthrough for ML workloads
- [ ] Implement automated security scanning
- [ ] Deploy ELK stack for advanced log analysis

## References

- [Proxmox VE Documentation](https://pve.proxmox.com/wiki/)
- [Ceph Documentation](https://docs.ceph.com/)
- [Ansible Documentation](https://docs.ansible.com/)
- [Terraform Proxmox Provider](https://registry.terraform.io/providers/Telmate/proxmox/)

---

**Project Completed:** November 5, 2025  
**Last Updated:** November 5, 2025  
**Maintainer:** Samuel Jackson
