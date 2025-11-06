# Homelab Firewall Rules Documentation

## Overview
Comprehensive firewall rules configured on UniFi Dream Machine Pro for inter-VLAN security.

## Rule Processing Order
Rules processed top-to-bottom (first match wins):
1. Management Access Rules
2. Trusted Network Rules  
3. IoT Isolation Rules
4. Guest Network Rules
5. Lab Network Rules
6. Default Deny (implicit)

## Firewall Rules Table

| Rule # | Name | Source | Destination | Protocol/Port | Action | Purpose | Logging |
|--------|------|--------|-------------|---------------|--------|---------|---------|
| 1 | Admin Workstations → Management | VLAN 10 | VLAN 1 | TCP: 22,443,8443 | ALLOW | Admin SSH/HTTPS access | Enabled |
| 2 | Non-Admin → Management Deny | All except VLAN 10 | VLAN 1 | ANY | DENY | Prevent unauthorized access | Enabled |
| 3 | Trusted → IoT Control | VLAN 10 | VLAN 50 | UDP: 5353, TCP: 80,443 | ALLOW | Control smart devices | Disabled |
| 4 | Trusted → Lab Access | VLAN 10 | VLAN 100 | ANY | ALLOW | Access test environments | Enabled |
| 5 | Trusted → Guest Deny | VLAN 10 | VLAN 99 | ANY | DENY | Prevent guest access | Enabled |
| 6 | IoT → Internet Only | VLAN 50 | Internet | TCP: 80,443, UDP: 53 | ALLOW | Cloud connectivity | Disabled |
| 7 | IoT → Management Deny | VLAN 50 | VLAN 1 | ANY | DENY | Block IoT from management | Enabled |
| 8 | IoT → Trusted Deny | VLAN 50 | VLAN 10 | ANY | DENY | Prevent lateral movement | Enabled |
| 9 | IoT → Guest/Lab Deny | VLAN 50 | VLAN 99,100 | ANY | DENY | Complete isolation | Enabled |
| 10 | Guest → Internet | VLAN 99 | Internet | TCP: 80,443, UDP: 53 | ALLOW | Internet access | Disabled |
| 11 | Guest → Internal Deny | VLAN 99 | 192.168.0.0/16 | ANY | DENY | Internal isolation | Enabled |
| 12 | Lab → Internet | VLAN 100 | Internet | ANY | ALLOW | Testing internet access | Enabled |
| 13 | Lab → Trusted Restricted | VLAN 100 | VLAN 10 | TCP: 8080,8443 | ALLOW | Web services only | Enabled |
| 14 | Lab → Other Deny | VLAN 100 | VLAN 1,50,99 | ANY | DENY | Prevent contamination | Enabled |
| 15 | Default Deny All | ANY | ANY | ANY | DENY | Implicit deny | Enabled |

## Security Controls

### Rate Limiting
- Guest Network: 10 Mbps per client
- Lab Network: 50 Mbps total

### GeoIP Blocking (WAN)
- Block: RU, CN, KP, IR, SY (high-risk countries)
- Allow: US, CA, GB, DE, NL (trusted countries)

### Port Forwarding
| Rule | External Port | Internal IP | Internal Port | Protocol | Purpose |
|------|---------------|-------------|---------------|----------|---------|
| PF-1 | 51820 | 192.168.1.1 | 51820 | UDP | WireGuard VPN |
| PF-2 | 2222 | 192.168.10.10 | 22 | TCP | Proxmox SSH |

## Maintenance

### Review Schedule
- Weekly: Check firewall logs
- Monthly: Review and update rules
- Quarterly: Complete rule audit

### Adding New Rules
1. Document the requirement
2. Use specific source/destination
3. Specify exact ports
4. Test the rule
5. Update this document

## Troubleshooting

**Device can't reach internet**
- Check Rules 6, 10, 12 for internet access
- Verify device is in correct VLAN
- Check DNS settings

**Trusted device can't control IoT device**
- Check Rule 3 (Trusted → IoT)
- Verify mDNS reflector enabled
- Check if IoT device blocks connections

**Guest device accessing internal resources**
- Check Rule 11 (Guest → Internal Deny)
- Verify guest policy enabled on SSID
- Test isolation from multiple devices

## Emergency Procedures

### Disable All Rules (Maintenance)
```bash
# SSH to UDMP
configure
set system config-temporary disable-firewall
commit
```

### Block Device Immediately
```bash
configure
set firewall group mac-group BLOCKED_MACS mac <MAC_ADDRESS>
set firewall name LAN_IN rule 9999 action drop
set firewall name LAN_IN rule 9999 source group mac-group BLOCKED_MACS
commit
```

For complete documentation with test procedures and log analysis, see the full firewall rules reference.
