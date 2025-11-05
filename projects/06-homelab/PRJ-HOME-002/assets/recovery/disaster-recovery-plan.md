# Disaster Recovery Plan
# Homelab Virtualization Infrastructure
# Version: 1.0
# Last Updated: 2025-11-05

## Document Control

**Document Owner:** Samuel Jackson  
**Classification:** Internal Use Only  
**Distribution:** IT Administration Team  
**Review Frequency:** Quarterly  
**Last DR Test:** 2025-11-01  
**Next DR Test:** 2026-02-01  

---

## Table of Contents

1. [Overview](#overview)
2. [Recovery Objectives](#recovery-objectives)
3. [Disaster Scenarios](#disaster-scenarios)
4. [Recovery Procedures](#recovery-procedures)
5. [Contact Information](#contact-information)
6. [Testing and Validation](#testing-and-validation)

---

## Overview

### Purpose
This Disaster Recovery (DR) Plan outlines procedures to recover the homelab virtualization infrastructure in the event of catastrophic failure, ensuring minimal downtime and data loss.

### Scope
- **In Scope:** Proxmox cluster, core services VMs, critical applications, storage systems
- **Out of Scope:** Desktop workstations, IoT devices, non-critical development VMs

### Assumptions
- At least one backup copy is accessible
- Replacement hardware can be obtained within 72 hours if needed
- Network infrastructure (pfSense, UniFi) is operational or can be restored first
- Offsite backup is accessible if local backups are lost

---

## Recovery Objectives

### Recovery Time Objective (RTO)

| Service Tier | RTO | Priority |
|--------------|-----|----------|
| Critical Infrastructure (FreeIPA, DNS) | 1 hour | P0 |
| Core Services (Nginx, Syslog) | 4 hours | P1 |
| Standard Applications (Wiki.js, Home Assistant) | 24 hours | P2 |
| Development/Test VMs | 7 days | P3 |

### Recovery Point Objective (RPO)

| Service Tier | RPO | Backup Frequency |
|--------------|-----|------------------|
| Critical Infrastructure | 24 hours | Daily |
| Core Services | 24 hours | Daily |
| Standard Applications | 7 days | Weekly |
| Development/Test VMs | 7 days | Weekly |

### Data Recovery Priority

1. **Priority 0 (Critical):**
   - FreeIPA/RADIUS (Authentication)
   - Pi-hole DNS
   - pfSense firewall configuration

2. **Priority 1 (High):**
   - Nginx reverse proxy
   - Centralized syslog
   - Proxmox cluster configuration

3. **Priority 2 (Medium):**
   - Wiki.js knowledge base
   - Home Assistant automation
   - Monitoring stack (Grafana, Prometheus)

4. **Priority 3 (Low):**
   - Development VMs
   - Test environments

---

## Disaster Scenarios

### Scenario 1: Single Node Failure

**Impact:** Loss of 1 out of 3 Proxmox nodes  
**Severity:** Medium  
**RTO:** 4 hours  

**Response:**
1. Verify cluster quorum (2 nodes remaining)
2. HA services automatically migrate to healthy nodes
3. Replace failed node hardware
4. Rejoin node to cluster
5. Rebalance VM distribution

**See:** [Recovery Procedures - Single Node](recovery-procedures/vm-migration.md)

---

### Scenario 2: Complete Cluster Failure

**Impact:** Loss of all 3 Proxmox nodes  
**Severity:** Critical  
**RTO:** 24 hours  

**Response:**
1. Assess cause of failure (power, network, corruption)
2. Restore network infrastructure first (pfSense, switch)
3. Rebuild Proxmox nodes from scratch
4. Restore VMs from Proxmox Backup Server
5. Verify services and reconfigure cluster

**See:** [Recovery Procedures - Complete Rebuild](recovery-procedures/service-restoration.md)

---

### Scenario 3: Storage Failure (Ceph)

**Impact:** Loss of distributed storage  
**Severity:** High  
**RTO:** 8 hours  

**Response:**
1. Assess Ceph cluster health
2. Replace failed OSDs if hardware failure
3. Restore from replication (3 copies)
4. If complete loss, restore VMs from backups
5. Recreate Ceph pools and restore data

**See:** [Recovery Procedures - Storage](recovery-procedures/storage-failover.md)

---

### Scenario 4: TrueNAS Storage Failure

**Impact:** Loss of backup storage and NFS shares  
**Severity:** High  
**RTO:** 12 hours  

**Response:**
1. Verify offsite backup availability
2. Rebuild TrueNAS on replacement hardware
3. Restore configuration from backup
4. Recreate ZFS pools
5. Restore data from offsite backup

**See:** [Recovery Procedures - Storage](recovery-procedures/storage-failover.md)

---

### Scenario 5: Critical Service VM Failure

**Impact:** Loss of essential service (DNS, Auth, Proxy)  
**Severity:** High  
**RTO:** 1-4 hours (depending on service)  

**Response:**
1. Attempt VM restart on same or different node
2. If boot failure, restore from most recent backup
3. Verify service configuration
4. Update DNS/firewall if IP changed
5. Test service functionality

**See:** [Recovery Procedures - Service Restoration](recovery-procedures/service-restoration.md)

---

### Scenario 6: Complete Site Disaster

**Impact:** Total loss of homelab (fire, flood, theft)  
**Severity:** Critical  
**RTO:** 7-14 days  

**Response:**
1. Activate offsite backup recovery
2. Procure replacement hardware
3. Rebuild network infrastructure
4. Rebuild Proxmox cluster
5. Restore all VMs from offsite backup
6. Reconfigure services and validate

**See:** All recovery procedure documents

---

## Recovery Procedures

### Phase 1: Assessment (0-15 minutes)

1. **Identify the Problem**
   - What failed? (Node, storage, service, network)
   - What is the impact? (Users affected, services down)
   - Is it hardware, software, or configuration?

2. **Check Monitoring**
   - Review Proxmox web interface
   - Check Grafana dashboards
   - Review syslog for errors
   - Run health check script: `./health-check.sh`

3. **Determine Recovery Path**
   - Can service be restarted?
   - Is VM migration possible?
   - Is restore from backup required?
   - Is hardware replacement needed?

---

### Phase 2: Communication (15-30 minutes)

1. **Notify Stakeholders**
   - Primary admin: [Phone/Email]
   - Secondary contact: [Phone/Email]
   - Users: Status page update

2. **Document Timeline**
   - Log incident start time
   - Document actions taken
   - Track progress toward recovery

---

### Phase 3: Stabilization (30 minutes - 2 hours)

1. **Network Infrastructure**
   - Verify pfSense is operational
   - Check switch and AP connectivity
   - Ensure DNS is resolving
   - Validate internet connectivity

2. **Proxmox Cluster**
   - Check cluster status: `pvecm status`
   - Verify quorum
   - Identify healthy nodes
   - Review HA services

3. **Storage**
   - Check Ceph health: `ceph -s`
   - Verify NFS mounts: `df -h`
   - Check PBS connectivity
   - Validate backup availability

---

### Phase 4: Recovery (2-24 hours)

**See detailed procedures in:**
- [Service Restoration](recovery-procedures/service-restoration.md)
- [VM Migration](recovery-procedures/vm-migration.md)
- [Storage Failover](recovery-procedures/storage-failover.md)

**General Recovery Steps:**

1. **Restore from Backup**
   ```bash
   # List available backups
   pvesh get /nodes/proxmox-01/storage/proxmox-backup/content
   
   # Restore VM
   qmrestore /path/to/backup.vma.zst 100 --storage local-lvm
   
   # Start VM
   qm start 100
   ```

2. **Verify Service**
   - Check VM console for boot errors
   - Verify network connectivity
   - Test service functionality
   - Update DNS if IP changed

3. **Validate Dependencies**
   - Check authentication (FreeIPA)
   - Verify DNS resolution (Pi-hole)
   - Test reverse proxy (Nginx)
   - Confirm monitoring (Grafana)

---

### Phase 5: Validation (After Recovery)

1. **Service Verification**
   - Run health check: `./health-check.sh`
   - Test user access
   - Verify data integrity
   - Check backups

2. **Documentation**
   - Update incident log
   - Document changes made
   - Note lessons learned
   - Update DR plan if needed

3. **Communication**
   - Notify users of restoration
   - Send incident report
   - Schedule post-mortem

---

## Contact Information

### Emergency Contacts

| Role | Name | Phone | Email | Availability |
|------|------|-------|-------|--------------|
| Primary Admin | Samuel Jackson | [REDACTED] | admin@homelab.local | 24/7 |
| Backup Admin | [Name] | [REDACTED] | backup@homelab.local | Business hours |

### Vendor Support

| Vendor | Service | Support Number | Account ID |
|--------|---------|----------------|------------|
| ISP | Internet Connectivity | [REDACTED] | [REDACTED] |
| Proxmox | Enterprise Support | N/A (Community) | N/A |
| Hardware | Server/Storage | [REDACTED] | [REDACTED] |

### External Resources

- Proxmox Documentation: https://pve.proxmox.com/wiki/
- Community Forum: https://forum.proxmox.com/
- Backup Repository: [Offsite Location/Cloud]

---

## Testing and Validation

### DR Test Schedule

**Frequency:** Quarterly  
**Next Test:** February 1, 2026  
**Duration:** 4 hours  
**Participants:** IT Admin Team  

### Test Scenarios

1. **Scenario 1: Service Restoration (Q1)**
   - Restore Pi-hole from backup
   - Verify DNS functionality
   - Document time to recovery

2. **Scenario 2: VM Migration (Q2)**
   - Migrate critical VMs to different node
   - Test HA failover
   - Validate service continuity

3. **Scenario 3: Node Failure (Q3)**
   - Simulate node failure
   - Verify cluster behavior
   - Test automatic recovery

4. **Scenario 4: Complete Recovery (Q4)**
   - Full cluster rebuild simulation
   - Restore all services
   - End-to-end testing

### Test Checklist

- [ ] Backups are accessible
- [ ] Restore procedures work
- [ ] RTO/RPO objectives met
- [ ] Documentation is accurate
- [ ] Contact information current
- [ ] Team trained on procedures
- [ ] Lessons learned documented
- [ ] DR plan updated

### Test Results

**Last Test Date:** November 1, 2025  
**Scenario Tested:** Service Restoration  
**Result:** Success  
**RTO Target:** 1 hour  
**Actual RTO:** 45 minutes  
**Observations:** Restore process smooth, documentation accurate  
**Improvements:** Added automation script for common restore tasks  

---

## Backup Verification

### Daily Verification
- Automated backup completion check
- Email notification on failure
- Storage capacity monitoring

### Weekly Verification
- Manual inspection of backup logs
- Random restore test of 1 VM
- Backup integrity verification

### Monthly Verification
- Full restore test of critical VM
- Offsite backup sync verification
- Backup retention policy review

---

## Data Recovery Procedures

### From Proxmox Backup Server

```bash
# 1. List available backups
pvesh get /nodes/node-name/storage/proxmox-backup/content

# 2. Restore VM
qmrestore proxmox-backup:backup/vm-100-* 100 --storage local-lvm

# 3. Start restored VM
qm start 100
```

### From NFS Backup

```bash
# 1. List backups
ls -lh /mnt/pve/truenas-backups/dump/

# 2. Restore
qmrestore /mnt/pve/truenas-backups/dump/vzdump-qemu-100-*.vma.zst 100

# 3. Start VM
qm start 100
```

### From Offsite Backup

```bash
# 1. Download backup from offsite
rsync -avz offsite-server:/backups/homelab/ /tmp/restore/

# 2. Restore as above
qmrestore /tmp/restore/vzdump-qemu-100-*.vma.zst 100
```

---

## Appendix

### Related Documentation
- [Service Restoration Procedures](recovery-procedures/service-restoration.md)
- [VM Migration Guide](recovery-procedures/vm-migration.md)
- [Storage Failover](recovery-procedures/storage-failover.md)
- [Backup Configuration](../proxmox/backup-config.json)

### Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-05 | Samuel Jackson | Initial DR plan creation |

---

**Document Classification:** Internal Use Only  
**Next Review Date:** February 5, 2026
