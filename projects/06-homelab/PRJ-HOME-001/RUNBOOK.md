# PRJ-HOME-001: Homelab & Secure Network Build - Operations Runbook

**Version:** 1.0
**Last Updated:** November 10, 2025
**Maintainer:** Samuel Jackson
**Project Status:** ✅ Completed

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Reference](#quick-reference)
3. [Detailed Runbooks](#detailed-runbooks)
4. [Common Operations](#common-operations)
5. [Emergency Procedures](#emergency-procedures)
6. [Maintenance Schedule](#maintenance-schedule)

---

## Overview

### Purpose
This runbook provides comprehensive operational procedures for managing the homelab network infrastructure including pfSense firewall, UniFi networking equipment, VLAN segmentation, and security controls.

### Scope
- **Firewall:** pfSense with Suricata IPS
- **Switching:** UniFi Switch 24 POE
- **Wireless:** 2x UniFi U6 Pro Access Points
- **Network Segments:** 5 VLANs (Trusted, IoT, Guest, Servers, DMZ)
- **Security:** WPA3 Enterprise, OpenVPN, IPS

### Service Level Objectives
- **Availability:** 99.9% uptime
- **RTO (Recovery Time Objective):** 30 minutes
- **RPO (Recovery Point Objective):** 24 hours
- **Incident Response Time:** <10 minutes for critical issues

---

## Quick Reference

### Critical Contact Information
- **Primary Admin:** Samuel Jackson
- **Documentation:** `/projects/06-homelab/PRJ-HOME-001/README.md`
- **Backup Location:** TrueNAS `/mnt/backups/network/`

### Network Access Points
| System | IP Address | Port | Credentials Location |
|--------|------------|------|---------------------|
| pfSense WebGUI | 192.168.1.1 | 443 | Password Manager |
| UniFi Controller | 192.168.1.2 | 8443 | Password Manager |
| Suricata IPS | 192.168.1.1 | 443 | Via pfSense GUI |

### VLAN Quick Reference
| VLAN | Network | Purpose | Gateway | DHCP Range |
|------|---------|---------|---------|------------|
| 10 | 192.168.1.0/24 | Trusted | 192.168.1.1 | 192.168.1.50-200 |
| 20 | 192.168.20.0/24 | IoT | 192.168.20.1 | 192.168.20.50-200 |
| 30 | 192.168.30.0/24 | Guest | 192.168.30.1 | 192.168.30.50-200 |
| 40 | 192.168.40.0/24 | Servers | 192.168.40.1 | 192.168.40.50-100 |
| 50 | 192.168.50.0/24 | DMZ | 192.168.50.1 | 192.168.50.50-100 |

### Critical Services Status Check
```bash
# pfSense Console Commands
# Check firewall status
pfctl -s info

# Check interface status
ifconfig

# Test DNS resolution
dig @192.168.1.1 google.com

# Check DHCP leases
dhcpd -T
```

---

## Detailed Runbooks

This project includes several comprehensive runbooks located in `assets/runbooks/`:

### 1. Network Operations Runbook
**Location:** `assets/runbooks/NETWORK_OPERATIONS_RUNBOOK.md`

**Covers:**
- Complete network outage response
- VLAN connectivity troubleshooting
- Wireless network issues
- Security incident response (Suricata IPS alerts)
- DNS, DHCP, and VPN troubleshooting
- Maintenance procedures
- Emergency recovery procedures

**Use When:**
- Network services are down or degraded
- Security alerts require investigation
- Performing routine maintenance
- Troubleshooting connectivity issues

### 2. Network Deployment Runbook
**Location:** `assets/runbooks/network-deployment-runbook.md`

**Covers:**
- Initial hardware installation
- UDMP/pfSense configuration from scratch
- VLAN creation and configuration
- Wi-Fi SSID setup
- Firewall rules implementation
- Static IP and DHCP reservations
- DNS configuration with Pi-hole
- VPN setup (WireGuard/OpenVPN)

**Use When:**
- Deploying network from scratch
- Rebuilding after hardware failure
- Replicating network in new location
- Training new administrators

---

## Common Operations

### Daily Operations

#### 1. Check System Health
```bash
# Via pfSense WebGUI
# 1. Navigate to Status → Dashboard
# 2. Verify all interface states show "up"
# 3. Check CPU/Memory usage (<80%)
# 4. Review recent alerts

# Via SSH
ssh admin@192.168.1.1
pfctl -s info           # Firewall status
top                     # Resource usage
netstat -i              # Interface statistics
```

#### 2. Monitor Suricata IPS Alerts
```bash
# Via pfSense WebGUI
# Services → Suricata → Alerts
# 1. Review alerts from last 24 hours
# 2. Investigate Priority 1 (Critical) alerts immediately
# 3. Document false positives
# 4. Update suppression rules as needed
```

#### 3. Review Backup Status
```bash
# Verify daily configuration backup completed
# Diagnostics → Backup & Restore → Config History
# Confirm: Latest backup dated today
# Action: Download weekly backup for offsite storage
```

### Weekly Operations

#### 1. Firewall Log Review
```bash
# Status → System Logs → Firewall
# Look for:
# - Unusual blocked traffic patterns
# - Failed authentication attempts
# - Port scan activity
# - Unexpected inter-VLAN traffic
```

#### 2. DHCP Lease Review
```bash
# Status → DHCP Leases
# 1. Check for lease exhaustion (>90% used)
# 2. Identify unknown devices
# 3. Create static reservations for servers
# 4. Remove stale leases from decommissioned devices
```

#### 3. Update IPS Signatures
```bash
# Services → Suricata → Updates
# 1. Click "Update Rules"
# 2. Wait for completion (~5 minutes)
# 3. Restart Suricata interfaces
# 4. Verify: Check logs for successful update
```

### Monthly Operations

#### 1. Apply Security Updates
**See:** `assets/runbooks/NETWORK_OPERATIONS_RUNBOOK.md` → Maintenance Procedures → Performing pfSense Updates

```bash
# System → Update → System Update
# 1. Backup configuration first
# 2. Review release notes
# 3. Apply updates (5-10 minute downtime)
# 4. Verify all services restart correctly
# 5. Test connectivity from each VLAN
```

#### 2. Firewall Rule Audit
```bash
# Firewall → Rules → All interfaces
# For each rule:
# 1. Check last hit timestamp
# 2. Remove rules not hit in >90 days
# 3. Verify rule descriptions are clear
# 4. Ensure logging is enabled on critical rules
# 5. Test that blocks are working as expected
```

#### 3. Test VPN Connectivity
```bash
# From external network (mobile hotspot):
# 1. Connect with OpenVPN client
# 2. Verify can ping internal resources
# 3. Test access to services (SSH, HTTPS)
# 4. Disconnect and verify no access
# 5. Review VPN logs for errors
```

### Quarterly Operations

#### 1. Disaster Recovery Test
**See:** `assets/runbooks/NETWORK_OPERATIONS_RUNBOOK.md` → Emergency Recovery

```bash
# Full DR test procedure:
# 1. Prepare spare hardware or VM
# 2. Download latest config backup
# 3. Install pfSense from scratch
# 4. Restore configuration
# 5. Verify all services operational
# 6. Document any issues
# Time: 1-2 hours
```

#### 2. Security Penetration Test
```bash
# From external network or testing VLAN:
# 1. Run Nmap scan against WAN IP
# 2. Test port forwarding rules
# 3. Attempt SQL injection on exposed services
# 4. Test wireless authentication bypass
# 5. Document findings and remediate
```

#### 3. Network Performance Baseline
```bash
# Run iperf3 tests between VLANs
iperf3 -s  # On server VLAN 40
iperf3 -c 192.168.40.10  # From trusted VLAN 10

# Expected: 900+ Mbps within same switch
# Document: Compare to previous quarters
```

---

## Emergency Procedures

### P0: Complete Network Outage
**Expected Response Time:** Immediate
**See:** `assets/runbooks/NETWORK_OPERATIONS_RUNBOOK.md` → Incident Response Procedures

**Quick Steps:**
1. Check physical layer (power, cables, LEDs)
2. Console into pfSense
3. Verify WAN connectivity: `ping 8.8.8.8`
4. Check pfSense services: `pfctl -s info`
5. Restart critical services if needed
6. Restore from last backup if necessary

### P1: VLAN Cannot Access Internet
**Expected Response Time:** 15 minutes
**See:** `assets/runbooks/NETWORK_OPERATIONS_RUNBOOK.md` → Incident Response Procedures

**Quick Steps:**
1. Identify affected VLAN
2. Test: Client → Gateway → Internet
3. Check firewall rules for that VLAN
4. Verify NAT configuration
5. Check DNS resolution

### P1: Wireless Network Down
**Expected Response Time:** 15 minutes
**See:** `assets/runbooks/NETWORK_OPERATIONS_RUNBOOK.md` → Incident Response Procedures

**Quick Steps:**
1. Check UniFi Controller status
2. Ping access points
3. Verify PoE power delivery
4. Force provision APs if needed
5. Check SSID configuration

### P0: Security Breach (Confirmed IPS Alert)
**Expected Response Time:** 5 minutes
**See:** `assets/runbooks/NETWORK_OPERATIONS_RUNBOOK.md` → Security Procedures

**Quick Steps:**
1. Identify compromised host
2. Block host at firewall immediately
3. Preserve evidence (logs, packet captures)
4. Investigate alert details
5. Isolate and rebuild host if compromised
6. Document incident

---

## Maintenance Schedule

### Daily (Automated)
- ✅ Configuration backup to TrueNAS
- ✅ Suricata IPS signature check
- ✅ System health monitoring

### Weekly (Manual - 15 minutes)
- Review firewall logs
- Check DHCP utilization
- Update IPS signatures
- Verify backup completion

### Monthly (Manual - 1 hour)
- Apply security updates
- Audit firewall rules
- Test VPN access
- Review security incidents
- Rotate guest network password

### Quarterly (Manual - 2-3 hours)
- Full disaster recovery test
- Security penetration test
- Capacity planning review
- Documentation updates
- Hardware inspection

---

## Configuration Backup Procedures

### Automated Daily Backups
```bash
# pfSense automatically backs up to:
# /cf/conf/backup/config-<timestamp>.xml

# Backups also sync to TrueNAS:
# /mnt/backups/network/pfsense/daily/
# Retention: 7 daily, 4 weekly, 12 monthly
```

### Manual Backup
```bash
# Via WebGUI:
# Diagnostics → Backup & Restore
# 1. Click "Download configuration"
# 2. Save as: pfsense-config-YYYY-MM-DD.xml
# 3. Store in secure location

# Via SSH:
scp admin@192.168.1.1:/cf/conf/config.xml ./pfsense-backup-$(date +%Y%m%d).xml
```

### UniFi Controller Backup
```bash
# Via UniFi UI:
# Settings → Backup → Download Backup
# Retention: Auto-backup daily, keep 30 days

# Backup location (self-hosted):
# /data/backup/autobackup/
```

---

## Troubleshooting Quick Guide

### "I can't access the internet"
1. Can you ping the gateway? (`ping 192.168.x.1`)
   - No → Layer 2 issue (cable, switch port, VLAN)
   - Yes → Continue
2. Can you ping 8.8.8.8?
   - No → Firewall rule or NAT issue
   - Yes → Continue
3. Can you resolve DNS? (`nslookup google.com`)
   - No → DNS server issue
   - Yes → Check browser/application

### "The firewall/switch is down"
1. Check power and physical connections
2. Verify LEDs show activity
3. Console into device if possible
4. Check for recent changes or updates
5. Restore from backup if needed
6. See Emergency Recovery section

### "IPS is alerting on everything"
1. Check for false positive patterns
2. Review alert severity (Priority 1-3)
3. Verify legitimate traffic vs attack
4. Add suppression rules for false positives
5. Update IPS signatures if outdated

---

## Related Documentation

### Project Documentation
- **Project README:** `/projects/06-homelab/PRJ-HOME-001/README.md`
- **Network Architecture:** `assets/documentation/network-architecture.mermaid`
- **Network Inventory:** `assets/documentation/network-inventory.md`
- **Security Policies:** `assets/documentation/security-policies.md`

### Configuration Files
- **pfSense Config:** `assets/pfsense/pfsense-config.xml`
- **UniFi Config:** `assets/unifi/unifi-config.json`

### External Resources
- [pfSense Documentation](https://docs.netgate.com/pfsense/en/latest/)
- [Suricata IPS Rules](https://rules.emergingthreats.net/)
- [UniFi Controller Guide](https://help.ui.com/)

---

## Change Management

### Making Changes to Network Configuration

**Before Making Changes:**
1. Backup current configuration
2. Document planned change
3. Identify rollback procedure
4. Schedule maintenance window (if needed)
5. Notify affected users

**During Changes:**
1. Make one change at a time
2. Test immediately after each change
3. Monitor logs for errors
4. Document what was actually done

**After Changes:**
1. Verify services are operational
2. Update documentation
3. Create new configuration backup
4. Monitor for 24 hours

**If Something Goes Wrong:**
1. Stop making changes
2. Assess impact
3. Rollback if necessary:
   - Diagnostics → Backup & Restore → Config History
   - Click "Restore" on previous config
4. Document what happened
5. Plan corrective action

---

## Contacts and Escalation

### Self-Service Resources (Tier 1)
- This runbook
- Project README
- Detailed operational runbooks in `assets/runbooks/`

### Community Support (Tier 2)
- r/PFSENSE (Reddit)
- r/Ubiquiti (Reddit)
- r/homelab (Reddit)
- Netgate forums
- UI.com community

### Professional Support (Tier 3)
- Netgate Support: https://www.netgate.com/support/
- Ubiquiti Support: https://help.ui.com/

---

## Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-11-10 | Initial runbook creation | Samuel Jackson |

---

**Next Review Date:** February 10, 2026
**Review Frequency:** Quarterly

---

*For detailed operational procedures, see the comprehensive runbooks in the `assets/runbooks/` directory.*
