# Disaster Recovery Runbook

**Purpose:** Procedures for recovering from catastrophic infrastructure failures
**RTO Target:** ≤ 4 hours
**RPO Target:** ≤ 24 hours
**Last Tested:** TBD

---

## Emergency Contacts

| Role | Name | Contact | Availability |
|------|------|---------|--------------|
| Primary Admin | Samuel Jackson | [Redacted] | 24/7 |
| Sponsor | Andrew Vongsady | [Redacted] | Business hours |
| ISP Support | Spectrum | 1-855-707-7328 | 24/7 |
| Hardware Vendor | HP Support | 1-800-474-6836 | Business hours |

---

## Disaster Scenarios

### Scenario 1: Complete Proxmox Host Failure

**Symptoms:**
- Proxmox host unresponsive
- Physical hardware failure (PSU, motherboard, disk)
- Cannot boot or access system

**Recovery Steps:**

#### Phase 1: Assessment (15 minutes)

1. **Verify failure is hardware-related:**
   ```bash
   # Attempt to ping host
   ping -c 5 192.168.10.10

   # Check UniFi for network connectivity
   # Access: https://unifi.homelab.local
   # Navigate: Devices > Proxmox Host
   ```

2. **Check for console access:**
   - Physical access to server
   - IPMI/iLO console (if available)
   - Serial console connection

3. **Document failure indicators:**
   - POST codes / beep patterns
   - LED status indicators
   - Console error messages

#### Phase 2: Backup Hardware Preparation (30 minutes)

**Option A: Spare Hardware Available**
```bash
# 1. Install Proxmox VE on spare hardware
wget https://www.proxmox.com/en/downloads
# Follow installation wizard

# 2. Configure network interfaces (same as failed host)
nano /etc/network/interfaces
# Copy configuration from: assets/configs/proxmox/interfaces.conf

# 3. Mount TrueNAS backup storage
mkdir /mnt/backups
mount -t nfs 192.168.10.11:/mnt/tank/homelab/backups /mnt/backups
```

**Option B: No Spare Hardware (Extended Recovery)**
- Order replacement parts (timeline: 1-3 business days)
- Consider cloud migration as temporary measure
- Notify stakeholders of extended RTO

#### Phase 3: Service Restoration (2-3 hours)

**Priority Order (restore in sequence):**

1. **Critical Services (First 1 hour):**
   ```bash
   # Restore Nginx Proxy Manager (VM 100)
   qmrestore /mnt/backups/vzdump-qemu-100-latest.vma.zst 100
   qm start 100

   # Verify service
   curl -I https://proxy.homelab.local
   ```

2. **Monitoring Stack (30 minutes):**
   ```bash
   # Restore monitoring services (VM 101)
   qmrestore /mnt/backups/vzdump-qemu-101-latest.vma.zst 101
   qm start 101

   # Verify Grafana accessible
   curl -I https://grafana.homelab.local
   ```

3. **Family Services (1 hour):**
   ```bash
   # Restore Immich photo service (VM 102)
   qmrestore /mnt/backups/vzdump-qemu-102-latest.vma.zst 102
   qm start 102

   # Verify photo upload/download works
   ```

4. **Supporting Services:**
   ```bash
   # Restore Wiki.js and other services
   qmrestore /mnt/backups/vzdump-qemu-103-latest.vma.zst 103
   qm start 103
   ```

#### Phase 4: Verification (30 minutes)

**Service verification checklist:**
- [ ] All VMs started successfully
- [ ] Network connectivity verified
- [ ] DNS resolution working
- [ ] SSL certificates valid
- [ ] User authentication functional
- [ ] Data integrity confirmed (spot checks)

**Data integrity verification:**
```bash
# Check PostgreSQL databases
docker exec -it immich_postgres psql -U immich -c "SELECT COUNT(*) FROM assets;"

# Verify ZFS snapshots accessible
ssh root@192.168.10.11
zfs list -t snapshot tank/homelab/media
```

#### Phase 5: Post-Recovery (30 minutes)

1. **Update documentation:**
   - Record incident details
   - Document recovery steps taken
   - Note any deviations from plan

