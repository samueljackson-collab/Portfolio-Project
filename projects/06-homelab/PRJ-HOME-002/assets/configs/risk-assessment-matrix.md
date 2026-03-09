# Homelab Risk Assessment Matrix

## Risk Assessment Framework

### Probability Levels
- **High (H):** Likely to occur (>50% chance annually)
- **Medium (M):** Possible (10-50% chance annually)
- **Low (L):** Unlikely (<10% chance annually)

### Impact Levels
- **Critical:** Data loss, major service outage >24h, security breach
- **High:** Significant service degradation, recovery required
- **Medium:** Minor service disruption, workaround available
- **Low:** Minimal impact, easily resolved

### Risk Matrix

|                     | **Low Impact** | **Medium Impact** | **High Impact** | **Critical Impact** |
|---------------------|----------------|-------------------|-----------------|---------------------|
| **High Probability** | Monitor        | Monitor           | **Mitigate**    | **Mitigate**        |
| **Medium Probability** | Accept         | Monitor           | **Mitigate**    | **Avoid/Mitigate**  |
| **Low Probability**  | Accept         | Accept            | Monitor         | **Avoid/Mitigate**  |

---

## Identified Risks & Mitigation

### CRITICAL RISKS (Mitigate Immediately)

#### Risk 1: Data Loss
- **Probability:** Medium
- **Impact:** Critical
- **Risk Score:** 8/10
- **Description:** Loss of family photos, documents, or critical data due to hardware failure, ransomware, or accidental deletion

**Mitigation Strategies:**
1. ✅ **Implemented:** 3-2-1 backup strategy (TrueNAS + PBS + Backblaze B2)
2. ✅ **Implemented:** ZFS with hourly snapshots (24h retention)
3. ✅ **Implemented:** Immutable backups on PBS
4. ✅ **Implemented:** Weekly offsite backup verification
5. ✅ **Implemented:** Quarterly DR drill

**Residual Risk:** Low (2/10)  
**Next Review:** Quarterly

---

#### Risk 2: Privacy Breach (IP Cameras)
- **Probability:** Medium
- **Impact:** Critical
- **Risk Score:** 8/10
- **Description:** Unauthorized access to IP camera feeds, exposing private moments or enabling surveillance

**Mitigation Strategies:**
1. ✅ **Implemented:** Cameras on isolated VLAN 50 (no internet access)
2. ✅ **Implemented:** Default passwords changed to strong unique passwords
3. ✅ **Implemented:** Frigate NVR with local-only storage
4. ✅ **Implemented:** Privacy zones configured (bedrooms, bathrooms)
5. ⚠️ **In Progress:** Regular firmware updates (manual process)
6. ⚠️ **Planned:** Camera access logging and monitoring

**Residual Risk:** Medium (5/10)  
**Next Review:** Monthly

---

#### Risk 3: Ransomware Attack
- **Probability:** Low
- **Impact:** Critical
- **Risk Score:** 6/10
- **Description:** Ransomware encrypts homelab data, demanding payment for decryption key

**Mitigation Strategies:**
1. ✅ **Implemented:** Network segmentation (IoT/Guest isolated)
2. ✅ **Implemented:** Immutable PBS backups (cannot be encrypted)
3. ✅ **Implemented:** Offsite backups (unaffected by local ransomware)
4. ✅ **Implemented:** Email filtering and phishing protection
5. ✅ **Implemented:** Antivirus on Windows workstations
6. ⚠️ **Planned:** Automated threat detection (Wazuh/OSSEC)

**Residual Risk:** Low (3/10)  
**Next Review:** Quarterly

---

### HIGH RISKS (Monitor & Mitigate)

#### Risk 4: Primary Storage (SSD) Failure
- **Probability:** High (SSDs degrade over time)
- **Impact:** High
- **Risk Score:** 7/10
- **Description:** Primary TrueNAS SSD fails, causing service outage until replacement

**Mitigation Strategies:**
1. ✅ **Implemented:** ZFS mirror (2-disk redundancy)
2. ✅ **Implemented:** SMART monitoring with Prometheus alerts
3. ✅ **Implemented:** ZFS scrub weekly (data integrity check)
4. ✅ **Implemented:** Hot spare drive available
5. ⚠️ **Planned:** Predictive failure analysis (ML on SMART data)

