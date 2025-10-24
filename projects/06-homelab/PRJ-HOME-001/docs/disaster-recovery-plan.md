# Disaster Recovery & Backup Plan
**Project:** PRJ-HOME-001 – UniFi Home Network  \
**Revision:** 2024-06-09

---

## 1. Objectives
- Restore critical connectivity (internet, trusted Wi-Fi) within 4 hours (RTO).
- Restore security monitoring (UniFi Protect) within 8 hours.
- Limit data loss of configurations and recordings to < 24 hours (RPO).

## 2. Critical Components & Priority
| Priority | Component | Function | RTO | RPO |
| --- | --- | --- | --- | --- |
| P1 | UDM-Pro | Routing, firewall, controller | 4h | 12h |
| P1 | Switch Pro 24 PoE | PoE distribution | 4h | n/a |
| P1 | Outdoor AP + Cameras | Security coverage | 8h | 12h |
| P2 | Cloud Key Gen2 Plus | UniFi Protect storage | 8h | 12h |
| P2 | NAS (TrueNAS) | Backups, DNS, NTP | 8h | 12h |
| P3 | Guest Wi-Fi | Visitor access | 24h | 24h |

## 3. Backup Strategy
- **Configurations:**
  - UniFi OS automated nightly backups to Cloud Key + external NAS (Services VLAN).
  - Weekly off-site sync of configuration backups to encrypted cloud storage (Backblaze B2).
- **UniFi Protect Footage:**
  - Continuous recording stored on Cloud Key; daily snapshot of critical footage exported to NAS.
  - Monthly export of doorbell motion clips for archival review.
- **Documentation:**
  - Git repository mirrored to remote origin (GitHub) after major updates.

## 4. Recovery Procedures
### 4.1 UDM-Pro Failure
1. Retrieve spare UDM-Pro (cold standby) from equipment shelf.
2. Restore latest configuration backup via USB or remote repository.
3. Swap WAN/LAN cables; power on; verify VLANs and firewall rules.
4. Confirm internet access and management reachability.

### 4.2 Switch Failure
1. Replace with spare UniFi Switch 24 PoE (pre-configured profile).
2. Restore configuration by adopting switch in UniFi Network and applying saved port profiles.
3. Validate PoE delivery to each AP/camera; adjust port mapping if necessary.

### 4.3 Power Outage > UPS Runtime
1. UPS sends SNMP trap to NAS triggering safe shutdown of Cloud Key + NAS.
2. After power restoration, bring up UPS → switch → UDM-Pro → Cloud Key → NAS in order.
3. Verify services resume; check integrity of Protect database.

### 4.4 Storage Failure (Cloud Key HDD)
1. Replace failed HDD with spare 2.5" drive; reinsert into Cloud Key.
2. Restore Protect backup from NAS (Settings → General → Backup).
3. Validate camera feeds and historical timeline.

## 5. Testing & Validation
- Quarterly failover drill: simulate UDM-Pro failure using spare, document results.
- Semi-annual restore test of Protect archive to ensure backup validity.
- Annual full power-down test to confirm UPS notifications and orderly shutdown.

## 6. Communication Plan
- Notify homeowner/stakeholders immediately upon disaster declaration (SMS + email).
- Provide status updates every hour until recovery.
- Document timeline and actions in incident log; conduct review within 48 hours.

## 7. Continuous Improvement
- After each drill or actual event, update this plan and associated runbooks.
- Track MTTD/MTTR metrics in monitoring dashboard; adjust objectives if necessary.

