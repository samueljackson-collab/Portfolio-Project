# PRJ-HOME-002: Virtualization & Core Services - Operations Runbook

**Version:** 1.0
**Last Updated:** November 10, 2025
**Maintainer:** Samuel Jackson
**Project Status:** ✅ Completed

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Reference](#quick-reference)
3. [Detailed Runbooks](#detailed-runbooks)
4. [Common Operations](#common-operations)
5. [Emergency Procedures](#emergency-procedures)
6. [Maintenance Schedule](#maintenance-schedule)

---

## Overview

### Purpose
This runbook provides comprehensive operational procedures for managing the homelab virtualization platform including Proxmox VE cluster, distributed Ceph storage, core infrastructure services, and automated backup/recovery operations.

### Scope
- **Virtualization:** 3-node Proxmox VE cluster with HA
- **Storage:** Ceph RBD (distributed), Local LVM, TrueNAS (NFS/iSCSI)
- **Core Services:** FreeIPA, Pi-hole, Nginx, Rsyslog, NTP
- **Automation:** Ansible playbooks, Terraform IaC
- **Backup:** Proxmox Backup Server, 3-2-1 strategy

### Service Level Objectives
- **Availability:** 99.95% (HA services)
- **RTO:** 1 hour (critical), 4 hours (core), 24 hours (standard)
- **RPO:** 24 hours (daily backups)

---

## Quick Reference

### Critical Contact Information
- **Primary Admin:** Samuel Jackson
- **Documentation:** `/projects/06-homelab/PRJ-HOME-002/README.md`
- **Backup Location:** PBS (192.168.40.50) + TrueNAS (192.168.40.20)
- **Automation:** `/opt/ansible/` and `/opt/terraform/`

### Cluster Access Points
| System | URL/IP | Port | Purpose |
|--------|--------|------|---------|
| Proxmox Node 1 | https://192.168.40.10:8006 | 8006 | Cluster management |
| Proxmox Node 2 | https://192.168.40.11:8006 | 8006 | Cluster management |
| Proxmox Node 3 | https://192.168.40.12:8006 | 8006 | Cluster management |
| PBS | https://192.168.40.50:8007 | 8007 | Backup management |
| TrueNAS | https://192.168.40.20 | 443 | Storage management |

### Core Services Quick Reference
| Service | IP Address | Purpose | Status Check |
|---------|------------|---------|--------------|
| FreeIPA | 192.168.40.25 | LDAP/RADIUS/CA | `curl -k https://192.168.40.25/ipa/ui/` |
| Pi-hole | 192.168.40.35 | DNS/Ad-blocking | `dig @192.168.40.35 google.com` |
| Nginx | 192.168.40.40 | Reverse proxy | `curl -k https://192.168.40.40` |
| Rsyslog | 192.168.40.30 | Log aggregation | `nc -zv 192.168.40.30 514` |
| NTP | 192.168.40.45 | Time sync | `ntpdate -q 192.168.40.45` |

### Cluster Health Check Commands
```bash
# SSH to any Proxmox node
ssh root@192.168.40.10

# Cluster status
pvecm status

# VM list
qm list

# HA status
ha-manager status

# Ceph health (if using Ceph)
ceph status

# Storage status
pvesm status
```

---

## Detailed Runbooks

This project includes several comprehensive runbooks located in `assets/runbooks/`:

### 1. Proxmox Cluster Operations Runbook
**Location:** `assets/runbooks/PROXMOX_CLUSTER_OPERATIONS.md`

**Covers:**
- Cluster management and health monitoring
- VM lifecycle management (create, start, stop, delete)
- Live VM migration between nodes
- High availability configuration and testing
- Performance monitoring and troubleshooting
- Emergency procedures (node failure, cluster failure)

**Use When:**
- Managing VMs or cluster nodes
- Performing live migrations
- Troubleshooting cluster or VM issues
- Testing HA failover
- Planning node maintenance

### 2. Backup and Recovery Operations Runbook
**Location:** `assets/runbooks/BACKUP_RECOVERY_RUNBOOK.md`

**Covers:**
- 3-2-1 backup strategy implementation
- Daily/weekly/monthly backup procedures
- VM backup and restore operations
- Configuration backups (Proxmox, services)
- Disaster recovery scenarios and procedures
- Backup verification and testing
- Recovery time/point objectives (RTO/RPO)

**Use When:**
- Performing manual backups
- Restoring VMs from backup
- Testing disaster recovery procedures
- Investigating backup failures
- Planning recovery from data loss

### 3. Service Management Runbook
**Location:** `assets/runbooks/SERVICE_MANAGEMENT_RUNBOOK.md`

**Covers:**
- FreeIPA: User management, RADIUS, LDAP operations
- Pi-hole: DNS configuration, ad-blocking, custom records
- Nginx: Reverse proxy configuration, SSL management
- Rsyslog: Centralized logging, log management
- NTP: Time synchronization, client configuration
- Service dependencies and health checks

**Use When:**
- Managing user accounts (FreeIPA)
- Configuring DNS records (Pi-hole)
- Adding reverse proxy entries (Nginx)
- Troubleshooting authentication or DNS issues
- Checking service health

---

## Common Operations

### Daily Operations

#### 1. Cluster Health Check
```bash
# SSH to any node
ssh root@192.168.40.10

# Quick health check script
/usr/local/bin/health-check.sh

# Or manual checks:
pvecm status              # Cluster membership
qm list                   # All VMs
ha-manager status         # HA resources
ceph status              # Ceph health (if used)
df -h                    # Disk usage
```

**Expected Time:** 5 minutes
**Frequency:** Daily (automated)

#### 2. Review Backup Status
```bash
# Check last backup completion
cat /var/log/vzdump.log | grep "INFO: Finished"

# Via PBS WebGUI
# https://192.168.40.50:8007 → Tasks
# Verify: All backups completed successfully

# Check backup storage usage
pvesm status | grep -E "pbs|truenas"
```

**Expected Time:** 5 minutes
**Frequency:** Daily

#### 3. Monitor Core Services
```bash
# Run automated health check
ssh admin@192.168.40.35
/usr/local/bin/health-check.sh

# Or via Ansible
cd /opt/ansible
ansible-playbook playbooks/check-services.yml

# Expected: All services return ✓ OK
```

**Expected Time:** 5 minutes
**Frequency:** Automated every 5 minutes

### Weekly Operations

#### 1. Update Systems
```bash
# Update Proxmox nodes (one at a time)
ssh root@192.168.40.10

# Check for updates
apt update
apt list --upgradable

# Apply updates (if non-kernel)
apt upgrade -y

# If kernel update required, plan node maintenance
# See: assets/runbooks/PROXMOX_CLUSTER_OPERATIONS.md → Node Maintenance

# Update VMs via Ansible
cd /opt/ansible
ansible-playbook playbooks/maintenance-updates.yml
```

**Expected Time:** 1 hour
**Frequency:** Weekly

#### 2. Storage Capacity Review
```bash
# Check all storage usage
pvesm status

# Check Ceph usage
ceph df

# Check TrueNAS
# https://192.168.40.20 → Storage → Pools

# Alert if any storage >80% full
```

**Expected Time:** 10 minutes
**Frequency:** Weekly

#### 3. Log Review
```bash
# Review centralized logs
ssh admin@192.168.40.30
cd /var/log/remote

# Check for errors in last week
grep -r "error\|fail\|critical" . --include="*.log" | less

# Review Proxmox cluster logs
ssh root@192.168.40.10
journalctl -p err -since "1 week ago"
```

**Expected Time:** 15 minutes
**Frequency:** Weekly

### Monthly Operations

#### 1. Test Backup Restore
**See:** `assets/runbooks/BACKUP_RECOVERY_RUNBOOK.md` → Testing Procedures

```bash
# Restore test VM from backup
ssh root@192.168.40.10

# Restore to test VM ID
qmrestore pbs-backup:backup/vm/101/latest 999 --storage local-lvm

# Start and verify
qm start 999
qm status 999

# Cleanup
qm stop 999
qm destroy 999 --purge

# Document results
echo "$(date): Backup restore test successful" >> /var/log/backup-tests.log
```

**Expected Time:** 30 minutes
**Frequency:** Monthly

#### 2. Security Audit
```bash
# Check for unauthorized VMs
qm list | awk '{print $1,$2}' | sort

# Review FreeIPA user accounts
ssh admin@192.168.40.25
ipa user-find --all | grep "User login" | wc -l
# Compare to expected count

# Check Nginx access logs for anomalies
ssh admin@192.168.40.40
tail -1000 /var/log/nginx/access.log | \
  awk '{print $1}' | sort | uniq -c | sort -rn | head -20
```

**Expected Time:** 1 hour
**Frequency:** Monthly

#### 3. Performance Baseline
```bash
# Test network between nodes
ssh root@192.168.40.10
iperf3 -s

# From another node
ssh root@192.168.40.11
iperf3 -c 192.168.40.10

# Test storage performance
fio --name=test --ioengine=libaio --rw=randrw --bs=4k \
    --size=1G --numjobs=4 --runtime=60 --group_reporting

# Document results for trending
```

**Expected Time:** 30 minutes
**Frequency:** Monthly

### Quarterly Operations

#### 1. Disaster Recovery Test
**See:** `assets/runbooks/BACKUP_RECOVERY_RUNBOOK.md` → Disaster Recovery

```bash
# Full DR test on spare hardware
# 1. Simulate complete cluster failure
# 2. Rebuild cluster from scratch
# 3. Restore all critical VMs
# 4. Verify all services operational
# 5. Document RTO/RPO achieved
```

**Expected Time:** 3-4 hours
**Frequency:** Quarterly
**Last Test:** November 1, 2025
**Next Test:** February 1, 2026

#### 2. Cluster Maintenance Window
```bash
# Full cluster maintenance
# 1. Update all nodes to latest Proxmox version
# 2. Update Ceph (if used)
# 3. Firmware updates
# 4. Cable inspection
# 5. UPS battery test

# See: assets/runbooks/PROXMOX_CLUSTER_OPERATIONS.md → Node Maintenance
```

**Expected Time:** 4-6 hours
**Frequency:** Quarterly

#### 3. Documentation Review
```bash
# Review and update all documentation
# 1. Verify IP addresses are current
# 2. Update VM inventory
# 3. Review and update runbooks
# 4. Update network diagrams
# 5. Review disaster recovery plan
```

**Expected Time:** 2 hours
**Frequency:** Quarterly

---

## Emergency Procedures

### P0: Single Node Failure
**Expected Response Time:** Immediate
**See:** `assets/runbooks/PROXMOX_CLUSTER_OPERATIONS.md` → Emergency Procedures

**Quick Steps:**
1. Don't panic - HA will auto-migrate VMs
2. Verify HA status on surviving nodes
3. Check for any non-HA VMs that need manual start
4. Monitor remaining nodes for stability
5. Plan node recovery or replacement

**Expected RTO:** 5 minutes (HA VMs), 1 hour (non-HA)

### P0: Complete Cluster Failure
**Expected Response Time:** Immediate
**See:** `assets/runbooks/BACKUP_RECOVERY_RUNBOOK.md` → Disaster Recovery

**Quick Steps:**
1. Assess: Power outage? Network failure? Multiple hardware failures?
2. Power on nodes in order (wait for each to boot)
3. Verify cluster quorum forms
4. Check Ceph status (if used)
5. Start critical VMs if not auto-started
6. Restore from backup if data loss

**Expected RTO:** 1 hour (critical services), 4-24 hours (full recovery)

### P0: Critical Service Down (FreeIPA, Pi-hole)
**Expected Response Time:** 5 minutes
**See:** `assets/runbooks/SERVICE_MANAGEMENT_RUNBOOK.md` → Service Management

**Quick Steps:**
1. Identify which service is down
2. SSH to service VM
3. Check service status
4. Restart service if stopped
5. If VM won't start, restore from backup
6. Verify service functionality

**Expected RTO:** 15 minutes (restart), 1 hour (restore)

### P1: Storage Degraded (Ceph Warning)
**Expected Response Time:** 15 minutes
**See:** `assets/runbooks/PROXMOX_CLUSTER_OPERATIONS.md` → Troubleshooting

**Quick Steps:**
1. Check Ceph status: `ceph status`
2. Check Ceph health detail: `ceph health detail`
3. Identify down OSDs: `ceph osd tree`
4. Attempt to start down OSDs
5. Monitor recovery progress
6. Escalate if >2 OSDs down

**Expected RTO:** 1-4 hours for recovery

### P1: Backup Failure
**Expected Response Time:** 4 hours
**See:** `assets/runbooks/BACKUP_RECOVERY_RUNBOOK.md` → Backup Operations

**Quick Steps:**
1. Check backup logs: `cat /var/log/vzdump.log`
2. Identify failed VM and reason
3. Check storage space on PBS and TrueNAS
4. Manually retry backup: `vzdump <VMID> --storage pbs-backup`
5. Verify backup completion
6. Document issue

**Expected RTO:** 4 hours to resolve

---

## Maintenance Schedule

### Daily (Automated)
- ✅ Cluster health monitoring
- ✅ VM backups to PBS (2:00 AM)
- ✅ Core services health check (every 5 min)
- ✅ Log aggregation to Rsyslog
- ✅ Backup verification

### Weekly (Manual - 1-2 hours)
- System security updates (Proxmox nodes + VMs)
- Storage capacity review
- Log review for anomalies
- Full VM backups to TrueNAS (Sunday 1:00 AM - automated)
- Backup cleanup (prune old backups)

### Monthly (Manual - 2-3 hours)
- Backup restore test
- Security audit (user accounts, access logs)
- Performance baseline testing
- VM inventory review
- Certificate expiration check
- Ansible playbook execution (maintenance)

### Quarterly (Manual - 4-8 hours)
- Full disaster recovery test
- Cluster maintenance window
- Major version updates (Proxmox, Ceph)
- Hardware inspection
- Documentation review and updates
- Capacity planning

---

## Automation

### Ansible Playbooks

**Location:** `/opt/ansible/playbooks/` or `assets/automation/ansible/playbooks/`

Available playbooks:
- `provision-infrastructure.yml` - Initialize Proxmox nodes
- `deploy-services.yml` - Deploy core services
- `maintenance-updates.yml` - Apply security updates
- `backup-operations.yml` - Backup procedures
- `security-hardening.yml` - Security controls
- `check-services.yml` - Service health checks

**Usage:**
```bash
cd /opt/ansible
ansible-playbook playbooks/maintenance-updates.yml

# With tags
ansible-playbook playbooks/deploy-services.yml --tags "pihole,nginx"

# Dry run
ansible-playbook playbooks/maintenance-updates.yml --check
```

### Terraform Infrastructure

**Location:** `/opt/terraform/` or `assets/automation/terraform/`

**Usage:**
```bash
cd /opt/terraform

# Initialize
terraform init

# Plan changes
terraform plan

# Apply changes
terraform apply

# Destroy resources
terraform destroy
```

### Operational Scripts

**Location:** `/usr/local/bin/` or `assets/automation/scripts/`

Available scripts:
- `health-check.sh` - Check all service health
- `backup-verify.sh` - Verify backup completion
- `security-scan.sh` - Vulnerability scanning
- `disaster-recovery.sh` - DR automation

---

## Configuration Management

### Configuration Backup Locations
- **Proxmox Node Configs:** `/etc/pve/` (replicated across cluster)
- **VM Configs:** Included in VM backups
- **Service Configs:** `/opt/configs/` + Git repository
- **Ansible Inventory:** `/opt/ansible/inventory/`
- **Terraform State:** Remote backend (configured)

### Git Repository Integration
```bash
# Configuration changes should be committed to Git
cd /opt/configs

# Add changes
git add .
git commit -m "Update nginx proxy configuration"
git push

# Backup configurations
ansible-playbook /opt/ansible/playbooks/backup-configs.yml
```

---

## Monitoring and Alerting

### Health Monitoring
- **Method:** Automated health checks every 5 minutes
- **Script:** `/usr/local/bin/health-check.sh`
- **Alerts:** Email/Slack on failure
- **Dashboard:** Proxmox WebGUI + Custom dashboard (if Grafana deployed)

### Alert Conditions
- Cluster node offline
- VM unexpectedly stopped
- HA failover event
- Backup job failure
- Storage >85% full
- Ceph health warning/error
- Service health check failure

### Alert Destinations
- **Email:** admin@homelab.local
- **Slack:** #homelab-alerts (if configured)
- **Log:** `/var/log/alerts.log`

---

## Troubleshooting Quick Guide

### "Cluster shows node offline"
1. Can you ping the node? If no → network or power issue
2. Can you SSH to the node? If no → node is down
3. Check cluster logs: `journalctl -u pve-cluster`
4. Check corosync: `systemctl status corosync`
5. Restart services: `systemctl restart pve-cluster corosync`

### "VM won't start"
1. Check VM config: `qm config <VMID>`
2. Check for locks: `qm unlock <VMID>`
3. Check storage: `pvesm list <STORAGE>`
4. Check logs: `journalctl -u qemu-server@<VMID>`
5. Try starting from command line: `qm start <VMID>`

### "Backup failed"
1. Check backup log: `cat /var/log/vzdump.log`
2. Check storage space on target
3. Check VM is running (snapshot mode required)
4. Manually retry: `vzdump <VMID> --storage pbs-backup`
5. Check PBS connection: `pvesm status | grep pbs`

### "Service not responding"
1. Identify service and VM
2. SSH to VM: `ssh admin@<VM_IP>`
3. Check service: `systemctl status <SERVICE>`
4. Restart service: `systemctl restart <SERVICE>`
5. Check logs: `journalctl -u <SERVICE> -n 50`
6. If persistent, restore from backup

---

## Related Documentation

### Project Documentation
- **Project README:** `/projects/06-homelab/PRJ-HOME-002/README.md`
- **Disaster Recovery Plan:** `assets/recovery/disaster-recovery-plan.md`
- **Recovery Procedures:** `assets/recovery/recovery-procedures/`

### Configuration Files
- **Proxmox Configs:** `assets/proxmox/`
- **Service Configs:** `assets/services/`
- **Automation:** `assets/automation/`

### External Resources
- [Proxmox VE Documentation](https://pve.proxmox.com/wiki/)
- [Ceph Documentation](https://docs.ceph.com/)
- [Ansible Documentation](https://docs.ansible.com/)
- [FreeIPA Documentation](https://www.freeipa.org/page/Documentation)

---

## Change Management

### Making Changes to Infrastructure

**Before Making Changes:**
1. Document planned change
2. Backup affected VMs/configs
3. Test in development environment (if possible)
4. Schedule maintenance window (for major changes)
5. Review runbooks for relevant procedures
6. Notify affected users

**During Changes:**
1. Follow runbook procedures
2. Make incremental changes
3. Test after each change
4. Document actual steps taken
5. Monitor for issues

**After Changes:**
1. Verify all services operational
2. Run health checks: `/usr/local/bin/health-check.sh`
3. Update documentation
4. Create new backups
5. Monitor for 24 hours
6. Close change ticket

**Rollback Procedure:**
1. Stop making changes immediately
2. Assess impact and risk
3. Restore from backup (if needed)
4. Verify services restored
5. Document what happened
6. Schedule post-mortem

---

## Contacts and Escalation

### Self-Service Resources (Tier 1)
- This runbook
- Detailed runbooks in `assets/runbooks/`
- Project README
- Inline documentation in configs

### Community Support (Tier 2)
- r/Proxmox (Reddit)
- r/homelab (Reddit)
- Proxmox Forum
- FreeIPA mailing list

### Professional Support (Tier 3)
- Proxmox Subscription Support
- Commercial support services (if needed)

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-10 | Initial runbook creation | Samuel Jackson |

---

**Next Review Date:** February 10, 2026
**Review Frequency:** Quarterly
**Last DR Test:** November 1, 2025
**Next DR Test:** February 1, 2026

---

*For detailed operational procedures, see the comprehensive runbooks in the `assets/runbooks/` directory.*