**Residual Risk:** Low (3/10)  
**Next Review:** Monthly (SMART data)

---

#### Risk 5: Power Outage
- **Probability:** Medium
- **Impact:** Medium
- **Risk Score:** 5/10
- **Description:** Extended power outage causes service disruption and potential data corruption

**Mitigation Strategies:**
1. ✅ **Implemented:** UPS (1500VA) on critical equipment
2. ✅ **Implemented:** Graceful shutdown scripts (NUT - Network UPS Tools)
3. ✅ **Implemented:** UPS monitoring via Prometheus
4. ⚠️ **Planned:** Generator for extended outages (>4 hours)
5. ⚠️ **Planned:** Automatic service restart after power restoration

**Residual Risk:** Low (2/10)  
**Next Review:** Annually

---

#### Risk 6: ISP Outage
- **Probability:** Medium
- **Impact:** Medium
- **Risk Score:** 5/10
- **Description:** Internet service outage disrupts cloud-dependent services and remote access

**Mitigation Strategies:**
1. ✅ **Implemented:** Local services (wiki, photos) function without internet
2. ⚠️ **Planned:** Cellular backup (LTE failover)
3. ⚠️ **Planned:** Dual-WAN with load balancing
4. ✅ **Implemented:** Offline documentation for troubleshooting

**Residual Risk:** Medium (4/10)  
**Next Review:** Semi-annually

---

#### Risk 7: Proxmox Host Hardware Failure
- **Probability:** Low
- **Impact:** High
- **Risk Score:** 5/10
- **Description:** Proxmox host motherboard/CPU failure causes all VMs to go offline

**Mitigation Strategies:**
1. ✅ **Implemented:** Daily VM backups to PBS
2. ✅ **Implemented:** VM configs in Git repository
3. ⚠️ **Planned:** Second Proxmox host for HA clustering
4. ✅ **Implemented:** Documented recovery procedure (restore VMs to new hardware)

**Residual Risk:** Medium (4/10)  
**Next Review:** Annually

---

### MEDIUM RISKS (Monitor)

#### Risk 8: VPN Misconfiguration
- **Probability:** Medium
- **Impact:** Medium
- **Risk Score:** 4/10
- **Description:** WireGuard VPN misconfiguration exposes internal network or blocks remote access

**Mitigation Strategies:**
1. ✅ **Implemented:** VPN config in version control (Git)
2. ✅ **Implemented:** Split-tunnel VPN (only homelab traffic)
3. ✅ **Implemented:** Firewall rules limit VPN access to trusted VLAN
4. ✅ **Implemented:** Regular connectivity testing
5. ⚠️ **Planned:** Automated VPN health checks

**Residual Risk:** Low (2/10)  
**Next Review:** Quarterly

---

#### Risk 9: DNS Failure (Pi-hole)
- **Probability:** Low
- **Impact:** Medium
- **Risk Score:** 3/10
- **Description:** Pi-hole DNS server failure causes all internal DNS resolution to fail

**Mitigation Strategies:**
1. ✅ **Implemented:** Secondary DNS (1.1.1.1 Cloudflare) in DHCP
2. ⚠️ **Planned:** Redundant Pi-hole instance
3. ✅ **Implemented:** Pi-hole backup configuration weekly
4. ✅ **Implemented:** Monitoring via Prometheus (DNS query success rate)

**Residual Risk:** Low (2/10)  
**Next Review:** Semi-annually

---

#### Risk 10: Docker Container Vulnerability
- **Probability:** Medium
- **Impact:** Medium
- **Risk Score:** 4/10
- **Description:** Vulnerable container image exploited, potentially compromising host

**Mitigation Strategies:**
1. ✅ **Implemented:** LXC containers with unprivileged mode where possible
2. ⚠️ **Planned:** Automated vulnerability scanning (Trivy, Clair)
3. ⚠️ **Planned:** Image update automation (Watchtower)
4. ✅ **Implemented:** Network isolation (containers on separate VLANs)

