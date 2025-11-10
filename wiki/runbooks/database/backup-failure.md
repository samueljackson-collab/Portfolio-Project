---
title: Runbook - Backup Job Failure
description: Response procedure when backup jobs fail
published: true
date: 2025-11-07
tags: [runbook, database, backup, alert, critical]
---

# Runbook: Backup Job Failure

**Alert Name**: `BackupJobFailed`
**Severity**: 🔴 Critical
**Response Time**: 15 minutes
**Prometheus Query**: `proxmox_backup_job_last_status != 0`

## Symptoms

- Prometheus alert `BackupJobFailed` firing
- Proxmox Backup Server (PBS) shows failed job
- Email notification of backup failure
- Missing backup in expected retention window

## Impact Assessment

**Immediate Impact**:
- No immediate service impact
- Gap in backup coverage
- Risk of data loss if system fails before next backup

**Risk Level**:
- **Single failure**: Low risk if previous backups exist
- **Multiple failures**: High risk - backup coverage gap widening
- **Long-term failure**: Critical risk - exceeding RTO/RPO

**Recovery Point Objective (RPO)**: 24 hours (nightly backups)
**Recovery Time Objective (RTO)**: 4 hours

## Immediate Actions

### 1. Verify the Failure

**Check PBS Web UI**:
```
Navigate to: https://192.168.1.15:8007
Dashboard → Backup Jobs
Look for: Red X or "FAILED" status
```

**Check Prometheus**:
```promql
# Query backup job status
proxmox_backup_job_last_status{job="nightly-vm-backup"}

# 0 = OK, 1 = WARNING, 2 = ERROR

# Check last successful backup time
time() - proxmox_backup_job_last_run_endtime{job="nightly-vm-backup"}
# Should be < 86400 (24 hours)
```

**Check Alert Details**:
- Which VMs/containers failed?
- Error message in alert annotation
- When did it last succeed?

### 2. Identify the Failed Backup Job

```bash
# SSH to PBS host
ssh root@192.168.1.15

# Check recent backup logs
journalctl -u proxmox-backup --since "24 hours ago" | grep -i error

# Check specific job logs
cat /var/log/proxmox-backup/tasks/*.log | tail -100

# List recent tasks
proxmox-backup-manager task list --limit 20
```

## Investigation Steps

### 3. Determine Failure Reason

**Common Error Messages**:

| Error Message | Cause | Quick Fix |
|---------------|-------|-----------|
| `connection timeout` | Network issue | Check network, firewall |
| `no space left on device` | PBS datastore full | Free up space, prune old backups |
| `VM not running` | VM powered off | Normal for stopped VMs |
| `snapshot failed` | QEMU issues | Check VM status |
| `permission denied` | Authentication failure | Verify PBS credentials |
| `backup canceled` | Manual cancellation | Re-run backup |

### 4. Check PBS Datastore Space

```bash
# On PBS host
df -h /mnt/datastore

# Check datastore usage in Web UI
# Storage → Datastores → Usage

# Should have at least 20% free
```

If low on space:
```bash
# List backup sizes
proxmox-backup-manager datastore content <datastore> --ns root

# Check retention policy
cat /etc/proxmox-backup/datastore.cfg

# Prune old backups (manual)
proxmox-backup-manager prune <datastore> --keep-last 7
```

### 5. Check Network Connectivity

```bash
# From Proxmox host to PBS
ping -c 4 192.168.1.15

# Check if PBS API is responding
curl -k https://192.168.1.15:8007/api2/json/version

# Check firewall rules (on pfSense)
# Status → System Logs → Firewall
# Look for blocks between Proxmox (192.168.1.x) and PBS (192.168.1.15)
```

### 6. Check VM/Container Status

```bash
# On Proxmox host
qm list  # For VMs
pct list # For containers

# Check specific VM that failed
qm status <vmid>

# Check VM config
qm config <vmid> | grep -i backup

# Look for: backup: 0 (means backup disabled)
```

