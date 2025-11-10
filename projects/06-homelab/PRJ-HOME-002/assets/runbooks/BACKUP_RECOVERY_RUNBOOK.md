# Backup and Recovery Operations Runbook

**Version:** 1.0
**Last Updated:** November 10, 2025
**Maintainer:** Samuel Jackson

---

## Table of Contents

1. [Overview](#overview)
2. [Backup Strategy](#backup-strategy)
3. [Backup Operations](#backup-operations)
4. [Recovery Operations](#recovery-operations)
5. [Disaster Recovery](#disaster-recovery)
6. [Testing Procedures](#testing-procedures)

---

## Overview

### Backup Architecture

**3-2-1 Backup Rule Implementation:**
1. **3 copies** of data: Production + 2 backups
2. **2 different media** types: Ceph/LVM + PBS + TrueNAS
3. **1 offsite** copy: Remote rsync to cloud/remote location

### Backup Infrastructure

| Component | Purpose | Location | Retention |
|-----------|---------|----------|-----------|
| **Proxmox Backup Server (PBS)** | Primary backup target | 192.168.40.50 | 7 daily, 4 weekly, 12 monthly |
| **TrueNAS NFS Share** | Secondary backup | 192.168.40.20:/mnt/backups | Weekly full backups |
| **Remote Sync** | Offsite backup | External location | Weekly sync |

### Recovery Objectives

| Priority | Service Type | RTO | RPO | Example Services |
|----------|-------------|-----|-----|------------------|
| **P0** | Critical | 1 hour | 24 hours | FreeIPA, Pi-hole |
| **P1** | Core | 4 hours | 24 hours | Nginx, Syslog |
| **P2** | Standard | 24 hours | 7 days | Development VMs |
| **P3** | Low | 72 hours | 30 days | Test/Lab VMs |

---

## Backup Strategy

### VM Backup Schedule

#### Daily Backups (Automated)
**Time:** 2:00 AM daily
**Target:** Proxmox Backup Server
**VMs:** All production VMs (P0, P1)

```bash
# Configured via Proxmox WebGUI:
# Datacenter → Backup → Add

# Or via vzdump cron:
cat /etc/cron.d/vzdump
# 0 2 * * * root vzdump --mode snapshot --storage pbs-backup --all 1 --quiet 1
```

#### Weekly Full Backups
**Time:** Sunday 1:00 AM
**Target:** TrueNAS NFS
**VMs:** All VMs (P0-P3)

```bash
# Custom backup script
cat /usr/local/bin/weekly-backup.sh
#!/bin/bash
vzdump --mode snapshot --storage truenas-nfs --all 1 --compress zstd

# Cron entry
crontab -l | grep weekly
# 0 1 * * 0 /usr/local/bin/weekly-backup.sh
```

#### Monthly Archives
**Time:** First Sunday of month
**Target:** PBS (preserved)
**VMs:** Critical VMs only

### Configuration Backups

#### Proxmox Node Configuration
**Frequency:** Daily (before any changes)
**Location:** `/var/lib/pve-backup/`

```bash
# Automated via Proxmox
# /etc/cron.daily/pve-backup

# Manual backup
tar -czf /tmp/pve-config-$(date +%Y%m%d).tar.gz \
  /etc/pve \
  /etc/network/interfaces \
  /etc/hosts \
  /etc/ceph  # If using Ceph
```

#### Service Configurations
**Frequency:** After any change
**Location:** Git repository + TrueNAS

```bash
# Backup script location
/usr/local/bin/backup-configs.sh

# Manual backup
ansible-playbook /opt/ansible/playbooks/backup-configs.yml
```

---

## Backup Operations

### Perform Manual VM Backup

#### Via WebGUI
```
1. Select VM → Backup → Backup now
2. Storage: pbs-backup (or truenas-nfs)
3. Mode: Snapshot
4. Compression: ZSTD
5. Protected: ☐ (uncheck for regular backup)
6. Click: Backup
7. Monitor: Tasks → Active (bottom panel)
```

#### Via CLI
```bash
# SSH to Proxmox node
ssh root@192.168.40.10

# Backup single VM
vzdump <VMID> --storage pbs-backup --mode snapshot --compress zstd
# Example: vzdump 101 --storage pbs-backup --mode snapshot --compress zstd

# Backup multiple VMs
vzdump 101 102 103 --storage pbs-backup --mode snapshot

# Backup all VMs
vzdump --all 1 --storage pbs-backup --mode snapshot

# Monitor backup progress
tail -f /var/log/vzdump.log
```

### Verify Backup Completion

#### Check Backup Jobs
```bash
# Via CLI
ssh root@192.168.40.10

# List recent backups
cat /var/log/vzdump.log | grep "INFO: Finished"

# Check last backup for specific VM
cat /var/log/vzdump.log | grep "VM <VMID>"

# Via WebGUI
# Select storage (pbs-backup) → Content
# View list of backups with timestamps
```

#### Verify Backup Integrity
```bash
# On Proxmox Backup Server
ssh root@192.168.40.50

# List all backups
proxmox-backup-manager list

# Verify specific backup
proxmox-backup-client verify \
  --repository backup@pbs:datastore \
  vm/101/2025-11-10T02:00:00Z

# Check verification logs
journalctl -u proxmox-backup -n 100
```

### Monitor Backup Storage Usage

#### PBS Storage Usage
```bash
# Via PBS WebGUI
# Dashboard → Datastore → Summary

# Via CLI
ssh root@192.168.40.50
proxmox-backup-manager datastore list
# Note: Used space, deduplication ratio
```

#### TrueNAS Storage Usage
```bash
# Via TrueNAS WebGUI
# Storage → Pools → backups

# Via CLI
ssh admin@192.168.40.20
zfs list -o name,used,avail,refer
```

### Cleanup Old Backups

#### Automatic Cleanup (Configured)
```bash
# PBS automatically prunes based on retention policy:
# - Keep last 7 daily
# - Keep last 4 weekly
# - Keep last 12 monthly

# View prune configuration
# PBS WebGUI → Datastore → Prune & GC → Prune Jobs
```

#### Manual Cleanup
```bash
# Via Proxmox WebGUI
# Select storage → Content
# Select old backup → Remove

# Via CLI
ssh root@192.168.40.10

# List backups for VM
ls -lh /mnt/pve/truenas-nfs/dump/

# Delete specific backup
rm /mnt/pve/truenas-nfs/dump/vzdump-qemu-101-2025-10-01T02_00_00.vma.zst

# Or use PBS client
proxmox-backup-client snapshot remove \
  vm/101/2025-10-01T02:00:00Z \
  --repository backup@pbs:datastore
```

---

## Recovery Operations

### Restore Single VM

#### Via WebGUI
```
1. Select target node (where to restore)
2. Local storage (pbs-backup or truenas-nfs) → Content
3. Find backup file
4. Click backup → Restore
5. Options:
   - VM ID: Original or new ID
   - Storage: Target storage (ceph-rbd or local-lvm)
   - Start after restore: ☐ (usually unchecked)
6. Click: Restore
7. Monitor: Tasks → Active

Expected time: 5-30 minutes depending on VM size
```

#### Via CLI
```bash
# SSH to target Proxmox node
ssh root@192.168.40.10

# List available backups
vzdump --list --storage pbs-backup

# Restore VM to original ID
qmrestore pbs-backup:backup/vm/101/2025-11-10T02:00:00Z 101 --storage ceph-rbd

# Restore to different ID (clone)
qmrestore pbs-backup:backup/vm/101/2025-11-10T02:00:00Z 201 --storage ceph-rbd

# Start restored VM
qm start 101

# Verify VM functionality
qm status 101
qm guest cmd 101 ping -- google.com
```

### Restore from TrueNAS NFS Backup

```bash
# Mount TrueNAS NFS if not already mounted
mount -t nfs 192.168.40.20:/mnt/backups /mnt/truenas-backups

# List backups
ls -lh /mnt/truenas-backups/proxmox/weekly/

# Restore
qmrestore /mnt/truenas-backups/proxmox/weekly/vzdump-qemu-101-2025-11-03.vma.zst 101 --storage local-lvm
```

### Restore Individual VM Disks

**Use Case:** Recover specific files or disk without full VM restore

```bash
# Extract VM config
vzdump --extract --storage pbs-backup --file backup/vm/101/2025-11-10T02:00:00Z

# Mount VM disk image
modprobe nbd max_part=8
qemu-nbd --connect=/dev/nbd0 /path/to/vm-disk.qcow2
mount /dev/nbd0p1 /mnt/vm-disk

# Copy needed files
cp /mnt/vm-disk/path/to/file /recovery/

# Cleanup
umount /mnt/vm-disk
qemu-nbd --disconnect /dev/nbd0
```

### Restore VM Configuration Only

**Use Case:** Rebuild VM with same settings

```bash
# Extract config from backup
vzdump --extractconfig backup/vm/101/2025-11-10T02:00:00Z > /tmp/vm101.conf

# View configuration
cat /tmp/vm101.conf

# Create new VM with same config
qm create 101 --config /tmp/vm101.conf
# Then attach storage manually
```

---

## Disaster Recovery

### Scenario 1: Single VM Corruption

**Symptoms:** VM won't boot, filesystem errors, data corruption

**Assessment:**
```bash
# Try to start VM in recovery mode
qm start 101

# Check VM logs
journalctl -u qemu-server@101 -n 50

# If disk corruption suspected:
qemu-img check /path/to/vm-disk.img
```

**Recovery:**
```bash
# Option A: Restore from last night's backup (if recent)
qmrestore pbs-backup:backup/vm/101/2025-11-10T02:00:00Z 101 --storage ceph-rbd

# Option B: Restore from snapshot (if available and newer)
qm rollback 101 pre-update

# Option C: Mount backup and extract specific files
# See "Restore Individual VM Disks" above

# Expected RPO: 24 hours (last backup)
# Expected RTO: 30 minutes
```

### Scenario 2: Node Failure with Local Storage

**Symptoms:** Node hardware failed, VMs on local storage unavailable

**Assessment:**
```bash
# From another node, check what VMs were on failed node
# Review inventory: /opt/documentation/vm-inventory.csv

# Identify which VMs need recovery
# Priority order: P0 → P1 → P2 → P3
```

**Recovery:**
```bash
# On healthy node:
ssh root@192.168.40.11

# Restore critical VMs (P0)
qmrestore pbs-backup:backup/vm/101/2025-11-10T02:00:00Z 101 --storage ceph-rbd
qmrestore pbs-backup:backup/vm/102/2025-11-10T02:00:00Z 102 --storage ceph-rbd

# Start VMs
qm start 101
qm start 102

# Verify services
# Check FreeIPA: curl -k https://192.168.40.25
# Check Pi-hole: dig @192.168.40.35 google.com

# Restore remaining VMs based on priority

# Expected RTO: 1 hour for P0, 4 hours for all critical
```

### Scenario 3: Complete Cluster Failure

**Symptoms:** All nodes lost, complete rebuild needed

**Prerequisites:**
- Fresh Proxmox installation on new/repaired hardware
- Access to backup storage (PBS, TrueNAS)
- Network infrastructure operational

**Recovery Procedure:**

#### Phase 1: Rebuild Cluster (0-2 hours)
```bash
# 1. Install Proxmox VE on first node
# Boot from Proxmox ISO, follow installer

# 2. Configure networking to match original
vi /etc/network/interfaces
# Match original IP: 192.168.40.10

# 3. Create new cluster
pvecm create homelab-cluster

# 4. Add remaining nodes (if available)
# On nodes 2 and 3:
pvecm add 192.168.40.10

# 5. Configure storage
# Add PBS storage:
pvesm add pbs pbs-backup \
  --server 192.168.40.50 \
  --datastore datastore1 \
  --username backup@pbs

# Add TrueNAS NFS:
pvesm add nfs truenas-nfs \
  --server 192.168.40.20 \
  --export /mnt/backups \
  --content backup
```

#### Phase 2: Restore Critical Services (2-4 hours)
```bash
# Priority 1: Infrastructure services
qmrestore pbs-backup:backup/vm/101/latest 101 --storage local-lvm
qm set 101 --net0 virtio,bridge=vmbr0,tag=40
qm start 101
# Wait for boot, verify service

# Priority 2: Authentication (FreeIPA)
qmrestore pbs-backup:backup/vm/102/latest 102 --storage local-lvm
qm start 102
# Test: kinit admin

# Priority 3: DNS (Pi-hole)
qmrestore pbs-backup:backup/vm/103/latest 103 --storage local-lvm
qm start 103
# Test: dig @192.168.40.35 google.com

# Priority 4: Reverse Proxy (Nginx)
qmrestore pbs-backup:backup/vm/104/latest 104 --storage local-lvm
qm start 104
# Test: curl -k https://192.168.40.40
```

#### Phase 3: Restore Remaining Services (4-24 hours)
```bash
# Restore all remaining VMs based on priority
for vmid in 105 106 107 108; do
  qmrestore pbs-backup:backup/vm/$vmid/latest $vmid --storage local-lvm
  qm start $vmid
  sleep 60  # Wait for boot
done

# Verify all services
ansible-playbook /opt/ansible/playbooks/verify-services.yml
```

#### Phase 4: Validation (24-48 hours)
```bash
# 1. Test all critical services
/usr/local/bin/health-check.sh

# 2. Verify backups are running
cat /var/log/vzdump.log

# 3. Review and update documentation
# Note any changes or issues

# 4. Notify stakeholders
# "Disaster recovery complete, all services restored"
```

**Expected Total RTO:**
- Critical services (P0): 4 hours
- All core services (P1): 8 hours
- Full environment (P0-P2): 24 hours

**Expected RPO:** 24 hours (daily backups)

### Scenario 4: Ceph Data Loss

**Symptoms:** Ceph cluster unhealthy, data unavailable

**Assessment:**
```bash
# Check Ceph health
ceph status
ceph health detail

# Check for data loss
ceph pg dump | grep -v "active+clean"

# If PGs are "incomplete":
# Data may be permanently lost
```

**Recovery:**
```bash
# If Ceph cannot be recovered:
# 1. Accept data loss for affected VMs
# 2. Restore those VMs from backup

# Identify affected VMs
ceph pg dump | grep incomplete | awk '{print $1}' | \
  xargs -I {} ceph pg {} query | grep -o 'vm-[0-9]*-disk-[0-9]*'

# For each affected VM:
qm stop <VMID>  # Stop if running
qm destroy <VMID> --purge  # Remove broken VM

# Restore from PBS
qmrestore pbs-backup:backup/vm/<VMID>/latest <VMID> --storage local-lvm

# Start restored VM
qm start <VMID>
```

---

## Testing Procedures

### Monthly Backup Test

**Objective:** Verify backups are restorable

**Procedure:**
```bash
# 1. Select test VM (non-production)
VMID=999

# 2. Restore to test ID
qmrestore pbs-backup:backup/vm/101/latest $VMID --storage local-lvm

# 3. Start and verify
qm start $VMID
sleep 60
qm status $VMID
# Expected: "status: running"

# 4. Login and verify functionality
ssh admin@<TEST_VM_IP>
# Perform basic tests

# 5. Cleanup
qm stop $VMID
qm destroy $VMID --purge

# 6. Document results
echo "$(date): Backup test successful" >> /var/log/backup-tests.log
```

### Quarterly DR Test

**Objective:** Full disaster recovery simulation

**Procedure:**
```bash
# Use spare hardware or separate environment
# Follow "Scenario 3: Complete Cluster Failure" above
# Document:
# - Time to restore each service
# - Any issues encountered
# - Updates needed to DR plan

# Update DR plan with lessons learned
vi /opt/documentation/disaster-recovery-plan.md
```

**Last Test:** November 1, 2025
**Next Test:** February 1, 2026
**Test Results:** `/var/log/dr-tests/2025-11-01-results.txt`

### Annual Full DR Drill

**Objective:** Complete rebuild from bare metal

**Scope:**
- Rebuild entire Proxmox cluster
- Restore all VMs
- Verify all services
- Test under time pressure

**Planned Date:** Annually (next: November 1, 2026)

---

## Backup Automation

### Automated Backup Scripts

#### Daily Backup Script
**Location:** `/usr/local/bin/daily-backup.sh`

```bash
#!/bin/bash
# Daily VM Backup to PBS

LOG="/var/log/daily-backup.log"
STORAGE="pbs-backup"

echo "$(date): Starting daily backup" >> $LOG

# Backup all running VMs
vzdump --all 1 --storage $STORAGE --mode snapshot --compress zstd --quiet 1 >> $LOG 2>&1

if [ $? -eq 0 ]; then
  echo "$(date): Backup completed successfully" >> $LOG
else
  echo "$(date): Backup failed!" >> $LOG
  # Send alert (email, Slack, etc.)
  /usr/local/bin/send-alert.sh "Daily backup failed"
fi
```

#### Offsite Sync Script
**Location:** `/usr/local/bin/offsite-sync.sh`

```bash
#!/bin/bash
# Weekly offsite backup sync

SOURCE="/mnt/pve/truenas-nfs/dump/"
REMOTE="backup@remote.example.com:/backups/proxmox/"
LOG="/var/log/offsite-sync.log"

echo "$(date): Starting offsite sync" >> $LOG

# Sync last 7 days of backups
rsync -avz --delete --max-delete=10 \
  --include="*.vma.zst" \
  --include="*.log" \
  --exclude="*" \
  $SOURCE $REMOTE >> $LOG 2>&1

if [ $? -eq 0 ]; then
  echo "$(date): Sync completed" >> $LOG
else
  echo "$(date): Sync failed!" >> $LOG
  /usr/local/bin/send-alert.sh "Offsite sync failed"
fi
```

### Backup Monitoring

#### Check Backup Status
```bash
# Via Ansible playbook
ansible-playbook /opt/ansible/playbooks/check-backups.yml

# Manual check
/usr/local/bin/backup-verify.sh

# Expected output:
# ✓ All VMs backed up in last 24 hours
# ✓ PBS storage usage: 45% (healthy)
# ✓ TrueNAS storage usage: 62% (healthy)
# ✓ Last offsite sync: 2 days ago (healthy)
```

#### Backup Alerts

```bash
# Configure alerts for:
# - Backup job failure
# - Storage >90% full
# - No backup in 48 hours
# - Restore verification failed

# Alert script: /usr/local/bin/send-alert.sh
# Integration: Email, Slack, PagerDuty
```

---

## Best Practices

### Backup Best Practices
1. **Automate Everything** - No manual backups for production
2. **Test Regularly** - Monthly restore tests minimum
3. **Multiple Copies** - Follow 3-2-1 rule strictly
4. **Monitor Closely** - Alert on any backup failure
5. **Document Changes** - Update runbook when process changes

### Recovery Best Practices
1. **Know Your RPO/RTO** - Understand acceptable data loss
2. **Prioritize** - Restore critical services first
3. **Verify** - Always test restored VM before production use
4. **Document** - Record what was restored and when
5. **Post-Mortem** - Learn from every recovery event

### Storage Management
1. **Monitor Usage** - Alert at 80% full
2. **Prune Regularly** - Remove old backups per policy
3. **Verify Integrity** - Regular scrubs and checks
4. **Plan Capacity** - Grow storage proactively

---

## Useful Commands Reference

```bash
# Backups
vzdump <VMID> --storage <STORAGE> --mode snapshot  # Backup VM
vzdump --all 1 --storage <STORAGE>                 # Backup all VMs
tail -f /var/log/vzdump.log                        # Monitor backup

# Restores
qmrestore <BACKUP> <VMID> --storage <STORAGE>      # Restore VM
vzdump --list --storage <STORAGE>                  # List backups

# PBS Commands
proxmox-backup-manager list                        # List backups
proxmox-backup-client verify                       # Verify backup
proxmox-backup-manager datastore list              # Storage usage

# Monitoring
cat /var/log/vzdump.log | grep ERROR               # Check errors
df -h /mnt/pve/*                                   # Storage usage
pvesm status                                       # All storage status
```

---

## Recovery Decision Tree

```
Is the problem with a single VM or entire cluster?
├─ Single VM
│   ├─ VM won't start?
│   │   └─ Restore from last backup (RTO: 30 min)
│   ├─ VM corrupted but running?
│   │   └─ Stop VM, restore from backup (RTO: 30 min)
│   └─ Need specific files only?
│       └─ Mount backup and extract files (RTO: 15 min)
│
└─ Entire Cluster
    ├─ Single node failed?
    │   ├─ Node has VMs on shared storage (Ceph)?
    │   │   └─ HA will auto-migrate (RTO: 5 min)
    │   └─ Node has VMs on local storage?
    │       └─ Restore VMs on other node (RTO: 1-4 hours)
    │
    └─ All nodes failed?
        └─ Full disaster recovery (RTO: 4-24 hours)
            1. Rebuild cluster infrastructure
            2. Restore critical VMs (P0)
            3. Restore core VMs (P1)
            4. Restore remaining VMs (P2-P3)
```

---

**End of Runbook**

*Last Reviewed: November 10, 2025*
*Next Review: February 10, 2026 (Quarterly)*
*Last DR Test: November 1, 2025*
*Next DR Test: February 1, 2026*