**Residual Risk:** Medium (3/10)  
**Next Review:** Quarterly

---

### LOW RISKS (Accept with Monitoring)

#### Risk 11: Thermal Issues (Overheating)
- **Probability:** Low
- **Impact:** Low
- **Risk Score:** 2/10
- **Description:** Equipment overheating due to inadequate cooling in rack

**Mitigation Strategies:**
1. ✅ **Implemented:** Rack-mounted fans with temperature monitoring
2. ✅ **Implemented:** Prometheus alerts for CPU temp >80°C
3. ✅ **Implemented:** Adequate ventilation around rack

**Residual Risk:** Very Low (1/10)  
**Next Review:** Annually

---

#### Risk 12: Network Configuration Drift
- **Probability:** Low
- **Impact:** Low
- **Risk Score:** 2/10
- **Description:** Manual network changes not documented, causing confusion

**Mitigation Strategies:**
1. ✅ **Implemented:** Network config backed up weekly
2. ✅ **Implemented:** Change log maintained in wiki
3. ⚠️ **Planned:** Infrastructure as Code (Terraform for UniFi)

**Residual Risk:** Very Low (1/10)  
**Next Review:** Annually

---

## Risk Treatment Summary

| Risk ID | Risk Name | Inherent Risk | Mitigation Status | Residual Risk | Priority |
|---------|-----------|---------------|-------------------|---------------|----------|
| 1 | Data Loss | Critical | ✅ Implemented | Low | 🔴 Critical |
| 2 | Privacy Breach | Critical | ⚠️ In Progress | Medium | 🔴 Critical |
| 3 | Ransomware | Critical | ⚠️ In Progress | Low | 🟡 High |
| 4 | SSD Failure | High | ✅ Implemented | Low | 🟡 High |
| 5 | Power Outage | Medium | ✅ Implemented | Low | 🟢 Medium |
| 6 | ISP Outage | Medium | ⚠️ Planned | Medium | 🟢 Medium |
| 7 | Hardware Failure | High | ⚠️ In Progress | Medium | 🟡 High |
| 8 | VPN Misconfig | Medium | ✅ Implemented | Low | 🟢 Medium |
| 9 | DNS Failure | Low | ✅ Implemented | Low | 🟢 Low |
| 10 | Container Vuln | Medium | ⚠️ Planned | Medium | 🟢 Medium |
| 11 | Thermal Issues | Low | ✅ Implemented | Very Low | 🟢 Low |
| 12 | Config Drift | Low | ⚠️ In Progress | Very Low | 🟢 Low |

---

## Risk Review Schedule

- **Daily:** Monitor critical alerts (backup failures, security events)
- **Weekly:** Review backup success rate and security logs
- **Monthly:** Review high-risk items and update mitigation status
- **Quarterly:** Full risk assessment review and DR drill
- **Annually:** Comprehensive risk audit and update this document

---

## Incident Response Procedures

### Data Loss Incident
1. **Identify:** Determine scope of data loss
2. **Contain:** Prevent further loss (stop processes, isolate systems)
3. **Assess:** Check backups (ZFS snapshots → PBS → Backblaze B2)
4. **Recover:** Restore from most recent valid backup
5. **Review:** Root cause analysis and update mitigation

### Security Incident
1. **Detect:** Alert triggered or anomaly observed
2. **Isolate:** Disconnect affected system from network
3. **Analyze:** Determine attack vector and scope
4. **Eradicate:** Remove malware/backdoors, patch vulnerability
5. **Recover:** Restore from clean backup if necessary
6. **Lessons Learned:** Update firewall rules, IDS signatures

### Hardware Failure
1. **Identify:** Failed component via monitoring alerts
2. **Assess:** Check if redundancy is active (RAID, UPS, etc.)
3. **Order:** Replacement part (leverage hot spare if available)
4. **Replace:** Swap failed component
5. **Verify:** Run diagnostics and restore to full capacity
6. **Document:** Update asset inventory and lessons learned

---

**Document Version:** 1.0  
**Last Updated:** November 2024  
**Next Review:** February 2025  
**Owner:** Homelab Administrator
