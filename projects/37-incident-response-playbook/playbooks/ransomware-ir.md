# Ransomware Incident Response Playbook

**Playbook ID:** IRP-001
**Version:** 2.1
**Last Updated:** 2026-01-10
**Classification:** Internal — Restricted
**Owner:** Security Operations / CISO Office

---

## Scope

This playbook governs response to ransomware incidents affecting corporate endpoints, servers,
cloud workloads, or OT/ICS environments. It covers the full PICERL lifecycle:
**Preparation → Identification → Containment → Eradication → Recovery → Lessons Learned**.

---

## Phase 1 — Preparation

### Required Assets (verify quarterly)

| Asset | Location | Owner | Last Verified |
|-------|----------|-------|---------------|
| Offline backup sets | NAS-BACKUP01, AWS S3 Glacier | Infra | 2026-01-03 |
| IR toolkit USB drives (x4) | SOC safe (drawer 2) | SOC Lead | 2026-01-03 |
| Out-of-band comms (Signal group "IR-TEAM") | Mobile devices | All IR members | 2025-12-15 |
| Forensics workstation (air-gapped) | Server Room Rack B | SecOps | 2025-12-15 |
| Cyber insurance policy (Policy #CYB-2025-9981) | CISO SharePoint | CISO | 2025-11-01 |
| Law enforcement pre-notification (FBI IC3) | On file | Legal | 2025-11-01 |

### Preparation Checklist

- [ ] Incident response retainer (IR firm) contact available
- [ ] Tabletop exercise completed in last 6 months
- [ ] Backup restoration tested in last 30 days
- [ ] EDR coverage > 98% of endpoints
- [ ] Network segmentation verified (VLAN isolation confirmed)

---

## Phase 2 — Identification

### Initial Detection Triggers

```
HIGH-CONFIDENCE INDICATORS:
  - EDR alert: ransomware family identified (CrowdStrike, Defender ATP)
  - Mass file extension changes (.locked, .enc, .crypto, .WNCRY)
  - Ransom note files present (README.txt, HOW_TO_DECRYPT.txt)
  - Volume Shadow Copy deletion (vssadmin delete shadows /all)
  - Rapid SMB/RDP lateral movement alerts
  - Unusual outbound data transfer (>5 GB) before encryption starts

MEDIUM-CONFIDENCE INDICATORS:
  - Multiple failed logins followed by success from new country
  - Cobalt Strike / Metasploit beacon detected
  - Living-off-the-land tool abuse (certutil, powershell -enc, wmic)
  - New scheduled tasks created by non-admin accounts
```

### Identification Checklist

1. **Confirm it is ransomware** (not a false positive or simulation)
   - Verify file extensions changed on > 3 hosts
   - Confirm ransom note or C2 beacon present
2. **Identify patient zero** — first infected host (check EDR timeline)
3. **Determine ransomware family** — upload sample to VirusTotal / any.run
4. **Assess blast radius** — how many hosts/shares are affected?
5. **Check for data exfiltration** — review proxy/firewall logs for large outbound transfers
6. **Declare incident** — notify Incident Commander (IC)
7. **Open incident ticket** — INC-YYYY-NNNN format

---

## Phase 3 — Containment

### Immediate Actions (within 15 minutes)

```bash
# Isolate affected hosts via EDR console (CrowdStrike example)
falcon-host-management contain --host-ids <comma_separated_ids>

# Or via network VLAN isolation (Cisco IOS)
interface GigabitEthernet0/X
  shutdown

# Block known C2 IPs at perimeter firewall
# Add entries to threat intel block list
```

### Containment Decision Matrix

| Scope | Action | Authority Required |
|-------|--------|--------------------|
| 1–5 hosts | Isolate hosts via EDR | SOC Analyst |
| 6–20 hosts | VLAN isolation + isolate | SOC Lead |
| 21–100 hosts | Network segment shutdown | CISO + IT Director |
| > 100 hosts / DC affected | Full network isolation + crisis team | CEO + CISO |

### Containment Checklist

- [ ] Affected hosts isolated (confirm no outbound connectivity)
- [ ] Shared drives unmounted from non-affected hosts
- [ ] VPN access suspended for affected user accounts
- [ ] Backups verified as unaffected and offline/immutable
- [ ] Cloud sync (OneDrive/SharePoint) suspended to prevent spread
- [ ] Credentials of affected accounts rotated
- [ ] Executive and legal notified (use out-of-band comms)

---

## Phase 4 — Eradication

### Eradication Checklist

- [ ] Full forensic image captured (before any remediation)
- [ ] Root cause identified (initial access vector confirmed)
- [ ] All affected hosts wiped and rebuilt from known-good images
- [ ] Persistence mechanisms removed (registry run keys, scheduled tasks, services)
- [ ] All credentials rotated (AD domain-wide password reset if DC affected)
- [ ] Threat actor TTPs mapped to ATT&CK — document all IOCs
- [ ] Patch applied for initial access vulnerability (if applicable)
- [ ] EDR exclusions reviewed — remove any attacker-added exclusions

### IOC Collection Template

```yaml
incident_id: INC-2026-NNNN
ransomware_family: "<identified_family>"
initial_access_vector: "<phishing | exploited_vuln | rdb | supply_chain>"
patient_zero_hostname: "<hostname>"
patient_zero_user: "<domain\\username>"
infection_datetime_utc: "YYYY-MM-DDTHH:MM:SSZ"
c2_ips:
  - "x.x.x.x"
  - "x.x.x.x"
c2_domains:
  - "malicious.example.com"
file_hashes_sha256:
  - "<hash_of_ransomware_binary>"
  - "<hash_of_dropper>"
ransom_wallet_address: "<if_identified>"
exfil_confirmed: false
exfil_volume_gb: 0
affected_host_count: 0
affected_share_count: 0
```

---

## Phase 5 — Recovery

### Recovery Priority Tiers

| Tier | Systems | Target RTO |
|------|---------|-----------|
| 1 | Domain Controllers, DNS, DHCP | 2 hours |
| 2 | Core business apps (ERP, billing, email) | 8 hours |
| 3 | File servers, collaboration tools | 24 hours |
| 4 | Developer workstations, test systems | 72 hours |

### Recovery Checklist

- [ ] Recovery team authorised by CISO / crisis management
- [ ] Restore from last known-good backup (verify backup integrity first)
- [ ] Systems rebuilt in isolated environment — test before reconnecting
- [ ] Business-critical services validated before customer-facing reconnect
- [ ] Monitoring enhanced on recovered systems (extended retention)
- [ ] EDR agent updated and policy hardened before reconnect
- [ ] Stakeholder communication issued (internal + external if required)

---

## Phase 6 — Lessons Learned

### Post-Incident Review (PIR) — within 5 business days

1. Timeline reconstruction (minute-by-minute from first indicator to resolution)
2. Root cause analysis (5 Whys or fishbone diagram)
3. Detection gap analysis (what should have caught this earlier?)
4. Control failures identified
5. Action items assigned with owners and deadlines
6. Metrics recorded: MTTD, MTTC, MTTR

### PIR Report Template → see [`templates/post-incident-report.md`](../templates/post-incident-report.md)

---

## Appendix A — Ransomware Families Quick Reference

| Family | Ext | Decryptor Available | Notes |
|--------|-----|---------------------|-------|
| WannaCry | .WNCRY | Yes (wanakiwi) | Requires SMB port closed |
| REvil / Sodinokibi | .random | No (keys seized) | Affiliates active again 2024 |
| LockBit 3.0 | .lockbit | Partial | Law enforcement disruption 2024 |
| BlackCat / ALPHV | .alphv | No | Rust-based, multi-platform |
| Clop | .clop | No | GoAnywhere/MOVEit campaigns |
| Akira | .akira | No | VMware ESXi variant |

---

## Contacts

| Role | Name | Primary | Out-of-Band |
|------|------|---------|-------------|
| Incident Commander | SOC Lead | SOC Slack | Signal |
| CISO | [CISO name] | Email | Mobile |
| Legal Counsel | [Legal name] | Email | Mobile |
| IR Retainer | [Firm name] | +1-800-XXX-0001 | 24/7 hotline |
| FBI Cyber Division | n/a | 1-855-292-3937 | IC3.gov |
