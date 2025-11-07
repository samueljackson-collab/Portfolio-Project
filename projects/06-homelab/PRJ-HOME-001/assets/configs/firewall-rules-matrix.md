# Firewall Rules Matrix
# =====================
# Complete firewall rules configuration for homelab network
# Platform: pfSense / UniFi Security Gateway
# All IPs are examples from RFC 1918 private ranges

## VLAN Configuration

| VLAN ID | Name | Subnet | Gateway | Purpose |
|---------|------|--------|---------|---------|
| 1 | Management | 192.168.1.0/24 | 192.168.1.1 | Network infrastructure management |
| 10 | Trusted | 192.168.10.0/24 | 192.168.10.1 | Trusted devices (workstations, servers) |
| 20 | IoT | 192.168.20.0/24 | 192.168.20.1 | IoT devices (smart home, cameras) |
| 30 | Guest | 192.168.30.0/24 | 192.168.30.1 | Guest wireless access |
| 99 | Quarantine | 192.168.99.0/24 | 192.168.99.1 | Isolated/untrusted devices |

## Inter-VLAN Firewall Rules

### Management VLAN (VLAN 1) → All VLANs
**Policy:** Allow all (admin access)

| Rule # | Source | Destination | Ports | Protocol | Action | Description |
|--------|--------|-------------|-------|----------|--------|-------------|
| M-001 | 192.168.1.0/24 | Any | Any | Any | Allow | Full admin access from management VLAN |
| M-002 | Any | 192.168.1.0/24 | 22,80,443 | TCP | Allow | SSH/Web access to network gear |
| M-003 | Any | 192.168.1.0/24 | Any | Any | Deny | Block unsolicited traffic to management |

---

### Trusted VLAN (VLAN 10) Rules

#### Trusted → Internet
| Rule # | Source | Destination | Ports | Protocol | Action | Description |
|--------|--------|-------------|-------|----------|--------|-------------|
| T-001 | 192.168.10.0/24 | Any (Internet) | 80,443 | TCP | Allow | Web browsing |
| T-002 | 192.168.10.0/24 | Any (Internet) | 53 | UDP/TCP | Allow | DNS queries |
| T-003 | 192.168.10.0/24 | Any (Internet) | 587,465,993,995 | TCP | Allow | Email (SMTP/IMAP) |
| T-004 | 192.168.10.0/24 | Any (Internet) | 22,3389 | TCP | Allow | SSH/RDP to external hosts |

#### Trusted → IoT
| Rule # | Source | Destination | Ports | Protocol | Action | Description |
|--------|--------|-------------|-------|----------|--------|-------------|
| T-101 | 192.168.10.0/24 | 192.168.20.0/24 | 80,443 | TCP | Allow | Web interface access to IoT devices |
| T-102 | 192.168.10.0/24 | 192.168.20.0/24 | 8123 | TCP | Allow | Home Assistant |
| T-103 | 192.168.10.0/24 | 192.168.20.0/24 | 1883,8883 | TCP | Allow | MQTT (plain and SSL) |

#### Trusted → Management (limited)
| Rule # | Source | Destination | Ports | Protocol | Action | Description |
|--------|--------|-------------|-------|----------|--------|-------------|
| T-201 | 192.168.10.100 | 192.168.1.0/24 | 22 | TCP | Allow | Admin workstation SSH to network gear |
| T-202 | 192.168.10.100 | 192.168.1.0/24 | 443 | TCP | Allow | Admin workstation HTTPS to network gear |
| T-203 | 192.168.10.0/24 | 192.168.1.0/24 | Any | Any | Deny | Block other traffic to management |

---

### IoT VLAN (VLAN 20) Rules

#### IoT → Internet
| Rule # | Source | Destination | Ports | Protocol | Action | Description |
|--------|--------|-------------|-------|----------|--------|-------------|
| I-001 | 192.168.20.0/24 | Any (Internet) | 80,443 | TCP | Allow | Cloud service connectivity |
| I-002 | 192.168.20.0/24 | Any (Internet) | 53 | UDP | Allow | DNS queries |
| I-003 | 192.168.20.0/24 | Any (Internet) | 123 | UDP | Allow | NTP time sync |

