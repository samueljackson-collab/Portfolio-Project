# SECURITY-POLICY: Homelab Defense & Operations

**Scope:** All systems and networks within PRJ-HOME-001 (pfSense, UniFi switching/wireless, Proxmox/TrueNAS, DMZ services).  
**Author:** Samuel Jackson  
**Version:** 1.0  
**Last Updated:** November 20, 2025  
**Classification:** Internal Use Only

---
## 1. Defense-in-Depth Model

| Layer | Primary Controls | Monitoring & Assurance |
|-------|------------------|-------------------------|
| **Perimeter (WAN)** | pfSense stateful firewall (default deny inbound), GeoIP/bogon blocks, rate limits, WAN DoS protections | Suricata inline on WAN, pfSense firewall logs to syslog, WAN availability alerts |
| **DMZ (VLAN 50)** | Isolated subnet, reverse proxy/WAF option, hardened OS baselines, least-privilege service accounts | Suricata inline on DMZ, web attack signatures, change-control approvals |
| **Internal Segmentation** | 5 VLANs with explicit inter-VLAN ACLs, uRPF/anti-spoofing, DHCP reservations, private addressing | Firewall rule change reviews, flow sampling, NetFlow/sFlow (where available) |
| **Endpoint/Server** | OS hardening, automatic security updates, host firewalls, EDR (where supported), SSH keys only | Centralized syslog, file integrity monitoring on servers, patch compliance dashboard |
| **Identity & Access** | RADIUS-backed WPA3 Enterprise, certificate-based VPN, MFA for admins, RBAC for controllers | Authentication logs (RADIUS/VPN), quarterly access reviews, failed-login alerting |
| **Data & Application** | TLS everywhere, encrypted backups, least-privilege DB accounts, secrets in vault/password manager | Backup verification logs, database audit logs, checksum validation |
| **Operations** | Daily log review, weekly rule tuning, quarterly tabletop exercises, tested backups | Maintenance windows with rollback plans, incident drills, runbook adherence |

---
## 2. WAN Ruleset (Inbound & Outbound)

### Inbound (WAN → Internal)
1. **Default deny** all unsolicited inbound traffic.  
2. **Allow HTTPS (443/TCP) & HTTP (80/TCP) to DMZ 192.168.50.0/24** via NAT/reverse proxy.  
3. **Allow OpenVPN (1194/UDP) to firewall** for authenticated remote access.  
4. **Allow ICMP echo-reply from firewall only** (diagnostics) — no pass-through.  
5. **Drop and log** everything else (including fragmented or bogon sources).

### Outbound (Internal → WAN)
- **Trusted (VLAN 10):** Full outbound except known malicious categories; egress logging enabled.  
- **Servers (VLAN 40):** HTTPS/HTTP, DNS, NTP, package mirrors; block high-risk ports (25/SMTP direct).  
- **IoT (VLAN 20) & Guest (VLAN 30):** HTTPS/HTTP/DNS/NTP only; deny RFC1918 destinations; enforce per-device rate limits.  
- **DMZ (VLAN 50):** HTTPS/HTTP for updates, DNS/NTP; no outbound to internal subnets; alert on any other attempt.  
- **All VLANs:** NAT with source tracking, egress IPS inspection, DNSSEC validation, block known C2 lists.

---
## 3. Inter-VLAN Security Policies (per VLAN)

### VLAN 10 – Trusted (192.168.10.0/24)
- **Allowed:** Full internet; management to IoT/Servers; VPN termination; RADIUS/SSH/HTTPS to infrastructure.  
- **Restricted:** No direct access to DMZ management planes; changes require admin role.  
- **Monitoring:** Auth/logon failures generate alerts; firewall rule changes logged.

### VLAN 20 – IoT (192.168.20.0/24)
- **Allowed:** HTTP/HTTPS/DNS/NTP to internet; vendor cloud endpoints; ping to gateway.  
- **Blocked:** All RFC1918 destinations; lateral IoT-to-IoT; access to management interfaces; SMB/SSH by default.  
- **Monitoring:** Inline IPS; anomaly alerts for unexpected protocols or volumes.