### 7. Check PBS Authentication

```bash
# On Proxmox host
# Check PBS configuration
cat /etc/pve/storage.cfg | grep -A 10 "pbs:"

# Verify credentials
pvesm status --storage <pbs-storage-name>

# Test connection
proxmox-backup-client login --repository <user>@<realm>!<token-name>@192.168.1.15:<datastore>
```

## Resolution Steps

### Option A: Retry Backup Job

**Via PBS Web UI**:
```
Dashboard → Backup Jobs → [Select Job] → Run Now
```

**Via Command Line**:
```bash
# On Proxmox host
vzdump <vmid> --storage <pbs-storage-name> --mode snapshot
```

**Watch Progress**:
```bash
# Monitor backup job
tail -f /var/log/pve/tasks/*.log

# Or watch in PBS UI
# Dashboard → Tasks
```

### Option B: Fix Datastore Space

```bash
# On PBS host

# Prune old backups according to retention policy
proxmox-backup-manager garbage-collect <datastore>

# Manual prune (keeps last 7, last 4 weeks, last 3 months)
proxmox-backup-manager prune <datastore> \
    --keep-last 7 \
    --keep-weekly 4 \
    --keep-monthly 3

# Verify space freed
df -h /mnt/datastore
```

### Option C: Fix Network/Firewall Issues

```bash
# Check pfSense firewall
# Firewall → Rules → VLAN 40 (Servers)
# Ensure: Pass rule for 192.168.1.x → 192.168.1.15:8007

# Test connectivity
telnet 192.168.1.15 8007

# Check PBS service
systemctl status proxmox-backup-proxy
systemctl status proxmox-backup
```

### Option D: Fix VM Configuration Issues

```bash
# On Proxmox host

# Enable backup for VM (if disabled)
qm set <vmid> --backup 1

# Change backup mode (if snapshot fails)
# Edit /etc/pve/vzdump.cron
# Change: mode: snapshot
# To: mode: suspend

# Restart qemu-guest-agent (for better snapshots)
qm guest cmd <vmid> guest-ping
```

### Option E: Re-configure PBS Storage

```bash
# On Proxmox host

# Remove old PBS configuration
pvesm remove <pbs-storage-name>

# Re-add PBS storage
pvesm add pbs <pbs-storage-name> \
    --server 192.168.1.15 \
    --datastore <datastore-name> \
    --username <user>@<realm>!<token-name> \
    --password <token-secret>

# Verify
pvesm status --storage <pbs-storage-name>
```

## Verification

### 8. Confirm Backup Succeeded

**Check PBS UI**:
```
Dashboard → Backup Jobs → [Job Name]
Status: Should show green checkmark
Last Run: Should show recent timestamp
```

**Check PBS CLI**:
```bash
# On PBS host
proxmox-backup-manager task list --limit 5

# Should show recent successful backup
```

**Verify Backup Files**:
```bash
# On PBS host
ls -lh /mnt/datastore/<namespace>/<vm-id>/

# Should see recent .fidx files
# Check timestamp and size
```

### 9. Verify Prometheus Alert Resolved

```promql
# Query in Prometheus
proxmox_backup_job_last_status{job="nightly-vm-backup"}
# Should return: 0

# Alert should auto-resolve in Alertmanager
# http://192.168.1.11:9093
```

### 10. Test Backup Integrity

```bash
# On PBS host

# Verify backup integrity
proxmox-backup-client verify \
    --repository <user>@<realm>!<token>@localhost:<datastore> \
    <backup-group> <backup-time>

# Expected: "verify successful"
```

## Post-Incident Actions

### 11. Document the Incident