2. **Notify stakeholders:**
   ```
   Subject: [RESOLVED] Homelab Infrastructure Recovery Complete

   Service has been restored as of [TIME].

   RTO achieved: [X] hours
   Data loss: [NONE / description]
   Services affected: [list]
   Root cause: [description]

   Next steps:
   - Root cause analysis scheduled
   - Hardware replacement planned
   - DR plan update based on lessons learned
   ```

3. **Schedule post-mortem:**
   - Within 48 hours of recovery
   - Document lessons learned
   - Identify improvement opportunities

---

### Scenario 2: TrueNAS Storage Failure

**Symptoms:**
- ZFS pool degraded or faulted
- Disk failure detected
- Cannot access NFS shares

**Recovery Steps:**

#### Phase 1: Assessment (10 minutes)

```bash
# SSH to TrueNAS
ssh root@192.168.10.11

# Check pool status
zpool status tank

# Check disk health
smartctl -a /dev/sda
smartctl -a /dev/sdb
```

**Determine failure severity:**
- **Single disk failure in mirror:** DEGRADED (can continue operating)
- **Multiple disk failures:** FAULTED (data loss risk, immediate action)
- **Pool corruption:** UNAVAIL (requires expert recovery)

#### Phase 2: Immediate Mitigation (30 minutes)

**For DEGRADED pool (single disk failure):**
```bash
# Replace failed disk
zpool replace tank old_disk new_disk

# Monitor resilver progress
watch -n 10 'zpool status tank'

# Expected resilver time: 4-8 hours for 2TB disk
```

**For FAULTED pool (multiple disk failures):**
```bash
# DO NOT attempt repairs without backups verified
# Import pool as read-only
zpool import -o readonly=on tank

# Copy critical data to external storage
rsync -avP /mnt/tank/homelab/databases /mnt/external/emergency/
rsync -avP /mnt/tank/homelab/configs /mnt/external/emergency/
```

#### Phase 3: Data Recovery (varies)

**Option A: Restore from offsite backup**
```bash
# Mount offsite backup location (Dad's house)
# Via Syncthing or physical drive

# Restore critical datasets
zfs receive tank/homelab/databases < /mnt/offsite/databases-snapshot.zfs
zfs receive tank/homelab/media < /mnt/offsite/media-snapshot.zfs
```

**Option B: Professional data recovery**
- Contact data recovery service
- Cost: $500-$2000+ depending on severity
- Timeline: 1-2 weeks
- Success rate: 60-90%

#### Phase 4: Rebuild Storage (2-4 hours)

```bash
# Create new pool (if complete rebuild needed)
zpool create tank mirror /dev/sda /dev/sdb

# Restore datasets from backup
zfs receive tank/homelab < /mnt/backup/full-backup.zfs

# Verify data integrity
zfs scrub tank
zpool status -v tank
```

---

### Scenario 3: Network Infrastructure Failure

**Symptoms:**
- Internet connectivity lost
- VLAN segmentation broken
- VPN inaccessible

**Recovery Steps:**

#### Phase 1: Isolate Issue (15 minutes)

**Check layer by layer:**
```bash
# Layer 1: Physical connectivity
# Check cable connections, link lights

# Layer 2: Switch connectivity
# Access UniFi switch via console port

# Layer 3: Gateway/routing
ping 192.168.10.1  # Gateway
ping 8.8.8.8       # Internet
ping 1.1.1.1       # Cloudflare DNS

# Layer 4-7: Services
curl https://photos.homelab.local
```

#### Phase 2: Restore Connectivity (30 minutes)

**Option A: UniFi Gateway failure**
```bash
# Connect backup router
# Configure basic NAT/firewall
# Temporary solution: single flat network

# Update DNS records if needed
# Point services to temporary IP addresses
```

**Option B: Switch failure**
```bash
# Replace with spare switch
# Restore configuration from backup
# UniFi controller > Settings > System > Backup/Restore

# Verify VLAN trunking
show vlan brief
show interfaces trunk
```

#### Phase 3: Restore Segmentation (1 hour)

```bash
# Import UniFi configuration backup
# Assets: assets/configs/networking/unifi-backup.json

# Verify firewall rules applied
# Test inter-VLAN connectivity
ping -c 3 192.168.10.10  # Management VLAN
ping -c 3 192.168.20.10  # Admin VLAN
ping -c 3 192.168.30.10  # Application VLAN
```

---

### Scenario 4: Ransomware / Security Breach