### VLAN 30 – Guest (192.168.30.0/24)
- **Allowed:** HTTP/HTTPS/DNS to internet; captive portal auth; bandwidth limits per client.  
- **Blocked:** All inter-VLAN traffic; peer-to-peer; administrative ports; multicast-to-unicast conversions disabled.  
- **Monitoring:** Portal logs and DNS filtering stats reviewed weekly.

### VLAN 40 – Servers (192.168.40.0/24)
- **Allowed:** East-west traffic within VLAN; management from Trusted; updates (HTTP/HTTPS), DNS, NTP; hypervisor clustering ports.  
- **Blocked:** Direct access from IoT/Guest/DMZ; outbound SMTP except relay; default deny to other VLANs unless documented.  
- **Monitoring:** Syslog/FIM; patch compliance; IPS signature tuning for east-west patterns.

### VLAN 50 – DMZ (192.168.50.0/24)
- **Allowed:** WAN → DMZ web ports; DMZ → WAN updates/DNS/NTP; health checks from Trusted jump host.  
- **Blocked:** All other inter-VLAN traffic; SMB/RDP/SSH inbound from WAN; outbound to internal subnets.  
- **Monitoring:** Full packet capture on incidents; IPS in blocking mode; WAF rules applied at reverse proxy.

### Additional Controls (All VLANs)
- DHCP reservations with MAC validation, uRPF enabled, anti-spoofing, and broadcast control.  
- Default deny for any unspecified inter-VLAN path; exceptions require ticket with business justification and expiry.

---
## 4. IDS/IPS Configuration

- **Engine:** Suricata (inline).  
- **Interfaces:** WAN + DMZ mandatory; optional mirror on Servers for east-west visibility.  
- **Rulesets:** Emerging Threats Open, Malware, Exploit, Scan, Web; local rules for homelab services.  
- **Tuning:** Weekly false-positive review; suppression lists for known-good; performance targets CPU <50%, drop rate <1%.  
- **Updates:** Signatures auto-refresh daily at 03:00; immediate manual pull for high/zero-day CVEs.  
- **Actions:** High severity → drop & alert; Medium → alert; Low → log only; auto-quarantine source for repeated critical hits (>3 in 10 minutes).  
- **Visibility:** Alerts forwarded to syslog/SEIM; dashboards show top talkers, signatures, and destinations.  
- **Validation:** Monthly test using benign eicar-equivalent and nmap scan from Trusted to confirm block and alert paths.

---
## 5. Content Filtering

- **DNS Filtering:** pfBlockerNG/Unbound with threat feeds (malware, phishing, C2, adult, gambling); DNSSEC enabled; safe-search enforcement.  
- **HTTP/HTTPS:** SSL/TLS inspection avoided for privacy; rely on DNS/web reputation lists and IPS web-attack rules.  
- **Guest Network:** Captive portal splash with AUP; ad/malware blocklists; per-client bandwidth shaping.  
- **Reporting:** Weekly block statistics, top blocked domains, and false-positive submissions.

---
## 6. Credential & Access Standards

- **Authentication:** WPA3-Enterprise with RADIUS for Trusted; certificate-based OpenVPN; SSH key-only for servers; controller/UIs require MFA.  
- **Passwords:** Minimum 14 chars, complexity enforced, rotation every 180 days for non-MFA accounts; no shared admin creds—use per-user roles.  
- **Secrets Management:** Store PSKs, VPN files, and admin creds in password manager/vault; PSKs rotated quarterly (IoT) and weekly (Guest portal password).  
- **Account Lifecycle:** Provision via ticket, quarterly review, disable dormant accounts after 45 days inactivity, immediate revocation on device loss.  
- **Access Boundaries:** Admin tasks from Trusted VLAN or VPN only; break-glass credentials sealed/offline with monthly seal checks.  
- **Logging:** RADIUS/VPN/SSH auth logs forwarded centrally; failed login thresholds trigger alert and temporary account lockout.

---
## 7. Incident Response Playbooks

**Activation Criteria:** IPS critical alert, confirmed malware, unauthorized access, or service disruption tied to security event.

