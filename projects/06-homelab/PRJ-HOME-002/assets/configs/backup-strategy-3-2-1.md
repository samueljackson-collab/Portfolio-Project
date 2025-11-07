# 3-2-1 Backup Strategy Implementation

## Backup Strategy Overview

The homelab implements the industry-standard 3-2-1 backup strategy:
- **3 copies** of data
- **2 different** media types
- **1 offsite** copy

### Visual Representation
```
Primary Data (TrueNAS ZFS)
    ├── Copy 1: Local (ZFS snapshots) - Medium: SSD/HDD
    ├── Copy 2: On-site (Proxmox Backup Server) - Medium: HDD
    └── Copy 3: Offsite (Backblaze B2) - Medium: Cloud Storage
```

## Implementation Details

### Copy 1: Primary Data Protection (TrueNAS)

**Technology:** ZFS with automated snapshots  
**Storage Medium:** SSD + HDD mirror pool  
**Location:** On-site (rack server)

**ZFS Pool Configuration:**
```bash
Pool: tank
Type: mirror (2-disk redundancy)
Capacity: 4TB usable
Compression: lz4
Deduplication: Disabled (performance)
```

**Snapshot Schedule:**
| Frequency | Retention | Purpose |
|-----------|-----------|---------|
| Hourly | 24 hours | Rapid recovery from accidental deletion |
| Daily | 7 days | Daily reversion point |
| Weekly | 4 weeks | Weekly archive |
| Monthly | 12 months | Long-term data retention |

**Snapshot Storage Overhead:**
- Average: 5-10% of dataset size
- Monitored via Grafana dashboard
- Alert at 80% pool utilization

---

### Copy 2: Local Backup Server (Proxmox Backup Server)

**Technology:** Proxmox Backup Server (PBS)  
**Storage Medium:** Dedicated HDD array  
**Location:** On-site (separate physical server)  
**Purpose:** VM/Container backups + file-level backups

**Backup Jobs:**

#### Virtual Machines
```yaml
Job: VM Full Backups
Schedule: Daily at 2:00 AM
Retention:
  - Keep last 7 daily backups
  - Keep last 4 weekly backups
  - Keep last 12 monthly backups
Compression: ZSTD
Encryption: AES-256
Notification: Email on failure
```

#### LXC Containers
```yaml
Job: Container Backups
Schedule: Daily at 3:00 AM
Retention:
  - Keep last 7 daily backups
  - Keep last 4 weekly backups
Mode: Snapshot (minimal downtime)
Compression: ZSTD
```

#### Critical Data (File-level)
```yaml
Job: File-level Backups
Source: /data/documents, /data/photos, /data/config
Schedule: Hourly incremental, Daily full
Retention:
  - Keep last 24 hourly backups
  - Keep last 30 daily backups
Deduplication: Enabled
Verification: Automatic checksum validation
```

**PBS Storage Configuration:**
```bash
Datastore: backup-pool
Type: ZFS
Capacity: 8TB usable
Encryption: Yes (at rest)
Deduplication: Yes (content-defined chunking)
Compression: ZSTD level 3
```

**Verification Procedures:**
- **Automatic:** Checksum verification on every backup
- **Manual:** Monthly test restore of random VM
- **Quarterly:** Full DR drill (restore entire environment)

---

### Copy 3: Offsite Backup (Cloud Storage)

**Provider:** Backblaze B2  
**Storage Medium:** Cloud object storage  
**Location:** Offsite (multi-region)  
**Purpose:** Disaster recovery (fire, theft, catastrophic failure)

**Backup Strategy:**
```yaml
Tool: Restic + rclone
Encryption: Client-side AES-256 before upload
Retention:
  - Keep all backups from last 30 days
  - Keep weekly backups for 1 year
  - Keep monthly backups for 7 years
Schedule:
  - Critical data: Daily at 4:00 AM
  - Photos: Weekly on Sunday at 1:00 AM
  - VM configs: After every change
Bandwidth Limit: 50 Mbps (to avoid ISP throttling)
```