#### IoT → Trusted (very limited)
| Rule # | Source | Destination | Ports | Protocol | Action | Description |
|--------|--------|-------------|-------|----------|--------|-------------|
| I-101 | 192.168.20.0/24 | 192.168.10.101 | 8123 | TCP | Allow | IoT devices to Home Assistant |
| I-102 | 192.168.20.0/24 | 192.168.10.102 | 1883 | TCP | Allow | IoT devices to MQTT broker |
| I-103 | 192.168.20.0/24 | 192.168.10.0/24 | Any | Any | Deny | Block other traffic to trusted |

#### IoT → IoT
| Rule # | Source | Destination | Ports | Protocol | Action | Description |
|--------|--------|-------------|-------|----------|--------|-------------|
| I-201 | 192.168.20.0/24 | 192.168.20.0/24 | Any | Any | Allow | IoT devices can communicate with each other |

#### IoT → All Other VLANs
| Rule # | Source | Destination | Ports | Protocol | Action | Description |
|--------|--------|-------------|-------|----------|--------|-------------|
| I-999 | 192.168.20.0/24 | 192.168.0.0/16 | Any | Any | Deny | Block IoT from accessing other VLANs |

---

### Guest VLAN (VLAN 30) Rules

#### Guest → Internet ONLY
| Rule # | Source | Destination | Ports | Protocol | Action | Description |
|--------|--------|-------------|-------|----------|--------|-------------|
| G-001 | 192.168.30.0/24 | Any (Internet) | 80,443 | TCP | Allow | Web browsing |
| G-002 | 192.168.30.0/24 | Any (Internet) | 53 | UDP | Allow | DNS queries |
| G-003 | 192.168.30.0/24 | 192.168.0.0/16 | Any | Any | Deny | Block access to internal networks |
| G-004 | 192.168.30.0/24 | 10.0.0.0/8 | Any | Any | Deny | Block access to internal networks |
| G-005 | 192.168.30.0/24 | 172.16.0.0/12 | Any | Any | Deny | Block access to internal networks |

---

### Quarantine VLAN (VLAN 99) Rules

#### Quarantine → Internet (DNS/Web only)
| Rule # | Source | Destination | Ports | Protocol | Action | Description |
|--------|--------|-------------|-------|----------|--------|-------------|
| Q-001 | 192.168.99.0/24 | 192.168.10.2 | 53 | UDP | Allow | DNS to internal Pi-hole only |
| Q-002 | 192.168.99.0/24 | Any (Internet) | 80,443 | TCP | Allow | Web for updates/registration |
| Q-003 | 192.168.99.0/24 | Any | Any | Any | Deny | Block everything else |

---

## Service Access Rules

### SSH Access
| Rule # | Source | Destination | Ports | Protocol | Action | Description |
|--------|--------|-------------|-------|----------|--------|-------------|
| S-001 | 192.168.10.100 | 192.168.10.0/24 | 22 | TCP | Allow | Admin workstation to all trusted servers |
| S-002 | 192.168.1.0/24 | Any | 22 | TCP | Allow | Management VLAN can SSH anywhere |
| S-003 | Any | Any | 22 | TCP | Deny | Block SSH from other sources |

### DNS (Pi-hole)
| Rule # | Source | Destination | Ports | Protocol | Action | Description |
|--------|--------|-------------|-------|----------|--------|-------------|
| S-101 | 192.168.0.0/16 | 192.168.10.2 | 53 | UDP/TCP | Allow | All internal networks to Pi-hole |
| S-102 | Any | Any | 53 | UDP/TCP | Deny | Block external DNS (force through Pi-hole) |