### Playbook A – IPS Critical Alert (WAN/DMZ)
1. Acknowledge alert; capture Suricata event payload and source/destination.  
2. Block offending IPs at pfSense alias; enable packet capture for 15 minutes.  
3. Validate service health; if DMZ service targeted, enable WAF rule or temporary geoblock.  
4. Assess scope via logs (VPN, firewall, servers); escalate severity if lateral movement suspected.  
5. After containment, tune rule (suppress/modify) if false positive; document in IPS change log.

### Playbook B – Suspected Credential Compromise
1. Disable affected account and revoke certificates/keys; rotate associated secrets.  
2. Review auth logs (RADIUS/VPN/SSH) for preceding 24 hours; identify access paths.  
3. Force MFA reset and device posture check; scan endpoints for malware.  
4. Restore access with least privilege; monitor for 72 hours.  
5. File incident report with timeline, root cause, and preventive actions.

### Playbook C – Malware/EDR Detection on Server
1. Isolate host via firewall rule (Servers VLAN quarantine tag) and snapshot VM.  
2. Run malware cleanup or reimage from golden template; apply patches.  
3. Review east-west connections and DMZ access from host; reset credentials used.  
4. Validate services in staging before returning to production VLAN.  
5. Update IOC list and share with IPS/DNS filters; close with lessons learned.

### Communication & Escalation
- Severity 1 (active exploitation/data risk): immediate call/text to primary admin; updates every 30 minutes.  
- Severity 2 (contained/high risk): respond within 1 hour; updates hourly.  
- Severity 3 (medium): same-day response; summary in daily log.  
- Post-incident review within 7 days with action items tracked.

---
## 8. Retention & Audit Schedule

| Data Type | Retention | Review Cadence | Notes |
|-----------|-----------|----------------|-------|
| Firewall & IPS logs | 180 days online; archive 1 year | Daily critical review; weekly summary | Syslog to centralized collector; time-synced (NTP) |
| VPN/RADIUS auth logs | 180 days | Weekly anomaly review | Trigger alerts on failed-login thresholds |
| DNS filtering stats | 90 days | Weekly | Track top blocked domains and false positives |
| Configuration backups (pfSense/UniFi) | Daily, retained 30 days; monthly snapshot kept 1 year | Monthly restore test | Stored encrypted offsite and locally |
| Vulnerability scans | 1 year | Monthly scanning; quarterly full review | OpenVAS or equivalent |
| Incident reports & playbooks | 3 years | Post-incident and quarterly table-top check | Stored in secured document repo |
| Change logs (firewall/IPS rules) | 1 year | Weekly diff review | Include requester/approver and rollback plan |

---
## 9. Reporting & Metrics

- **Monthly Metrics:**
  - IPS alerts by severity and interface; mean time to acknowledge (MTTA) and resolve (MTTR).  
  - Blocked inbound/egress attempts (top sources/destinations).  
  - VPN usage (success/fail trends), failed authentications, and MFA enforcement rate.  
  - Patch compliance (% servers up to date), backup success rate, and restore test results.  
  - Content filtering effectiveness (blocked domains/categories, false-positive rate).  
  - Inter-VLAN rule exceptions open vs. closed; average age of temporary rules.

- **Reporting Cadence:**
  - **Weekly:** IPS false-positive tuning notes, DNS/portal block summary, open action items.  
  - **Monthly:** Consolidated security health report to project owner; include KPIs above.  
  - **Quarterly:** Tabletop exercise outcomes, vulnerability trend analysis, and policy updates required.

- **Thresholds & Alerts:**
  - Critical IPS alert unacknowledged >15 minutes triggers escalation.  
  - Backup failure >1 day triggers immediate remediation.  
  - Patch compliance <95% in Servers VLAN prompts expedited maintenance.

---
## 10. Maintenance & Review

- **Weekly:** Log review, IPS tuning, DHCP lease audit, IoT/Guest PSK health checks.  
- **Monthly:** Firewall rule audit, VPN certificate expiry check (60-day warning), restore test, metric publication.  
- **Quarterly:** Full policy review, VLAN segmentation validation, penetration test/light purple-team exercise.  
- **Annual:** Disaster recovery test, identity/access recertification, architecture refresh, and document version bump.

---
**Distribution:** Internal administrators only. Unauthorized disclosure prohibited.