**Data Classification for Offsite Backup:**
| Data Type | Backup Frequency | Retention | Estimated Size |
|-----------|------------------|-----------|----------------|
| Critical Documents | Daily | 7 years | 50 GB |
| Photos/Videos | Weekly | Permanent | 500 GB |
| VM Configurations | On change | 1 year | 10 GB |
| Code Repositories | Daily | 1 year | 20 GB |
| Wiki Content | Daily | 1 year | 5 GB |

**Cost Estimation:**
- Storage: ~600 GB × $0.005/GB/month = $3/month
- Download (DR scenario): ~600 GB × $0.01/GB = $6 one-time
- **Total Monthly Cost:** ~$3-5/month

**Security:**
- Encryption: Client-side before upload (zero-knowledge)
- Access: IAM-restricted application key
- Monitoring: Alert on failed uploads

---

## Backup Verification & Testing

### Automated Verification

**Daily (Automated):**
```bash
#!/bin/bash
# Daily backup verification script

# Check PBS backup completion
pbs-check() {
    latest_backup=$(pbs list backups --output-format json | jq -r '.[0].status')
    if [ "$latest_backup" != "complete" ]; then
        alert "PBS backup failed or incomplete"
    fi
}

# Check ZFS snapshot creation
zfs-check() {
    latest_snap=$(zfs list -t snapshot -o name -s creation | tail -1)
    snap_age=$(zfs get -H -o value creation "$latest_snap")
    if [ "$snap_age" -gt 86400 ]; then
        alert "ZFS snapshot older than 24 hours"
    fi
}

# Check offsite backup sync
b2-check() {
    last_sync=$(rclone lsf b2:homelab-backup/ --max-age 24h | wc -l)
    if [ "$last_sync" -eq 0 ]; then
        alert "No offsite backup in last 24 hours"
    fi
}

pbs-check
zfs-check
b2-check
```

### Manual Testing Schedule

**Monthly (Manual Restore Test):**
1. Select random VM from last week's backup
2. Restore to test VLAN
3. Verify VM boots and services start
4. Document restore time (RTO target: 30 minutes)
5. Delete test restoration

**Quarterly (Full DR Drill):**
1. Simulate total site loss
2. Restore critical VMs from Backblaze B2
3. Restore file shares from PBS
4. Verify all services operational
5. Document total recovery time
6. Identify gaps and update documentation

---

## Recovery Time/Point Objectives

| Data Type | RPO (Max Data Loss) | RTO (Max Downtime) | Recovery Source |
|-----------|---------------------|---------------------|-----------------|
| Critical VMs | 24 hours | 4 hours | PBS → TrueNAS |
| File Shares | 1 hour | 2 hours | ZFS Snapshot |
| Databases | 24 hours | 4 hours | PBS + transaction logs |
| Photos | 7 days | 24 hours | Backblaze B2 |
| Configuration | 1 day | 1 hour | Git + PBS |

---

## Disaster Recovery Scenarios

### Scenario 1: Accidental File Deletion
**Recovery Steps:**
1. Access TrueNAS web UI
2. Browse ZFS snapshots
3. Locate file in most recent hourly snapshot
4. Restore file to original location
**Expected RTO:** < 15 minutes

### Scenario 2: VM Corruption
**Recovery Steps:**
1. Access Proxmox Backup Server
2. Select most recent daily backup
3. Restore VM to Proxmox host
4. Start VM and verify services
**Expected RTO:** 30-60 minutes

### Scenario 3: Ransomware Attack
**Recovery Steps:**
1. Isolate infected systems immediately
2. Verify PBS backups are not encrypted (immutable snapshots)
3. Restore VMs from PBS to clean Proxmox host
4. Restore file shares from ZFS snapshots (pre-infection)
5. Scan restored data before bringing online
**Expected RTO:** 4-8 hours

