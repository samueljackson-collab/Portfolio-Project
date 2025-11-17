# Network Security Policies

## Firewall Rule Philosophy
- Defense in depth: WAN edge drop inbound, inter-VLAN default deny, IDS/IPS inspection, endpoint firewalls.
- Zero trust: least privilege, microsegmentation, continuous monitoring.

## Internet Edge (WAN) Rules
**Inbound**: drop all; allow ESTABLISHED/RELATED; drop invalid. No port forwards. VPN access only via UniFi when enabled.
**Outbound**: allow HTTP/HTTPS/DNS/NTP; block SMB and high-risk ports (23,135-139,445,3389); default allow monitored via IDS/IPS.

## Inter-VLAN Rules (summarized)
- Management inbound: allow SSH/HTTPS from Trusted; deny all else.
- Trusted outbound: allow Internet, Servers, Management; deny IoT/Guest/Cameras.
- IoT outbound: HTTP/HTTPS, DNS, NTP; block RFC1918; allow mDNS from Trusted for discovery.
- Servers inbound: allow SSH from Mgmt/Trusted, HTTP/S, SMB/NFS, Proxmox console; deny IoT/Guest.
- Guest: Internet only; RFC1918 blocked.
- Cameras: allow RTSP/HTTP to Servers (NVR); deny Internet and other VLANs except DNS/NTP.

## IDS/IPS Configuration
- Categories enabled: malware, botnet, phishing, exploit, lateral movement; port scan with threshold.
- WAN: block mode; LAN: alert mode.
- Signature updates daily 03:00; weekly engine version check.
- Notifications: critical immediate (push/SMS), high via email within 15m, medium/low aggregated daily.

## Content Filtering
- DNS: OpenDNS for all VLANs, FamilyShield for Guest; firewall blocks external DNS and DoH/DoT endpoints.
- DPI: Guest blocks P2P/torrents/gaming; IoT monitored only.
- Overrides: Trusted/Servers unfiltered for flexibility.

## Password & Access Policies
- UniFi admin strong password (20+ chars) with MFA; cloud SSO preferred.
- WiFi PSKs unique per SSID; stored in 1Password; guest rotated monthly.
- Infrastructure SSH key-based auth; passwords disabled where possible.
- Access reviews: weekly firewall log review, monthly IDS/IPS tuning, quarterly full audit, annual pen-test.

## Incident Response
- Levels: Informational (log), Warning (investigate within hour), Critical (isolate device/VLAN immediately).
- Containment: block MAC at switch, isolate VLAN, capture evidence before remediation.
- Recovery: nightly UDMP config backup to NAS; restore via UniFi UI/import.

## Compliance & Audit
- Retention: firewall logs 30d on UDMP + 1y archive; IDS alerts 90d + 1y archive; config changes versioned in Git.
- Change management: all firewall/VLAN changes documented; new devices assigned to correct VLAN with record.
- Metrics: weekly security report (blocked threats, top destinations, bandwidth by VLAN, failed logins, new devices) and monthly executive summary.