```markdown
## Backup Failure Incident - 2025-11-07

**Affected VMs**: wiki-vm (ID: 100), homeassistant (ID: 101)
**Failure Duration**: 2025-11-07 02:00 - 2025-11-07 03:15 (1h 15m)
**Root Cause**: PBS datastore 98% full, backup job failed with "no space left"

**Timeline**:
- 02:00: Nightly backup job started
- 02:15: Job failed with disk space error
- 02:30: Alert fired (BackupJobFailed)
- 02:45: Investigation started
- 03:00: Old backups pruned, 45GB freed
- 03:10: Backup job re-run successfully
- 03:15: Verified backup integrity

**Prevention**:
- Added alert for PBS datastore >85%
- Automated weekly garbage collection
- Updated retention policy (7/4/3 → 7/4/2)
- Scheduled monthly backup integrity tests
```

### 12. Implement Prevention Measures

**Add Datastore Space Alert**:
```yaml
# /etc/prometheus/alerts/backup_alerts.yml

- alert: PBSDatastoreFull
  expr: (pbs_datastore_available / pbs_datastore_total) < 0.15
  for: 30m
  labels:
    severity: warning
  annotations:
    summary: "PBS datastore {{ $labels.datastore }} running low on space"
    description: "Only {{ $value | humanizePercentage }} space remaining"
    runbook: https://wiki.homelab.local/runbooks/database/backup-failure
```

**Automate Garbage Collection**:
```bash
# On PBS host
# /etc/cron.weekly/pbs-gc

#!/bin/bash
/usr/bin/proxmox-backup-manager garbage-collect main-datastore
/usr/bin/proxmox-backup-manager prune main-datastore --keep-last 7 --keep-weekly 4 --keep-monthly 2

# Make executable
chmod +x /etc/cron.weekly/pbs-gc
```

**Schedule Backup Verification**:
```bash
# Monthly cron job for backup verification
# /etc/cron.monthly/verify-backups

#!/bin/bash
# Verify last week's backups
proxmox-backup-client verify --repository root@pam!monitoring@localhost:main-datastore vm/100/$(date -d '7 days ago' +%Y-%m-%d)
```

### 13. Update Documentation

- Update [Backup & Recovery Playbook](/playbooks/backup-recovery)
- Add to [PBS Operations Guide](/projects/sde-devops/prj-sde-002/operations#backup-operations)
- Update retention policy documentation

## Escalation Path

Escalate if:
- **Cannot free up space**: Need additional storage hardware
- **Backup consistently failing**: PBS or storage hardware issue
- **Data corruption detected**: Engage data recovery specialist
- **Multiple days without backups**: Risk exceeds RPO, notify management

**Escalation Contact**:
- Storage Issues: Storage team / vendor support
- PBS Issues: Proxmox support (if subscription active)
- Data Recovery: Data recovery specialist

## Related Documentation

- [Disk Space Low Runbook](/runbooks/infrastructure/disk-space-low)
- [Backup & Recovery Playbook](/playbooks/backup-recovery)
- [Disaster Recovery Playbook](/playbooks/disaster-recovery)
- [PRJ-SDE-002: Observability & Backups](/projects/sde-devops/prj-sde-002/overview)
- [PBS Configuration Guide](/projects/sde-devops/prj-sde-002/pbs-configuration)

## Backup Retention Policy

| Backup Type | Retention | Purpose |
|-------------|-----------|---------|
| **Daily** | 7 days | Short-term recovery |
| **Weekly** | 4 weeks | Medium-term recovery |
| **Monthly** | 2-3 months | Long-term compliance |

**Storage Calculation**:
- Average VM size: 20GB
- Daily incremental: 2GB
- Weekly full: 20GB
- Total for 7/4/2 policy: ~170GB per VM

## Prevention Checklist

- [ ] PBS datastore monitoring alert configured
- [ ] Automated garbage collection scheduled
- [ ] Backup verification tests scheduled
- [ ] Retention policy documented and enforced
- [ ] Network connectivity monitored
- [ ] PBS credentials tested and documented
- [ ] Regular backup restore drills conducted

---

**Last Updated**: November 7, 2025
**Runbook Owner**: Sam Jackson
**Review Frequency**: Quarterly
**Next Review**: February 2026
