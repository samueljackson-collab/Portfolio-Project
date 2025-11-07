# Firewall Policy Matrix

## Default Policy: Deny All

All traffic between VLANs is denied by default. Only explicitly allowed traffic is permitted.

## Inter-VLAN Traffic Rules

### Source: VLAN 10 (Trusted)

| Destination | Protocol/Port | Action | Purpose | Notes |
|-------------|---------------|--------|---------|-------|
| VLAN 30 (Management) | TCP 22 | ALLOW | SSH to network equipment | Admin access only |
| VLAN 30 (Management) | TCP 443, 8443 | ALLOW | HTTPS to UDMP/switches | Management UI |
| VLAN 50 (IoT) | TCP 80, 443 | ALLOW | Access IoT device web interfaces | Limited access |
| VLAN 50 (IoT) | TCP 8123 | ALLOW | Home Assistant access | |
| VLAN 50 (IoT) | UDP 5353 (mDNS) | ALLOW | Service discovery | |
| VLAN 99 (Guest) | ALL | DENY | No guest network access | Security isolation |
| Internet (WAN) | ALL | ALLOW | Full internet access | Trusted users |

### Source: VLAN 30 (Management)

| Destination | Protocol/Port | Action | Purpose | Notes |
|-------------|---------------|--------|---------|-------|
| VLAN 10 (Trusted) | ALL | DENY | Management isolation | Admin access via VLAN 10 only |
| VLAN 50 (IoT) | ALL | DENY | Complete isolation | |
| VLAN 99 (Guest) | ALL | DENY | Complete isolation | |
| Internet (WAN) | TCP 80, 443 | ALLOW | Firmware updates | Equipment updates only |

### Source: VLAN 50 (IoT)

| Destination | Protocol/Port | Action | Purpose | Notes |
|-------------|---------------|--------|---------|-------|
| VLAN 10 (Trusted) | ALL | DENY | IoT cannot initiate to trusted | Prevent IoT compromise spread |
| VLAN 30 (Management) | ALL | DENY | Complete isolation | |
| VLAN 99 (Guest) | ALL | DENY | Complete isolation | |
| Internet (WAN) | TCP 80, 443 | ALLOW | Cloud services | Required for IoT functionality |
| Internet (WAN) | UDP 53 | ALLOW | DNS queries | |
| Internet (WAN) | UDP 123 | ALLOW | NTP time sync | |
| Internet (WAN) | Other | DENY | Limit attack surface | |

### Source: VLAN 99 (Guest)

| Destination | Protocol/Port | Action | Purpose | Notes |
|-------------|---------------|--------|---------|-------|
| VLAN 10 (Trusted) | ALL | DENY | Complete internal isolation | |
| VLAN 30 (Management) | ALL | DENY | Complete internal isolation | |
| VLAN 50 (IoT) | ALL | DENY | Complete internal isolation | |
| Internet (WAN) | TCP 80, 443 | ALLOW | Web browsing | Basic internet access |
| Internet (WAN) | UDP 53 | ALLOW | DNS queries | |
| Guest VLAN clients | ALL | DENY | Client isolation enabled | Prevent guest-to-guest attacks |

## Inbound WAN Rules

| Service | External Port | Internal IP | Internal Port | Protocol | Notes |
|---------|---------------|-------------|---------------|----------|-------|
| WireGuard VPN | 51820 | 192.168.30.1 | 51820 | UDP | Secure remote access |
| HTTPS (Nginx Proxy) | 443 | 192.168.10.25 | 443 | TCP | Reverse proxy for services |
| HTTP (Nginx Proxy) | 80 | 192.168.10.25 | 80 | TCP | HTTP to HTTPS redirect |

### VPN Access Rules

When connected via WireGuard VPN:
- Access to VLAN 10 (Trusted): FULL
- Access to VLAN 30 (Management): FULL
- Access to VLAN 50 (IoT): READ-ONLY
- Access to VLAN 99 (Guest): DENY

## Special Rules

### DHCP/DNS Services

| Source | Destination | Protocol/Port | Action | Purpose |
|--------|-------------|---------------|--------|---------|
| ALL VLANs | 192.168.*.1 | UDP 67 (DHCP) | ALLOW | IP address assignment |
| ALL VLANs | 192.168.*.1 | UDP 53 (DNS) | ALLOW | Name resolution |

### NTP Services

| Source | Destination | Protocol/Port | Action | Purpose |
|--------|-------------|---------------|--------|---------|
| ALL VLANs | NTP Pool | UDP 123 | ALLOW | Time synchronization |

### Established/Related Traffic

All VLANs can receive responses to their outbound connections (stateful firewall).

## Security Policies

### GeoIP Blocking

- **Enabled:** Yes
- **Blocked Regions:** Russia, China, North Korea, Iran, known high-risk ASNs
- **Action:** DROP at WAN interface
- **Whitelist:** VPN connections exempt

### Intrusion Prevention System (IPS)

- **Enabled:** Yes (UDMP Threat Management)
- **Detection Level:** Medium
- **Blocked Categories:**
  - Malware downloads
  - Exploit attempts
  - Phishing sites
  - Known malicious IPs
  - Tor exit nodes (optional)

### Rate Limiting

| Service | Rate Limit | Purpose |
|---------|------------|---------|
| SSH (all sources) | 5 attempts/minute | Prevent brute force |
| HTTPS (WAN) | 100 requests/second | DDoS mitigation |
| DNS (external queries) | 50 queries/second | DNS amplification prevention |

### DPI (Deep Packet Inspection)

- **Enabled:** Yes
- **Actions:**
  - Block known P2P protocols on Guest VLAN
  - Monitor but allow encrypted traffic
  - Alert on unusual traffic patterns

## Firewall Logging

### Logged Events

- All DENY rules (for security monitoring)
- VPN connection attempts
- WAN inbound connection attempts
- IPS alerts
- Failed authentication attempts

### Log Retention

- **Duration:** 30 days
- **Storage:** Local UDMP + forwarded to Loki
- **Review Frequency:** Weekly

## Firewall Rule Maintenance

### Review Schedule

- **Daily:** Check IPS alerts for new threats
- **Weekly:** Review deny logs for false positives
- **Monthly:** Audit all firewall rules for necessity
- **Quarterly:** Penetration test from WAN and each VLAN

### Change Management

All firewall rule changes must:
1. Document business justification
2. Test in lab environment first (if possible)
3. Implement during maintenance window
4. Monitor for 24 hours post-change
5. Update this documentation

## Firewall Performance

### Current Throughput

- **WAN to LAN:** ~1 Gbps (line rate)
- **Inter-VLAN:** ~1 Gbps (hardware switching)
- **VPN:** ~500 Mbps (CPU limited)
- **IPS Enabled:** ~850 Mbps

### Capacity Planning

- Current utilization: <20% average
- Alert threshold: >70% sustained
- Upgrade trigger: >80% peak for 30 days
