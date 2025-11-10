---
title: Runbook - Disk Space Low
description: Response procedure when disk usage exceeds threshold
published: true
date: 2025-11-07
tags: [runbook, infrastructure, alert, warning]
---

# Runbook: Disk Space Low

**Alert Name**: `DiskSpaceLow`
**Severity**: ⚠️ Warning (>80%), 🔴 Critical (>90%)
**Response Time**: 1 hour (Warning), 15 minutes (Critical)
**Prometheus Query**: `(node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 < 15`

## Symptoms

- Prometheus alert `DiskSpaceLow` or `DiskSpaceCritical` firing
- Application logs showing "No space left on device"
- Write operations failing
- Services unable to create temporary files

## Impact Assessment

**Warning (80-90%)**:
- No immediate impact
- Time to investigate and clean up
- Plan for capacity expansion

**Critical (>90%)**:
- Applications may fail to write data
- Logs may stop rotating
- Databases may enter read-only mode
- Risk of service outages

## Immediate Actions

### 1. Identify the Affected Host and Filesystem

```bash
# From Prometheus alert
instance: "192.168.1.21:9100"
mountpoint: "/var"

# Or check in Grafana
# Dashboard: Infrastructure Overview
# Panel: Disk Usage by Host
```

### 2. SSH to Host and Verify

```bash
ssh user@<host_ip>

# Check all filesystems
df -h

# Expected output:
# Filesystem      Size  Used Avail Use% Mounted on
# /dev/sda1        50G   45G    3G  94% /
# /dev/sdb1       100G   75G   20G  80% /var

# Check inode usage (can also fill up)
df -i
```

## Investigation Steps

### 3. Identify What's Consuming Space

```bash
# Find largest directories
du -h / | sort -rh | head -20

# Or use ncdu (if installed)
ncdu /

# Check specific common locations
du -sh /var/log/*
du -sh /var/lib/docker/*
du -sh /tmp/*
du -sh /home/*
```

### 4. Check for Common Culprits

**Logs**:
```bash
# Large log files
find /var/log -type f -size +100M -exec ls -lh {} \;

# Unrotated logs
ls -lh /var/log/*.log

# Check systemd journal size
journalctl --disk-usage
```

**Docker/Containers**:
```bash
# Docker disk usage
docker system df

# Dangling images
docker images -f "dangling=true"

# Stopped containers
docker ps -a --filter "status=exited"

# Unused volumes
docker volume ls -qf "dangling=true"
```

**Backups**:
```bash
# Old backup files
find /var/backups -type f -mtime +30

# Large backup files
find /var/backups -type f -size +1G -exec ls -lh {} \;
```

**Temp Files**:
```bash
# Old temp files
find /tmp -type f -mtime +7

# Large temp files
find /tmp -type f -size +100M
```

## Resolution Steps

### Option A: Clean Up Logs (Safest)

```bash
# Rotate logs manually
logrotate -f /etc/logrotate.conf

# Clean old journal logs (keep 7 days)
journalctl --vacuum-time=7d

# Remove old compressed logs
find /var/log -name "*.gz" -mtime +30 -delete
find /var/log -name "*.1" -mtime +7 -delete

# Truncate large active logs (if safe)
: > /var/log/large-application.log
# or
truncate -s 0 /var/log/large-application.log
```

### Option B: Clean Up Docker/Containers

```bash
# Clean up Docker system
docker system prune -a -f

# Remove specific dangling images
docker rmi $(docker images -f "dangling=true" -q)

# Remove stopped containers
docker rm $(docker ps -a -f "status=exited" -q)

# Remove unused volumes
docker volume rm $(docker volume ls -qf "dangling=true")

# Remove build cache
docker builder prune -a -f
```

### Option C: Clean Up Old Backups

```bash
# List old backups
find /var/backups -type f -mtime +30

# Remove old backups (be careful!)
find /var/backups -name "backup-*.tar.gz" -mtime +30 -delete

# Verify backup retention policy
# Expected: 7 daily, 4 weekly, 3 monthly
```

### Option D: Move Data to Larger Filesystem

```bash
# Identify moveable data
du -sh /var/lib/application/*

# Create new location
mkdir -p /mnt/data/application

# Move data (example: PostgreSQL)
systemctl stop postgresql
rsync -av /var/lib/postgresql/ /mnt/data/postgresql/
mv /var/lib/postgresql /var/lib/postgresql.old
ln -s /mnt/data/postgresql /var/lib/postgresql
systemctl start postgresql

# Verify application works, then remove old
rm -rf /var/lib/postgresql.old
```

### Option E: Expand Filesystem (If Virtual)