### Web Services
| Rule # | Source | Destination | Ports | Protocol | Action | Description |
|--------|--------|-------------|-------|----------|--------|-------------|
| S-201 | 192.168.10.0/24 | 192.168.10.100-110 | 80,443 | TCP | Allow | Access to internal web services |
| S-202 | 192.168.10.0/24 | 192.168.10.103 | 3000 | TCP | Allow | Grafana dashboards |
| S-203 | 192.168.10.0/24 | 192.168.10.103 | 9090 | TCP | Allow | Prometheus |

---

## Intrusion Prevention (IPS/IDS)

### Suricata Rules Enabled
- **ET Open Ruleset**: Emerging Threats
- **Snort VRT**: Vulnerability Research Team rules
- **Custom Rules**: Homelab-specific threat signatures

### IPS Mode: Inline
- Block on detection: Enabled
- Alert on detection: Enabled (send to syslog)
- Monitored interfaces: WAN, Trusted, IoT

### IPS Categories Enabled
- Malware
- Exploit Kits
- Phishing
- Command & Control
- Data Exfiltration
- Brute Force Attacks

---

## NAT Rules (WAN)

### Port Forwarding (Inbound)
| Rule # | WAN Port | Internal IP | Internal Port | Protocol | Description |
|--------|----------|-------------|---------------|----------|-------------|
| N-001 | NONE | NONE | NONE | NONE | No inbound port forwarding (reverse proxy only) |

**Note:** All external access goes through Cloudflare Tunnel / reverse proxy, no direct port forwarding

### Outbound NAT
- Mode: Automatic (hybrid)
- Source NAT: Enabled for all internal VLANs
- Preserve source port: Enabled

---

## Traffic Shaping / QoS

### Priority Classes
1. **High Priority** (VoIP, Video Conferencing)
   - Ports: 3478-3497 (WebRTC), 5060 (SIP)
   - Guaranteed: 30% bandwidth
   - Max: 80%

2. **Medium Priority** (HTTP/HTTPS, DNS)
   - Ports: 80, 443, 53
   - Guaranteed: 50% bandwidth
   - Max: 95%

3. **Low Priority** (Bulk Downloads, P2P)
   - Ports: BitTorrent, FTP
   - Guaranteed: 10% bandwidth
   - Max: 40%

---

## Logging & Monitoring

### Firewall Logging
- **Logged Events:**
  - All denied connections (default deny)
  - All allowed connections from untrusted VLANs (IoT, Guest, Quarantine)
  - Rule matches for critical services (SSH, RDP, etc.)

- **Log Destinations:**
  - Local: /var/log/firewall.log (7 day retention)
  - Remote Syslog: 192.168.10.103:514 (Loki/Grafana)

### Alert Thresholds
- Connection rate > 1000/sec: Alert
- Blocked connection attempts > 100/min from single IP: Alert
- IPS rule matches: Alert immediately

---

## Default Policies

### Implicit Deny
All traffic not explicitly allowed is denied and logged.

### Anti-Lockout Rule
Management VLAN (192.168.1.0/24) always has access to firewall web interface and SSH to prevent lockout.

### Bogon Networks
Block traffic from/to bogon networks (RFC 1918, multicast, etc.) on WAN interface.

---

## Maintenance Windows

### Rule Review Schedule
- Weekly: Review firewall logs for anomalies
- Monthly: Review and optimize rules
- Quarterly: Full security audit

### Change Control
- All rule changes require:
  1. Documentation of reason
  2. Testing in lab environment (if possible)
  3. Backup of current configuration
  4. Rollback plan

---

## Notes

- All IP addresses are examples from RFC 1918 private ranges
- Adjust to match your actual network topology
- Always test changes in a lab before production
- Keep firewall firmware up to date
- Regular backups of firewall configuration

## Configuration Files

- pfSense: Diagnostics > Backup & Restore
- UniFi: Settings > System > Backup
- Store encrypted backups offsite

---

**Last Updated:** 2024-11-06
**Maintained By:** Network Infrastructure Team