### Scenario 4: Total Site Loss (Fire/Theft)
**Recovery Steps:**
1. Acquire replacement hardware
2. Install Proxmox from ISO
3. Download critical data from Backblaze B2
4. Restore VMs and configurations
5. Bring services online incrementally
**Expected RTO:** 24-48 hours

---

## Backup Monitoring & Alerting

### Prometheus Metrics
```yaml
backup_job_status{job="pbs-daily-vm"} 1    # 1 = success, 0 = failure
backup_job_duration_seconds{job="pbs-daily-vm"} 1234
backup_size_bytes{job="pbs-daily-vm"} 50000000000
zfs_snapshot_age_seconds{pool="tank"} 3600
b2_last_sync_timestamp 1699564800
```

### Alert Rules
```yaml
- alert: BackupFailed
  expr: backup_job_status == 0
  for: 1h
  annotations:
    summary: "Backup job {{ $labels.job }} failed"
    
- alert: OldZFSSnapshot
  expr: zfs_snapshot_age_seconds > 86400
  for: 1h
  annotations:
    summary: "ZFS snapshot older than 24 hours"
    
- alert: OffsiteBackupStale
  expr: time() - b2_last_sync_timestamp > 172800
  annotations:
    summary: "Offsite backup not updated in 48 hours"
```

---

## Backup Security

### Encryption
- **At Rest:** All PBS backups encrypted with AES-256
- **In Transit:** TLS 1.3 for all backup transfers
- **Offsite:** Client-side encryption before cloud upload

### Access Control
- **PBS:** RBAC with dedicated backup user
- **TrueNAS:** SSH key-based authentication only
- **Backblaze:** Application-specific keys with minimal permissions

### Key Management
- Backup encryption keys stored in password manager
- Tested key recovery process quarterly
- Offsite key backup in safe deposit box

---

## Backup Cost Analysis

| Component | Monthly Cost | Annual Cost |
|-----------|--------------|-------------|
| TrueNAS (owned hardware) | $10 (power) | $120 |
| PBS (owned hardware) | $5 (power) | $60 |
| Backblaze B2 (600 GB) | $3 | $36 |
| **Total** | **$18/month** | **$216/year** |

**Cost per GB:** $0.03/month (~industry avg: $0.02-0.10)

**ROI of Backups:**
- Cost of data loss: Priceless (family photos, documents)
- Cost of downtime: ~$50/hour (lost productivity)
- Cost of backup: $18/month
- **Conclusion:** Backup investment is justified

---

## Maintenance & Operations

### Daily Tasks (Automated)
- [ ] Backup jobs execute
- [ ] Verification scripts run
- [ ] Alerts sent on failures

### Weekly Tasks (Automated)
- [ ] Offsite sync to Backblaze B2
- [ ] ZFS scrub (data integrity check)
- [ ] Cleanup old snapshots per retention policy

### Monthly Tasks (Manual)
- [ ] Review backup success rate (target: 100%)
- [ ] Test random VM restore
- [ ] Review storage capacity (alert at 80%)
- [ ] Update this documentation if changes made

### Quarterly Tasks (Manual)
- [ ] Full DR drill
- [ ] Review and update retention policies
- [ ] Verify encryption key accessibility
- [ ] Audit backup security (access logs)

---

## Continuous Improvement

### Metrics to Track
1. **Backup Success Rate:** Target 100% (alert if < 98%)
2. **Recovery Time Actual vs. Target:** Quarterly DR drill results
3. **Storage Growth Rate:** Plan capacity upgrades
4. **Cost Efficiency:** $/GB trend over time

### Lessons Learned Log

| Date | Incident | Lesson | Action Taken |
|------|----------|--------|--------------|
| 2024-01 | Backup failed due to full disk | Monitor disk space proactively | Added Grafana alert at 80% |
| 2024-03 | Slow restore from B2 | Download speed limited by ISP | Documented expected RTO |
| 2024-06 | PBS encryption key not documented | Key management process unclear | Created key recovery runbook |

---

**Document Version:** 1.0  
**Last Updated:** November 2024  
**Next Review:** February 2025