**For LVM**:
```bash
# Check volume group
vgs

# Extend logical volume
lvextend -L +10G /dev/vg0/root

# Resize filesystem
resize2fs /dev/vg0/root  # For ext4
xfs_growfs /               # For XFS
```

**For Proxmox VM**:
```bash
# On Proxmox host
qm resize <vmid> scsi0 +10G

# On VM, then extend as above
```

## Verification

### 5. Confirm Space Available

```bash
# Check filesystem
df -h /

# Should show <80% usage

# Check alert in Prometheus
# Query: (node_filesystem_avail_bytes{instance="<host>",mountpoint="/"} / node_filesystem_size_bytes) * 100
# Should be > 20%

# Alert should auto-resolve
```

### 6. Verify Services

```bash
# Check critical services
systemctl status application
systemctl status database

# Test write operations
echo "test" > /tmp/write-test.txt
rm /tmp/write-test.txt

# Check application logs
tail -f /var/log/application.log
```

## Post-Incident Actions

### 7. Document What Was Cleaned

```markdown
## Disk Cleanup - <hostname> - 2025-11-07

**Space Before**: 94% (3GB free)
**Space After**: 72% (15GB free)
**Space Recovered**: 12GB

**Actions Taken**:
- Cleaned Docker images: 5GB recovered
- Rotated old logs: 4GB recovered
- Removed old backups >30 days: 3GB recovered

**Files Removed**:
- /var/lib/docker/overlay2/* (dangling layers)
- /var/log/*.gz (30+ days old)
- /var/backups/backup-2025-09-*.tar.gz
```

### 8. Implement Monitoring Improvements

```bash
# Add filesystem growth rate alert
# /etc/prometheus/alerts/infrastructure_alerts.yml

- alert: DiskFillingUp
  expr: predict_linear(node_filesystem_avail_bytes[6h], 24*3600) < 0
  for: 1h
  labels:
    severity: warning
  annotations:
    summary: "Disk will fill in 24 hours on {{ $labels.instance }}"
    description: "Filesystem {{ $labels.mountpoint }} will run out of space in 24h"
```

### 9. Implement Prevention

**Automate Log Rotation**:
```bash
# /etc/logrotate.d/application
/var/log/application/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 app app
    sharedscripts
    postrotate
        systemctl reload application
    endscript
}
```

**Automate Docker Cleanup**:
```bash
# Add cron job
crontab -e

# Run weekly cleanup
0 2 * * 0 docker system prune -a -f --volumes
```

**Set Up Backup Retention**:
```bash
# /usr/local/bin/cleanup-old-backups.sh
#!/bin/bash
find /var/backups -name "daily-*.tar.gz" -mtime +7 -delete
find /var/backups -name "weekly-*.tar.gz" -mtime +28 -delete
find /var/backups -name "monthly-*.tar.gz" -mtime +90 -delete

# Add to cron
0 3 * * * /usr/local/bin/cleanup-old-backups.sh
```

## Escalation Path

Escalate if:
- **Cannot free up enough space**: Need additional storage
- **Critical database affected**: Risk of data loss, engage DBA team
- **Filesystem corruption suspected**: Engage system administrator
- **Application failures persist**: Engage application team

## Related Documentation

- [High Disk I/O Runbook](/runbooks/infrastructure/high-disk-io)
- [Backup Job Failure Runbook](/runbooks/database/backup-failure)
- [Storage Expansion Playbook](/playbooks/storage-expansion)
- [Backup & Recovery Playbook](/playbooks/backup-recovery)

## Common Causes and Solutions

| Cause | Indicator | Solution |
|-------|-----------|----------|
| **Runaway logs** | `/var/log` growing rapidly | Fix application logging, add rotation |
| **Docker images** | `docker system df` shows high usage | Regular `docker system prune` |
| **Database growth** | `/var/lib/postgresql` large | Archive old data, vacuum |
| **Failed backups** | Partial backup files accumulate | Fix backup job, clean old files |
| **Core dumps** | Large files in `/var/crash` | Investigate crashes, remove dumps |
| **Package cache** | `/var/cache/apt` large | `apt-get clean` |

## Prevention Checklist

- [ ] Log rotation configured for all applications
- [ ] Docker cleanup cron job in place
- [ ] Backup retention policy automated
- [ ] Monitoring alert for disk filling rate
- [ ] Regular review of disk usage trends
- [ ] Documentation of data growth expectations
- [ ] Capacity planning for next 6 months

---

**Last Updated**: November 7, 2025
**Runbook Owner**: Sam Jackson
**Review Frequency**: Quarterly
