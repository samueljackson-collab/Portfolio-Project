# Network Security Policies

## Firewall Rule Philosophy
- Defense in depth: WAN edge blocks inbound, inter-VLAN default deny, IDS/IPS inspection.
- Zero trust: least privilege, segmentation, continuous validation.

## Internet Edge (WAN) Rules
Inbound: default DROP; allow ESTABLISHED/RELATED; drop invalid; no port forwards. DDoS and geo-filtering enabled on UDMP.
Outbound: allow HTTP/S, DNS, NTP; block SMB and risky ports (23,135-139,445,3389); IDS/IPS monitors rest.

## Inter-VLAN Rules Summary
- Management (VLAN1): inbound SSH/HTTPS from Trusted; outbound updates only.
- Trusted (VLAN10): full access to Servers/Management; denied to IoT/Guest/Cameras.
- IoT (VLAN20): outbound HTTP/S, DNS, NTP; inbound mDNS and specific control ports from Trusted; no RFC1918 outbound.
- Servers (VLAN40): inbound SSH/HTTPS/SMB/NFS from Trusted/Management; outbound updates and monitoring.
- Guest (VLAN30): Internet-only; RFC1918 blocked; client isolation enforced.
- Cameras (VLAN50): inbound RTSP/HTTP from Servers; outbound DNS/NTP only; Internet denied.

## IDS/IPS
- Categories enabled: malware, botnet, phishing, exploit, lateral movement; port scan alert threshold >100 ports/min.
- WAN in block mode; LAN in alert mode to reduce false positives.
- Signature updates daily at 03:00 with weekly version review.

## Content Filtering
- DNS via OpenDNS Home; UDMP forwards and firewall blocks direct DNS to public resolvers.
- Guest VLAN uses FamilyShield; P2P/torrent DPI blocked.
- IoT monitored only; Trusted/Servers unfiltered.

## Password & Access Policies
- UniFi admin with 20+ char password, MFA enabled, SSO preferred.
- SSH key auth for infrastructure devices; password auth disabled.
- WiFi keys unique per SSID: WPA3 trusted, WPA2 IoT/Guest; stored in 1Password; Guest rotated monthly.

## Incident Response Procedures
- Alert levels: informational (log), warning (investigate within hour), critical (immediate containment).
- Containment: isolate device or VLAN, capture evidence, remediate then restore.
- Recovery: nightly UDMP config backups to TrueNAS; restore via controller import, validate rules post-restore.

## Compliance & Audit
- Logs: firewall 30d, IDS 90d, archived 1y to TrueNAS.
- Change management: document firewall/VLAN changes in git repo; quarterly security review; annual internal pen test.
- Metrics: weekly security report (top threats, destinations, bandwidth by VLAN, failed logins, new devices); monthly executive summary of incidents and policy changes.
