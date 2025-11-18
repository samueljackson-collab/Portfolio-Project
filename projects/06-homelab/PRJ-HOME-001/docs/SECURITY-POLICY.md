# Network Security Policies

## Firewall Philosophy
- Default deny between VLANs; explicit allows documented in inter-VLAN matrix.
- Defense in depth: WAN drop inbound, IDS/IPS on UDMP, VLAN isolation, endpoint firewalls.
- Zero trust posture for IoT/Guest/Cameras; only required flows permitted.

## WAN Rules
- Inbound: drop all except established/related and invalid drop; VPN adds explicit rule when enabled.
- Outbound: allow HTTP/S, DNS, NTP; block SMB and high-risk ports (23,135-139,445,3389) with logging.

## Inter-VLAN Rules (Highlights)
- **Management** inbound: SSH/HTTPS from Trusted only; deny all others; outbound firmware updates allowed.
- **Trusted** outbound: allow to Servers/Management; deny to IoT/Guest/Cameras except via specific services.
- **IoT** outbound: HTTP/S + DNS/NTP; RFC1918 blocked; inbound only mDNS/control ports from Trusted.
- **Servers** inbound: SSH from Management/Trusted; HTTP/S/SMB/NFS from Trusted; deny IoT/Guest/Cameras.
- **Guest**: Internet only; client isolation; RFC1918 blocked.
- **Cameras**: Allow RTSP/HTTP to Servers; deny internet and other VLANs.

## IDS/IPS
- Categories enabled: malware, botnet, phishing, exploit, lateral movement; port scan detection threshold enabled.
- WAN interface in block mode; LAN in alert mode to reduce false positives.
- Automatic signature updates daily at 03:00; weekly review of alerts and tuning.

## DNS Filtering
- UDMP forwards to OpenDNS (208.67.222.222/220.220); firewall blocks external DNS to prevent bypass; DoH/DoT destinations blocked.
- Guest VLAN uses FamilyShield for family-friendly filtering.

## Access Controls
- UniFi admin accounts require MFA and 20+ character passwords; session timeout 30 minutes.
- SSH to infrastructure uses key-based auth; passwords disabled where possible.
- WiFi passphrases rotated: Guest monthly, IoT quarterly, Trusted annually or upon staff change.

## Incident Response
- Severity levels: informational (logged), warning (email within 1h), critical (push+SMS immediate).
- Containment: isolate device by switch port shutdown or VLAN ACL; preserve logs; rebuild compromised hosts from backup.
- Recovery: restore UDMP config from nightly backup; retest firewall rules; document lessons learned in change log.

## Compliance & Audit
- Firewall and IDS logs retained 30 days on UDMP; archived to TrueNAS for 1 year.
- Quarterly security review covering firewall rules, VPN access, and password rotations.
- Annual penetration test planned; results tracked in risk register.
