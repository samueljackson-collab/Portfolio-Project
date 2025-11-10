# Homelab Firewall Rules Documentation

## Overview
This document outlines all inter-VLAN firewall rules configured on the UniFi Dream Machine Pro. Rules are processed in order from top to bottom (first match wins).

## Rule Processing Order
1. **Management Access Rules** (Rules 1-2)
2. **Trusted Network Rules** (Rules 3-5)
3. **IoT Isolation Rules** (Rules 6-9)
4. **Guest Network Rules** (Rules 10-11)
5. **Lab Network Rules** (Rules 12-14)
6. **Default Deny Rule** (Rule 15 - implicit)

## Firewall Rules Table

| Rule # | Name | Source | Destination | Protocol/Port | Action | Purpose | Logging |
|--------|------|--------|-------------|---------------|--------|---------|---------|
| 1 | Admin Workstations → Management | VLAN 10 (192.168.10.0/24) | VLAN 1 (192.168.1.0/24) | TCP: 22, 443, 8443 | ALLOW | Admin SSH/HTTPS access to network gear | Enabled |
| 2 | Non-Admin → Management Deny | All VLANs (except VLAN 10) | VLAN 1 (192.168.1.0/24) | ANY | DENY | Prevent unauthorized management access | Enabled |
| 3 | Trusted → IoT Control | VLAN 10 (192.168.10.0/24) | VLAN 50 (192.168.50.0/24) | UDP: 5353 (mDNS), TCP: 80, 443 | ALLOW | Control smart home devices | Disabled |
| 4 | Trusted → Lab Access | VLAN 10 (192.168.10.0/24) | VLAN 100 (192.168.100.0/24) | ANY | ALLOW | Access test environments | Enabled |
| 5 | Trusted → Guest Deny | VLAN 10 (192.168.10.0/24) | VLAN 99 (192.168.99.0/24) | ANY | DENY | Prevent access to guest network | Enabled |
| 6 | IoT → Internet Only | VLAN 50 (192.168.50.0/24) | Internet (0.0.0.0/0) | TCP: 80, 443, UDP: 53 | ALLOW | Device cloud connectivity | Disabled |
| 7 | IoT → Management Deny | VLAN 50 (192.168.50.0/24) | VLAN 1 (192.168.1.0/24) | ANY | DENY | Block IoT from management | Enabled |
| 8 | IoT → Trusted Deny | VLAN 50 (192.168.50.0/24) | VLAN 10 (192.168.10.0/24) | ANY | DENY | Prevent IoT lateral movement | Enabled |
| 9 | IoT → Guest/Lab Deny | VLAN 50 (192.168.50.0/24) | VLAN 99, VLAN 100 | ANY | DENY | Complete isolation | Enabled |
| 10 | Guest → Internet | VLAN 99 (192.168.99.0/24) | Internet (0.0.0.0/0) | TCP: 80, 443, UDP: 53 | ALLOW | Internet access for guests | Disabled |
| 11 | Guest → Internal Deny | VLAN 99 (192.168.99.0/24) | 192.168.0.0/16 | ANY | DENY | Complete internal isolation | Enabled |
| 12 | Lab → Internet | VLAN 100 (192.168.100.0/24) | Internet (0.0.0.0/0) | ANY | ALLOW | Internet for testing | Enabled |
| 13 | Lab → Trusted Restricted | VLAN 100 (192.168.100.0/24) | VLAN 10 (192.168.10.0/24) | TCP: 8080, 8443 | ALLOW | Access web services on specific ports | Enabled |
| 14 | Lab → Management/IoT/Guest Deny | VLAN 100 (192.168.100.0/24) | VLAN 1, VLAN 50, VLAN 99 | ANY | DENY | Prevent lab contamination | Enabled |
| 15 | Default Deny All | ANY | ANY | ANY | DENY | Implicit deny-all rule | Enabled |

## Additional Security Controls

### Rate Limiting
- **Guest Network**: 10 Mbps per client
- **Lab Network**: 50 Mbps total (shared among lab devices)
- **IoT Network**: No rate limiting (but monitored for anomalies)

### GeoIP Blocking (WAN Rules)
| Rule | Name | Source | Action | Purpose |
|------|------|--------|--------|---------|
| WAN-1 | High-Risk Countries Block | Countries: RU, CN, KP, IR, SY | DROP | Block traffic from high-risk countries |
| WAN-2 | VPN Countries Allow | Countries: US, CA, GB, DE, NL | ALLOW | Allow traffic from trusted countries |

### Port Forwarding Rules
| Rule | Name | External Port | Internal IP | Internal Port | Protocol | Purpose |
|------|------|---------------|-------------|---------------|----------|---------|
| PF-1 | WireGuard VPN | 51820 | 192.168.1.1 | 51820 | UDP | Remote access VPN |
| PF-2 | SSH Jump Host | 2222 | 192.168.10.10 | 22 | TCP | Proxmox SSH access |

## Rule Maintenance

### Review Schedule
- **Weekly**: Check firewall logs for unusual denied traffic
- **Monthly**: Review and update rules based on new devices/services
- **Quarterly**: Complete rule audit and cleanup

### Adding New Rules
When adding new firewall rules:

1. **Document the requirement** (what service needs access)
2. **Use specific source/destination** (avoid "ANY" when possible)
3. **Specify exact ports** (avoid port ranges unless necessary)
4. **Test the rule** from both source and destination
5. **Update this document** with the new rule

### Troubleshooting Common Issues

**Issue: Device can't reach internet**
- Check Rules 6 (IoT), 10 (Guest), 12 (Lab) for internet access
- Verify device is in correct VLAN
- Check DNS settings (Pi-hole status)

**Issue: Trusted device can't control IoT device**
- Check Rule 3 (Trusted → IoT)
- Verify mDNS reflector is enabled
- Check if IoT device is blocking connections

**Issue: Guest device can access internal resources**
- Check Rule 11 (Guest → Internal Deny)
- Verify guest policy is enabled on SSID
- Test isolation from multiple guest devices

## Log Analysis

### Critical Log Patterns to Monitor
- **Repeated DENY from IoT to Trusted**: Potential compromised IoT device
- **DENY from Guest to Internal**: Normal (expected behavior)
- **ALLOW from Lab to Trusted on non-standard ports**: Potential security issue

### Log Retention
- **Firewall Logs**: 30 days (UniFi Controller)
- **Critical DENY Rules**: 90 days (exported to external SIEM)
- **ALLOW Rules**: 7 days (high volume, reduced retention)

## Emergency Procedures

### Disable All Rules (Maintenance Mode)
```bash
# SSH to UDMP
configure
set system config-temporary disable-firewall
commit
# Remember to re-enable after maintenance!
```

### Block Specific Device Immediately
```bash
# Block device by MAC address
configure
set firewall group mac-group BLOCKED_MACS mac <MAC_ADDRESS>
set firewall name LAN_IN rule 9999 action drop
set firewall name LAN_IN rule 9999 source group mac-group BLOCKED_MACS
commit
```

## Rule Validation Tests

### Regular Testing Schedule
- **Daily**: Automated script tests critical rules
- **Weekly**: Manual test of each ALLOW rule
- **Monthly**: Complete rule set validation

### Test Commands
```bash
# Test Trusted → IoT (Rule 3)
ping -c 2 192.168.50.10  # Should work (if ICMP allowed)
curl -I http://192.168.50.10  # Should work

# Test IoT → Trusted (Rule 8) - Should FAIL
# From IoT device:
ping -c 2 192.168.10.10  # Should fail
```

This firewall configuration implements the principle of least privilege with comprehensive logging and regular validation to maintain network security.
