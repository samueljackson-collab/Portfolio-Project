# Network Security Policies

## Firewall Rule Philosophy
- **Defense in Depth**: WAN edge default deny, inter-VLAN explicit allows, IDS/IPS threat detection, endpoint firewalls on servers/workstations.
- **Zero Trust**: Default deny, least privilege, microsegmentation by VLAN, continuous validation via IDS/IPS.

## Internet Edge (WAN) Rules
- **Default Inbound**: DROP ALL; only ESTABLISHED/RELATED allowed.
- **Default Outbound**: Allow, monitored by IDS/IPS; high-risk ports explicitly blocked.

### Inbound Rules (Internet → LAN)
| Priority | Rule | Source | Destination | Service | Action | Logging | Justification |
|----------|------|--------|-------------|---------|--------|---------|---------------|
| 1 | Allow ESTABLISHED | Any | Any | Any | ACCEPT | No | Return traffic for outbound sessions |
| 2 | Allow RELATED | Any | Any | Any | ACCEPT | No | Support related flows (FTP data, ICMP) |
| 3 | Drop Invalid | Any | Any | Any | DROP | Yes | Remove malformed/attack traffic |
| 999 | Default Deny | Any | Any | Any | DROP | Yes | Enforce closed perimeter |

Notes: No port forwards; VPN disabled by default; Geo-IP blocks high-risk countries; DDoS mitigation via UDMP threat management.

### Outbound Rules (LAN → Internet)
| Priority | Rule | Source | Destination | Service | Action | Logging | Justification |
|----------|------|--------|-------------|---------|--------|---------|---------------|
| 1 | Allow HTTP/S | Any LAN | Any | 80,443 | ACCEPT | No | Web/API access |
| 2 | Allow DNS | Any LAN | Any | 53 | ACCEPT | No | Name resolution |
| 3 | Allow NTP | Any LAN | Any | 123 | ACCEPT | No | Time sync |
| 4 | Block SMB | Any LAN | Any | 139,445 | DROP | Yes | Stop worm/ransomware spread |
| 5 | Block High-Risk Ports | Any LAN | Any | 23,135-139,3389 | DROP | Yes | Close common attack vectors |
| 999 | Allow All Else | Any LAN | Any | Any | ACCEPT | No | Permissive egress with IDS/IPS oversight |

## Inter-VLAN Firewall Rules

### Management VLAN (VLAN 1)
- **Inbound**: Allow ESTABLISHED/RELATED; Allow SSH/HTTPS from Trusted (192.168.10.0/24); Allow HTTP redirect from Trusted; Deny all (log).
- **Outbound**: Allow Internet for updates; Deny all else (log).
- **Rationale**: Restrict admin plane to trusted sources; minimal outbound footprint.

### Trusted VLAN (VLAN 10)
- **Inbound**: Allow ESTABLISHED/RELATED; Allow HTTP/HTTPS/SMB from Servers; Allow SSH from Management; Deny all.
- **Outbound**: Allow Internet; Allow Servers (all); Allow Management (22/80/443); Deny IoT/Guest/Cameras.
- **Rationale**: Full user access to services with isolation from lower-trust zones.

### IoT VLAN (VLAN 20)
- **Inbound**: Allow ESTABLISHED/RELATED; Allow mDNS from Trusted (5353); Allow HA (8123) and Zigbee hub (8099) from Trusted; Deny all.
- **Outbound**: Allow HTTP/HTTPS (80/443) to Internet; Allow DNS 53; Allow NTP 123; Deny all RFC1918; Deny all else.
- **Rationale**: Cloud-only access; prevents lateral movement; allows discovery/control from Trusted only.

### Guest VLAN (VLAN 30)
- **Inbound**: Allow ESTABLISHED/RELATED; Deny all else (no log high volume).
- **Outbound**: Allow HTTP/HTTPS 80/443; Allow DNS 53; Deny all RFC1918; Deny all else.
- **Rationale**: Complete isolation; internet-only service.