**Symptoms:**
- Encrypted files detected
- Unusual system behavior
- Unauthorized access alerts
- Suspicious network traffic

**Immediate Actions (DO NOT DELAY):**

1. **ISOLATE affected systems:**
   ```bash
   # Disable network interfaces immediately
   ip link set enp0s31f6 down

   # Disconnect from UniFi switch (physical)
   # Block at firewall level
   ```

2. **PRESERVE evidence:**
   ```bash
   # Do not reboot or shutdown
   # Capture memory dump if possible
   # Document all indicators

   # Take screenshots of:
   # - Ransom notes
   # - File listings
   # - Process lists
   # - Network connections
   ```

3. **NOTIFY stakeholders:**
   - Inform sponsor immediately
   - Document timeline of events
   - Do NOT pay ransom

4. **ASSESS scope:**
   ```bash
   # Check for encrypted files
   find / -name "*.encrypted" -o -name "*.locked" 2>/dev/null

   # Review authentication logs
   grep -i "accepted publickey" /var/log/auth.log

   # Check cron jobs for backdoors
   crontab -l
   ```

5. **RESTORE from clean backups:**
   ```bash
   # Use oldest known-good backup
   # Verify backup integrity before restore
   sha256sum /mnt/backups/*.vma.zst

   # Restore to isolated network first
   # Verify no malware present
   # Then restore to production
   ```

6. **HARDEN and monitor:**
   - Change all credentials
   - Review firewall rules
   - Enable additional logging
   - Schedule security audit

---

## Recovery Time Objectives (RTO)

| Scenario | Target RTO | Actual RTO (Last Test) | Status |
|----------|------------|------------------------|--------|
| Complete host failure | 4 hours | Not tested | ⚠️ Test scheduled |
| Storage failure | 4 hours | Not tested | ⚠️ Test scheduled |
| Network failure | 2 hours | Not tested | ⚠️ Test scheduled |
| Security breach | Immediate isolation | Not tested | ⚠️ Test scheduled |

---

## Testing Schedule

| Test Type | Frequency | Last Performed | Next Scheduled |
|-----------|-----------|----------------|----------------|
| Full DR simulation | Quarterly | TBD | Q1 2026 |
| Backup restore test | Monthly | TBD | Jan 2026 |
| Network failover | Bi-annually | TBD | Jun 2026 |
| Runbook walkthrough | Monthly | TBD | Jan 2026 |

---

## Recovery Resources

### Required Hardware
- [ ] Spare server (or cloud VM credits)
- [ ] Spare network equipment (switch, router)
- [ ] Spare hard drives (matching pool configuration)
- [ ] USB boot drives (Proxmox installer)
- [ ] Console cables (serial, USB)

### Required Access
- [ ] Physical datacenter access
- [ ] IPMI/iLO credentials
- [ ] Root credentials (encrypted, offline storage)
- [ ] Backup encryption keys
- [ ] VPN configuration files

### Required Documentation
- [ ] This DR runbook (printed copy)
- [ ] Network topology diagram
- [ ] IP address allocation table
- [ ] Service dependency map
- [ ] Vendor contact information

---

## Post-Recovery Checklist

```
Disaster Recovery - Post-Recovery Checklist
Incident Date: __________ Recovery Date: __________

[ ] All services restored and verified
[ ] Data integrity confirmed
[ ] Performance within normal parameters
[ ] Monitoring re-enabled
[ ] Backups running successfully
[ ] Security scan completed (no new vulnerabilities)
[ ] Stakeholders notified of resolution
[ ] Incident report documented
[ ] Post-mortem scheduled
[ ] DR plan updated with lessons learned

RTO Achieved: _____ hours (target: ≤ 4 hours)
RPO Achieved: _____ hours (target: ≤ 24 hours)

Notes:
_________________________________________________
_________________________________________________

Completed by: _________________ Date: _________
```

---

## Lessons Learned Template

**Incident Summary:**
- Date/Time:
- Duration:
- Services affected:
- Root cause:

**What Went Well:**
1.
2.
3.

**What Went Wrong:**
1.
2.
3.

**Action Items:**
| Action | Owner | Due Date | Priority |
|--------|-------|----------|----------|
|        |       |          |          |

---

**Last Updated:** 2024-12-16
**Owner:** Samuel Jackson
**Next Review:** Quarterly
**Next Test:** Q1 2026