### Servers VLAN (VLAN 40)
- **Inbound**: Allow ESTABLISHED/RELATED; Allow SSH from Mgmt/Trusted; Allow HTTP/HTTPS/SMB/NFS from Trusted; Allow Proxmox console 8006 from Trusted; Deny all else.
- **Outbound**: Allow Internet (updates/APIs); Allow Management (SNMP/SSH/HTTPS); Deny IoT/Guest/Cameras unless session initiated.
- **Rationale**: Protect critical services while enabling admin and user access.

### Cameras VLAN (VLAN 50)
- **Inbound**: Allow ESTABLISHED/RELATED; Allow RTSP 554 & HTTP 80 from Servers; Deny all else.
- **Outbound**: Allow to Servers 554/80; Allow DNS 53; Allow NTP 123; Deny Internet; Deny other VLANs.
- **Rationale**: Cameras talk only to NVR; no cloud egress.

## IDS/IPS Configuration
- **Enabled Categories**: Malware, Botnet, Phishing, Exploit, Lateral Movement; Port scanning alerts threshold >100 ports/min; Bandwidth Hogging disabled (handled via QoS).
- **Action Modes**: WAN in Block mode; LAN in Alert mode to reduce false positives.
- **Updates**: Automatic daily at 03:00; weekly version check.
- **Notifications**: Critical immediate push; High email within 15 min; Medium/Low daily digest.

## Content Filtering
- **DNS Strategy**: UDMP forwards to OpenDNS (208.67.222.222 / 208.67.220.220); categories blocked Malware/Phishing/Botnet/Adult (Guest additionally FamilyShield). DNS egress forced to UDMP via firewall (blocks 8.8.8.8/1.1.1.1/DoH/DoT).
- **DPI**: Guest blocks P2P/Torrents/Adult/Gaming; IoT monitored only; Trusted/Servers unfiltered.

## Password & Access Policies
- **UniFi Controller**: SSO only, MFA TOTP, 20+ char admin password in 1Password, session timeout 30 minutes, access limited to Mgmt/Trusted subnets.
- **WiFi Credentials**: Distinct PSKs per SSID (HomeNetwork-5G WPA3, IoT WPA2, Guest WPA2 rotated monthly), stored in 1Password.
- **Infrastructure Access**: SSH key-only where supported; strong fallback passwords; keys stored in 1Password and offline backup.

## Access Review & Logging
- **Weekly**: Review firewall/IDS logs for anomalies.
- **Monthly**: Tune IDS signatures and content filtering.
- **Quarterly**: Full rule/audit review; rotate guest PSK monthly.
- **Annually**: Internal/external security assessment.
- **Retention**: Firewall logs 30d local, 1y archived; IDS alerts 90d local, 1y archived; config changes tracked indefinitely in Git.

## Incident Response Procedures
### Alert Levels
- **Level 1 Informational**: Port scans or blocked malware domains; log only, review weekly.
- **Level 2 Warning**: Repeated auth failures or suspicious outbound; investigate within 1 hour; email notification.
- **Level 3 Critical**: Confirmed malware/unauthorized access; immediate containment, push + email + SMS.

### Containment
- **Device Compromised**: Isolate via switch port/MAC block, capture logs, preserve evidence, rebuild from backup, update rules.
- **VLAN Compromised**: Block inter-VLAN for affected VLAN, allow internet-only for investigation, identify nodes, apply device containment.

### Recovery
1. Restore UDMP config from nightly backup to TrueNAS; validate DHCP scopes, firewall rules, VPN.
2. If switch failed, trunk spare switch to UDMP; apply port profiles from docs.
3. If AP failed, replace with spare; adopt and push SSID profiles.
4. Post-recovery: run AV/EDR scans, update IDS signatures, document lessons learned.

## Compliance & Change Management
- **Change Control**: All firewall/VLAN changes documented in Git with justification.
- **New VLANs/Devices**: Require security review and correct VLAN assignment before onboarding.
- **Audit Schedule**: Monthly rule audit; quarterly security config review; annual external assessment.
- **Metrics**: Weekly top-blocked threats, bandwidth by VLAN, failed login attempts, new devices added.
