# Network Infrastructure - Operational Runbook

**Version:** 1.0
**Last Updated:** November 6, 2025
**Maintainer:** Samuel Jackson
**On-Call Contact:** #homelab-network (Slack)

---

## Table of Contents

1. [Overview](#overview)
2. [Network Architecture](#network-architecture)
3. [Incident Response Procedures](#incident-response-procedures)
4. [Troubleshooting Guide](#troubleshooting-guide)
5. [Maintenance Procedures](#maintenance-procedures)
6. [Security Procedures](#security-procedures)
7. [Emergency Recovery](#emergency-recovery)
8. [Reference Information](#reference-information)

---

## Overview

### Purpose

This runbook provides operational procedures for managing and troubleshooting
the homelab network infrastructure, including pfSense firewall, UniFi
switching/wireless, VLAN segmentation, and security controls.

### Scope

- **Firewall:** pfSense (192.168.1.1)
- **Switching:** UniFi Switch 24 POE (192.168.1.2)
- **Wireless:** 2x UniFi U6 Pro Access Points (192.168.1.3-4)
- **VLANs:** 5 network segments (Trusted, IoT, Guest, Servers, DMZ)
- **Security:** Suricata IPS, OpenVPN, WPA3 Enterprise

### Service Criticality

- **Criticality Level:** P0 (Critical Infrastructure)
- **RTO (Recovery Time Objective):** 30 minutes
- **RPO (Recovery Point Objective):** 24 hours (config backups)

### Key Metrics

- **Uptime Target:** 99.9% (8.76 hours downtime/year)
- **Incident Response Time:** <10 minutes (network outage), <30 minutes (VLAN issue)
- **Security Incident Response:** <5 minutes (critical IPS alert)

---

## Network Architecture

### VLAN Summary

| VLAN | Network | Purpose | Trust Level | Gateway |
|------|---------|---------|-------------|---------|
| 10 | 192.168.1.0/24 | Trusted | High | 192.168.1.1 |
| 20 | 192.168.20.0/24 | IoT | Medium | 192.168.20.1 |
| 30 | 192.168.30.0/24 | Guest | Low | 192.168.30.1 |
| 40 | 192.168.40.0/24 | Servers | High | 192.168.40.1 |
| 50 | 192.168.50.0/24 | DMZ | Low | 192.168.50.1 |

### Critical Services

| Service | IP Address | Port | Purpose | Status Check |
|---------|------------|------|---------|--------------|
| pfSense WebGUI | 192.168.1.1 | 443 | Firewall management | `curl -k https://192.168.1.1` |
| UniFi Controller | 192.168.1.2 | 8443 | Network management | `curl -k https://192.168.1.2:8443/status` |
| DNS (Unbound) | 192.168.1.1 | 53 | DNS resolution | `dig @192.168.1.1 google.com` |
| DHCP Server | 192.168.1.1 | 67 | IP assignment | `dhcping -s 192.168.1.1` |
| OpenVPN | 192.168.1.1 | 1194 | Remote access | `telnet 192.168.1.1 1194` |

### Inter-VLAN Firewall Rules Summary

```
Trusted (VLAN 10) → Servers (VLAN 40): ALLOW all
Trusted (VLAN 10) → IoT (VLAN 20): ALLOW all
Trusted (VLAN 10) → Internet: ALLOW all

IoT (VLAN 20) → Internet: ALLOW HTTP/HTTPS only
IoT (VLAN 20) → Servers (VLAN 40): DENY all
IoT (VLAN 20) → Trusted (VLAN 10): DENY all

Guest (VLAN 30) → Internet: ALLOW HTTP/HTTPS only (10/5 Mbps limit)
Guest (VLAN 30) → All Internal VLANs: DENY all

Servers (VLAN 40) → Internet: ALLOW all
Servers (VLAN 40) → All Internal VLANs: ALLOW initiated connections

DMZ (VLAN 50) → Internet: ALLOW all
DMZ (VLAN 50) → All Internal VLANs: DENY all
Internet → DMZ (VLAN 50): ALLOW ports 80, 443 (port forward)
```

---

## Incident Response Procedures

### INCIDENT: Complete Network Outage

**Symptoms:**

- All devices lose connectivity
- Cannot access pfSense WebGUI
- Wireless networks disappear

**Severity:** Critical
**Response Time:** Immediate

#### Immediate Actions

1. **Verify Physical Layer**

   ```bash
   # Check if you can console into pfSense
   # Physical access to firewall or IPMI/iLO

   # At pfSense console:
   # Option 1: Assign Interfaces
   # Option 8: Shell

   # Check interface status
   ifconfig
   # Look for: UP,RUNNING on WAN and LAN interfaces

   # Check link status
   ifconfig <INTERFACE> | grep status
   # Expected: status: active
   ```

2. **Check WAN Connectivity**
   ```bash

   # At pfSense shell

   ping -c 4 8.8.8.8

   # If fails, check WAN interface

   ifconfig <WAN_INTERFACE>

   # Verify IP address assigned by ISP

   # Check ISP modem

   # Physically inspect: Power, Link, Online lights should be solid

   # Reboot modem if necessary

   # 1. Unplug power from modem

   # 2. Wait 30 seconds

   # 3. Plug back in

   # 4. Wait 2-5 minutes for sync

   ```

3. **Check pfSense Services**
   ```bash
   # At pfSense shell
   pfctl -s info
   # Check: Status: Enabled for X days

   # If firewall is disabled:
   pfctl -e

   # Check routing table
   netstat -rn
   # Verify default route exists:
   # default   <ISP_GATEWAY>   UGS   <WAN_INTERFACE>
   ```

4. **Test LAN Connectivity**

   ```bash
   # From pfSense shell, ping a device on LAN
   ping -c 4 192.168.1.2  # UniFi Switch

   # If fails:
   # - Check LAN interface: ifconfig <LAN_INTERFACE>
   # - Check switch port light is on
   # - Check cable is plugged in
   ```

#### Resolution Decision Tree

```
Can you access pfSense console?
├─ NO → Physical issue with firewall
│   ├─ No power? → Check PSU, power cable
│   ├─ Boot failure? → Boot from USB recovery, restore config
│   └─ Hardware failure? → Swap to backup firewall, restore config
│
└─ YES → Check service status
    ├─ WAN down? → Check ISP modem, reboot modem
    ├─ LAN down? → Check switch connectivity, verify VLAN config
    ├─ DHCP not responding? → Restart DHCP service
    └─ DNS not resolving? → Restart Unbound service
```

#### Recovery Steps

**Scenario A: WAN Down (ISP Issue)**
```bash

# Verify WAN interface

ifconfig <WAN_INTERFACE>

# Request new DHCP lease from ISP

dhclient -r <WAN_INTERFACE>  # Release
sleep 5
dhclient <WAN_INTERFACE>      # Renew

# Or via WebGUI (if accessible from LAN):

# Status → Interfaces → WAN → Release / Renew

# Test connectivity

ping -c 4 8.8.8.8
ping -c 4 google.com

# If still down, call ISP support:

# - Account number: <YOUR_ACCOUNT>

# - Service address: <YOUR_ADDRESS>

# - Report: "No sync on cable modem"

```

**Scenario B: LAN Services Down**
```bash
# Restart key services
pfSsh.php playback svc restart unbound    # DNS
pfSsh.php playback svc restart dhcpd      # DHCP
pfSsh.php playback svc restart ntpd       # NTP

# Or via WebGUI:
# Status → Services → Select service → Restart

# Verify services running
ps aux | grep -E "unbound|dhcpd|ntpd"
```

**Scenario C: Firewall Rules Broken (Recent Change)**

```bash
# Check recent changes
clog /var/log/filter.log | head -50

# View active firewall rules
pfctl -s rules

# Rollback to previous config
# Via console:
# Option 15: Restore recent configuration
# Select backup from 1-2 days ago

# Or via WebGUI:
# Diagnostics → Backup & Restore → Config History
# Click "Restore" on last known-good config
```

#### Verification
- [ ] WAN has IP address and default route
- [ ] Can ping 8.8.8.8 from pfSense
- [ ] Can ping pfSense LAN IP from client
- [ ] DNS resolves: `nslookup google.com 192.168.1.1`
- [ ] DHCP assigns IP to test device
- [ ] Can browse internet from client device

---

### INCIDENT: VLAN Cannot Access Internet

**Symptoms:**
- Devices on one VLAN cannot access internet
- Other VLANs working fine
- Devices can ping gateway but not external IPs

**Severity:** High
**Response Time:** 15 minutes

#### Diagnosis

1. **Identify Affected VLAN**
   ```bash

   # From client on affected VLAN

   ip addr show  # Linux/Mac
   ipconfig      # Windows

   # Note VLAN subnet (e.g., 192.168.20.x = VLAN 20 IoT)

   ```

2. **Test Connectivity Stages**
   ```bash
   # Stage 1: Can reach gateway?
   ping 192.168.20.1  # VLAN 20 gateway
   # If fails → Layer 2 issue (switch/VLAN config)

   # Stage 2: Can reach pfSense WAN interface?
   ping 192.168.1.1   # pfSense LAN
   # If fails → Firewall rule blocking inter-VLAN

   # Stage 3: Can reach internet IPs?
   ping 8.8.8.8
   # If fails → NAT or routing issue

   # Stage 4: Can resolve DNS?
   nslookup google.com 192.168.20.1
   # If fails → DNS forwarding issue
   ```

3. **Check Firewall Rules**

   ```bash
   # Via pfSense WebGUI:
   # Firewall → Rules → <VLAN_INTERFACE> (e.g., IoT_VLAN20)

   # Look for rules allowing:
   # - Source: IoT subnet (192.168.20.0/24)
   # - Destination: any or WAN net
   # - Protocol: any or ICMP/TCP/UDP

   # Check rule ordering (top-down evaluation)
   # DENY rules above ALLOW rules will block traffic
   ```

#### Common Issues

| Symptom | Cause | Resolution |
|---------|-------|------------|
| Can ping gateway, can't ping 8.8.8.8 | Firewall rule blocking | Add rule: Allow IoT → any |
| Can ping 8.8.8.8, can't browse | DNS broken | Check Unbound forwarding, verify DNS rule allows port 53 |
| Intermittent connectivity | Stateful connection tracking full | Increase firewall state table size (sysctl) |
| New VLAN never worked | NAT rule missing | Add outbound NAT rule for new VLAN subnet |

#### Resolution Steps

**Scenario A: Firewall Rule Blocking**
```bash

# Via pfSense WebGUI:

# Firewall → Rules → IoT (VLAN 20)

# Add rule at TOP of list:

# ┌─────────────────────────────┐

# │ Action: Pass                │

# │ Interface: IoT              │

# │ Address Family: IPv4        │

# │ Protocol: Any               │

# │ Source: IoT subnet          │

# │ Destination: Any            │

# │ Description: Allow internet │

# └─────────────────────────────┘

# Click "Save" → "Apply Changes"

# Test immediately from client

ping 8.8.8.8

```

**Scenario B: DNS Not Resolving**
```bash
# Via pfSense WebGUI:
# Services → DNS Resolver → Access Lists

# Verify IoT subnet (192.168.20.0/24) is in access list
# If missing:
# - Action: Allow
# - Network: 192.168.20.0/24
# - Description: IoT VLAN DNS access

# Save and restart Unbound
# Services → DNS Resolver → Apply Changes

# Test from client
nslookup google.com 192.168.20.1
```

**Scenario C: NAT Not Configured**

```bash
# Via pfSense WebGUI:
# Firewall → NAT → Outbound

# Check mode: "Automatic outbound NAT" (default)
# If "Hybrid" or "Manual":

# Add manual rule:
# ┌──────────────────────────────────┐
# │ Interface: WAN                   │
# │ Source: 192.168.20.0/24 (IoT)    │
# │ Translation: Interface Address   │
# │ Description: IoT NAT             │
# └──────────────────────────────────┘

# Save → Apply Changes

# Test from client
curl -I https://google.com
```

#### Verification
- [ ] Ping gateway succeeds
- [ ] Ping 8.8.8.8 succeeds
- [ ] DNS resolution works: `nslookup google.com`
- [ ] Can browse websites
- [ ] Check firewall logs show PASS entries (not BLOCK)

---

### INCIDENT: Wireless Network Down

**Symptoms:**
- SSID not broadcasting or clients cannot connect
- Existing clients lose connectivity
- Authentication failures

**Severity:** High
**Response Time:** 15 minutes

#### Diagnosis

1. **Check UniFi Controller Status**
   ```bash

   # Via browser: https://192.168.1.2:8443

   # Or SSH to UniFi Switch

   ssh admin@192.168.1.2

   # Check if controller is running

   ps aux | grep unifi

   # Check access points status

   # UniFi UI → Devices → Access Points

   # Status should be: "Connected" (green)

   ```

2. **Check Access Point Connectivity**
   ```bash
   # Ping both APs
   ping -c 4 192.168.1.3  # AP1 Living Room
   ping -c 4 192.168.1.4  # AP2 Office

   # SSH to AP (if accessible)
   ssh admin@192.168.1.3

   # Check status
   info
   # Look for: State: Connected
   ```

3. **Check PoE Power Delivery**

   ```bash
   # Via UniFi UI:
   # Devices → UniFi Switch → Port Manager

   # Check ports 2-3 (where APs are connected)
   # PoE status should show: "Powered" with ~10-15W consumption

   # If not powered:
   # - Check PoE budget (total <250W)
   # - Disable PoE on non-critical ports
   # - Cycle PoE on AP port
   ```

#### Common Issues

| Issue | Symptom | Resolution |
|-------|---------|------------|
| AP offline | No SSID broadcast, device shows "Disconnected" | Check PoE, reboot AP, check trunk port VLAN config |
| Authentication fails | Clients can't connect, "Incorrect password" | Check RADIUS server (if WPA3 Enterprise), verify PSK |
| Slow performance | Connects but slow speeds | Check channel interference, perform RF scan, adjust power |
| Intermittent drops | Clients disconnect randomly | Check AP firmware version, update if buggy release |

#### Resolution Steps

**Scenario A: Access Point Offline (No PoE)**
```bash

# Via UniFi UI:

# Devices → UniFi Switch → Port 2 (AP1) → Settings

# Disable PoE:

# PoE: Off → Apply

# Wait 10 seconds

# Re-enable PoE:

# PoE: Auto (802.3at) → Apply

# Monitor AP boot (takes 2-3 minutes)

# Watch for LED sequence:

# - White flashing = Booting

# - White solid = Upgrading firmware

# - Blue solid = Connected and adopted

# Verify in UI: Status should change to "Connected"

```

**Scenario B: SSID Not Broadcasting**
```bash
# Via UniFi UI:
# Settings → WiFi → Select SSID

# Check configuration:
# - Enabled: ✓ (checked)
# - Hide SSID: ☐ (unchecked)
# - WiFi Band: 2.4 GHz & 5 GHz (both)

# Check AP assignment:
# WLAN Group: Should include both APs
# If "All APs" is selected, should broadcast on both

# Force provision APs:
# Devices → Access Points → Select AP → "Force Provision"

# Wait 30 seconds, test with phone WiFi scan
```

**Scenario C: WPA3 Enterprise Authentication Fails**

```bash
# Via pfSense or RADIUS server
# Check FreeIPA RADIUS service

ssh admin@192.168.40.25  # FreeIPA server

# Check RADIUS service status
systemctl status radiusd

# If stopped:
systemctl start radiusd

# Check RADIUS logs
tail -f /var/log/radius/radius.log

# Test RADIUS authentication
radtest testuser password 192.168.40.25 0 testing123

# Expected: Access-Accept

# If fails:
# - Verify user exists in FreeIPA
# - Verify shared secret matches UniFi config
# - Check firewall allows UDP 1812 (auth) and 1813 (accounting)
```

#### Verification
- [ ] SSIDs visible in WiFi scan
- [ ] Test device connects successfully
- [ ] Internet access works after connection
- [ ] Both APs show "Connected" status
- [ ] No authentication errors in logs

---

### INCIDENT: Suricata IPS Alert - Potential Intrusion

**Symptoms:**
- Critical IPS alert fires
- Blocked traffic to/from specific IP
- Potential compromise indicated

**Severity:** Critical (if exploit detected)
**Response Time:** 5 minutes

#### Immediate Actions

1. **Assess Alert Severity**
   ```bash

   # Via pfSense WebGUI:

   # Services → Suricata → Alerts

   # Check alert details:

   # - Priority: 1 (Critical), 2 (High), 3 (Medium)

   # - Category: Exploit, Malware, Scan, Policy Violation

   # - Source/Destination IPs

   # Common critical alerts:

   # - "ET EXPLOIT" → Active exploitation attempt

   # - "ET MALWARE" → Malware command & control

   # - "ET DROP" → Known malicious IP

   ```

2. **Identify Affected Host**
   ```bash
   # Note internal IP from alert (e.g., 192.168.1.25)

   # Determine hostname
   # Via pfSense: Status → DHCP Leases
   # Or: nslookup 192.168.1.25 192.168.1.1

   # Identify device type/purpose
   # Check network inventory spreadsheet
   ```

3. **Immediate Containment (If Critical)**

   ```bash
   # Option 1: Block at firewall (temporary)
   # Via pfSense WebGUI:
   # Firewall → Rules → <VLAN> → Add rule at TOP
   # ┌───────────────────────────┐
   # │ Action: Block             │
   # │ Source: 192.168.1.25      │
   # │ Destination: Any          │
   # │ Log: ✓                    │
   # │ Description: Quarantine   │
   # └───────────────────────────┘
   # Save → Apply Changes

   # Option 2: Shutdown host immediately
   ssh admin@192.168.1.25 "sudo shutdown -h now"

   # Option 3: Disconnect from network physically
   # If VM: Shutdown via Proxmox UI
   # If physical: Disable switch port
   ```

#### Alert Classification

**False Positive Indicators:**
- Triggered by legitimate software update
- Internal vulnerability scanner (e.g., Nessus)
- Known safe source IP
- Low-severity rule (Priority 3)

**True Positive Indicators:**
- Multiple related alerts from same source
- Destination is external malicious IP (check threat intel)
- Unusual traffic pattern (e.g., 3am download spike)
- Alert matches recent CVE

#### Investigation Steps

**Step 1: Analyze Traffic**
```bash

# Via pfSense: Diagnostics → Packet Capture

# - Interface: <VLAN_INTERFACE>

# - Host Address: 192.168.1.25 (affected host)

# - Capture file: /tmp/capture-$(date +%s).pcap

# Start capture for 2 minutes

# Download PCAP and analyze with Wireshark

# Look for:

# - Unusual ports (e.g., 4444, 31337)

# - Unencrypted credentials (HTTP Basic Auth)

# - DNS queries to suspicious domains

```

**Step 2: Check Host Logs**
```bash
# SSH to affected host (if safe to do so)
ssh admin@192.168.1.25

# Check authentication logs
sudo grep "Failed password" /var/log/auth.log | tail -20

# Check network connections
sudo netstat -tulpn | grep ESTABLISHED

# Check running processes
ps aux --sort=-%cpu | head -20

# Check cron jobs (backdoor persistence)
sudo crontab -l
sudo cat /etc/cron.d/*

# Check for suspicious files
sudo find / -name "*.php" -mtime -1  # PHP shells added today
sudo find /tmp -type f -executable   # Executable files in /tmp
```

**Step 3: Correlate with Threat Intelligence**

```bash
# Check external IP reputation
curl -s https://www.abuseipdb.com/check/<EXTERNAL_IP>/json?key=<API_KEY> | jq .

# Check VirusTotal (if file hash available)
curl -s https://www.virustotal.com/vtapi/v2/file/report?apikey=<KEY>&resource=<HASH> | jq .

# Check Emerging Threats rule details
# https://rules.emergingthreats.net/open/suricata-6.0/rules/
# Search for SID (signature ID) from alert
```

#### Response Actions

**Scenario A: False Positive (Safe Traffic)**
```bash

# Via pfSense WebGUI:

# Services → Suricata → Suppression

# Add suppression rule:

# ┌──────────────────────────────────────┐

# │ SID: <SIGNATURE_ID>                  │

# │ Track by: Source IP                  │

# │ IP Address: 192.168.1.25             │

# │ Description: Update server traffic   │

# └──────────────────────────────────────┘

# Save → Apply Changes

# Document decision in incident log

```

**Scenario B: Confirmed Compromise**
```bash
# Immediate actions:
# 1. Isolate host (already done in containment step)

# 2. Preserve evidence
ssh admin@192.168.1.25
sudo tar -czf /tmp/evidence-$(date +%s).tar.gz \
  /var/log \
  /tmp \
  /home/*/.bash_history \
  /root/.bash_history

# Copy evidence off host
scp admin@192.168.1.25:/tmp/evidence-*.tar.gz /mnt/incident-response/

# 3. Determine entry vector
# - Check for unpatched vulnerabilities
# - Review firewall logs for initial connection
# - Check for phishing emails

# 4. Eradication
# - Rebuild host from known-good backup
# - Or: Wipe and reinstall OS

# 5. Recovery
# - Restore host with latest patches
# - Change all passwords/API keys
# - Update firewall rules to prevent recurrence

# 6. Post-incident
# - Write incident report
# - Update IPS rules
# - Schedule penetration test
```

**Scenario C: Scanning Activity (Reconnaissance)**

```bash
# If alert shows port scanning from internal IP:
# This could be:
# - Legitimate vulnerability scanner (Nessus, OpenVAS)
# - Compromised host performing reconnaissance
# - Misconfigured service (mDNS discovery)

# Check if scan is authorized:
# - Is source IP a known scanner? (192.168.40.50 = Nessus)
# - Is there a scheduled security assessment?

# If unauthorized:
# - Identify user/owner of device
# - Investigate host for compromise
# - Review recent software installs

# If authorized:
# - Create Suricata suppression rule for scanner IP
# - Schedule scans during maintenance window
# - Document in security procedures
```

#### Verification
- [ ] Alert has been investigated and categorized
- [ ] Affected host is contained or cleared
- [ ] Evidence preserved (if compromise)
- [ ] Firewall rules updated (if needed)
- [ ] IPS rules tuned (suppression or new signature)
- [ ] Incident documented in log
- [ ] Stakeholders notified

---

## Troubleshooting Guide

### DNS Not Resolving

**Symptoms:**
- `nslookup google.com` fails or times out
- Can ping 8.8.8.8 but can't browse websites
- Error: "DNS server not responding"

**Diagnosis:**
```bash

# Test DNS resolution from client

nslookup google.com 192.168.1.1

# If fails, test from pfSense

dig @127.0.0.1 google.com

# If succeeds on pfSense but fails from client:

# → Firewall rule blocking port 53

# If fails on pfSense:

# → Unbound service issue or upstream DNS down

```

**Resolution:**
```bash
# Via pfSense WebGUI:
# Services → DNS Resolver

# Check Unbound status:
# Status: Running (green checkmark)

# If stopped:
# Click "Start"

# Check configuration:
# Enable DNS Resolver: ✓ (checked)
# Listen Port: 53
# Network Interfaces: All (or specific VLANs)

# Test forwarding to upstream:
# System → General Setup
# DNS Servers: 1.1.1.1, 8.8.8.8
# Click "Save"

# Restart Unbound:
# Services → DNS Resolver → Apply Changes

# Verify from client:
nslookup google.com 192.168.1.1
```

---

### DHCP Not Assigning IPs

**Symptoms:**

- Device gets APIPA address (169.254.x.x)
- Cannot obtain network configuration
- Static IP works but DHCP doesn't

**Diagnosis:**

```bash
# Via pfSense WebGUI:
# Status → System Logs → DHCP

# Look for:
# - "DHCPREQUEST for X.X.X.X from <MAC> via <INTERFACE>"
# - "DHCPACK on X.X.X.X to <MAC>"

# If no DHCPREQUEST appears:
# → Client not sending requests (driver issue)

# If DHCPREQUEST appears but no DHCPACK:
# → DHCP service issue or pool exhausted
```

**Resolution:**
```bash

# Check DHCP service status

# Via pfSense WebGUI:

# Status → Services

# dhcpd should show "Running"

# If stopped:

# Click "Start"

# Check DHCP pool has available IPs

# Services → DHCP Server → <VLAN>

# For VLAN 20 (IoT):

# Range: 192.168.20.50 to 192.168.20.200

# Total IPs: 151

# Check leases:

# Status → DHCP Leases

# Count active leases, compare to pool size

# If pool exhausted:

# Option 1: Expand range

# Services → DHCP Server → IoT

# Range to: 192.168.20.250

# Option 2: Reduce lease time

# Default lease time: 7200 (2 hours)

# Maximum lease time: 86400 (24 hours)

# Restart DHCP service:

# Services → DHCP Server → Save → Apply Changes

```

---

### VPN Connection Fails

**Symptoms:**
- OpenVPN client cannot connect
- Authentication succeeds but no traffic
- Connection drops after few minutes

**Diagnosis:**
```bash
# Check OpenVPN server status
# Via pfSense WebGUI:
# Status → OpenVPN

# Should show:
# - Status: up since <TIMESTAMP>
# - 0 or more clients connected

# If down:
# → Service crashed or certificate issue

# Check firewall rule allows UDP 1194
# Firewall → Rules → WAN
# Should have rule: Allow UDP 1194 from any to WAN address
```

**Resolution:**

```bash
# Restart OpenVPN server
# Status → OpenVPN → Server: <NAME> → Restart

# Check certificates validity
# System → Cert Manager → Certificates
# Expiration date should be future

# If certificate expired:
# 1. Renew certificate:
#    System → Cert Manager → CAs → Renew
# 2. Regenerate client config
# 3. Redistribute to users

# Test connectivity from external IP
# Use mobile hotspot or different network
# openvpn --config homelab.ovpn --verb 3

# Check logs:
# Status → System Logs → OpenVPN
# Look for authentication errors or routing issues
```

---

## Maintenance Procedures

### Performing pfSense Updates

**Frequency:** Monthly or when critical security patch released
**Downtime:** 5-10 minutes
**Risk Level:** Medium

#### Prerequisites
- [ ] Backup current configuration
- [ ] Notify users of maintenance window
- [ ] Verify backup firewall available (if dual-WAN)
- [ ] Schedule during low-traffic period (2am-4am)

#### Steps
```bash

# 1. Backup configuration

# Diagnostics → Backup & Restore

# Download config.xml to safe location with date:

# pfsense-config-2025-11-06.xml

# 2. Review release notes

# Visit: https://docs.netgate.com/pfsense/en/latest/releases/

# Check for breaking changes or known issues

# 3. Install updates

# System → Update → System Update

# Click "Confirm" to download and install

# 4. Wait for reboot (5-10 minutes)

# Dashboard will become unavailable during reboot

# 5. Verify services after reboot

# Status → Services

# All should show "Running":

# - dpinger

# - Unbound

# - dhcpd

# - sshd

# 6. Test connectivity

# From client device:

ping 8.8.8.8              # Internet
nslookup google.com       # DNS
ssh admin@server.local    # Internal routing

# 7. Check Suricata IPS (if installed)

# Services → Suricata → Interfaces

# All should show "Running"

# If Suricata fails to start:

# - Check rulesets are updated

# - Restart interface: Click "Start"

# 8. Monitor firewall logs for anomalies

# Status → System Logs → Firewall

# Look for unexpected BLOCK entries

```

#### Rollback (If Issues Occur)
```bash
# Via console (if WebGUI inaccessible):
# Option 15: Restore recent configuration
# Select previous backup

# Or via WebGUI:
# Diagnostics → Backup & Restore → Config History
# Click "Restore" on pre-update config (top of list)

# System will reboot to previous version
```

---

### Adding a New Firewall Rule

**When to Use:** Opening port, allowing new service, inter-VLAN access

#### Best Practices

1. **Principle of Least Privilege:** Only allow what's necessary
2. **Specific Sources/Destinations:** Avoid "any to any"
3. **Logging:** Enable logging for new rules (disable after verification)
4. **Documentation:** Add clear description

#### Steps

```bash
# Via pfSense WebGUI:
# Firewall → Rules → <INTERFACE>

# Click "Add" (arrow up icon for top of list)

# Example: Allow IoT devices to access Pi-hole DNS
# ┌────────────────────────────────────────────────┐
# │ Action: Pass                                   │
# │ Disabled: ☐ (unchecked)                        │
# │ Interface: IoT                                 │
# │ Address Family: IPv4                           │
# │ Protocol: TCP/UDP                              │
# │                                                │
# │ Source:                                        │
# │   Type: IoT subnet                             │
# │   Address: 192.168.20.0/24                     │
# │                                                │
# │ Destination:                                   │
# │   Type: Single host or alias                   │
# │   Address: 192.168.40.35 (Pi-hole)             │
# │   Port: 53 (DNS)                               │
# │                                                │
# │ Log: ✓ (checked for first 24 hours)           │
# │ Description: IoT → Pi-hole DNS                 │
# └────────────────────────────────────────────────┘

# Click "Save" → "Apply Changes"

# Test immediately from IoT device:
nslookup google.com 192.168.40.35

# Monitor firewall logs to verify rule is hit:
# Status → System Logs → Firewall
# Look for entries matching source/destination

# After 24 hours, disable logging if rule works correctly
```

---

### VLAN Changes or Additions

**When to Use:** Adding new network segment, changing IP scheme

#### Steps
```bash

# 1. Plan VLAN configuration

# - VLAN ID: 60 (example: Cameras)

# - Subnet: 192.168.60.0/24

# - Gateway: 192.168.60.1 (pfSense)

# - DHCP Range: 192.168.60.100-200

# 2. Configure VLAN in pfSense

# Interfaces → Assignments → VLANs → Add

# ┌───────────────────────────┐

# │ Parent Interface: igb0    │

# │ VLAN Tag: 60              │

# │ Description: Cameras      │

# └───────────────────────────┘

# Save

# 3. Assign interface

# Interfaces → Assignments

# Available network ports: VLAN 60 on igb0 (opt6)

# Click "Add" → Save

# 4. Enable and configure interface

# Interfaces → OPT6

# ┌───────────────────────────────────┐

# │ Enable: ✓ (checked)               │

# │ Description: Cameras              │

# │ IPv4 Configuration Type: Static   │

# │ IPv4 Address: 192.168.60.1/24     │

# └───────────────────────────────────┘

# Save → Apply Changes

# 5. Configure DHCP for VLAN

# Services → DHCP Server → Cameras

# ┌───────────────────────────────────┐

# │ Enable: ✓                         │

# │ Range: 192.168.60.100 to          │

# │        192.168.60.200             │

# │ DNS Servers: 192.168.40.35        │

# │ Gateway: 192.168.60.1             │

# └───────────────────────────────────┘

# Save

# 6. Create firewall rules

# Firewall → Rules → Cameras

# Add rules:

# - Allow Cameras → Internet (HTTP/HTTPS only)

# - Allow Trusted → Cameras (viewing access)

# - Block Cameras → All other VLANs

# 7. Configure VLAN on UniFi Switch

# Via UniFi UI:

# Settings → Networks → Create New Network

# ┌─────────────────────────────┐

# │ Name: Cameras               │

# │ VLAN ID: 60                 │

# │ Gateway/Subnet: 192.168.60.1/24 │

# │ DHCP Mode: None (pfSense handles) │

# └─────────────────────────────┘

# Save

# Assign VLAN to switch ports:

# Devices → UniFi Switch → Port Manager

# Ports 10-14 → Network: Cameras (untagged)

# 8. Test connectivity

# Connect device to port 10, verify:

# - Gets IP 192.168.60.x

# - Can ping gateway 192.168.60.1

# - Can access internet

# - Cannot ping other VLANs (192.168.1.x)

```

---

## Security Procedures

### Responding to Security Incidents

**Classification:**
- **Level 1 (Info):** Suspicious activity, no impact
- **Level 2 (Low):** Policy violation, minor impact
- **Level 3 (Medium):** Unauthorized access attempt, potential impact
- **Level 4 (High):** Confirmed breach, active incident
- **Level 5 (Critical):** Data exfiltration, full compromise

**Response Timeline:**
- Level 1-2: 4 hours
- Level 3: 1 hour
- Level 4-5: 15 minutes

#### Incident Response Checklist

**Phase 1: Detection & Analysis (0-15 min)**
- [ ] Identify source IP and affected systems
- [ ] Classify incident severity (1-5)
- [ ] Document initial observations
- [ ] Notify incident response team

**Phase 2: Containment (15-30 min)**
- [ ] Isolate affected systems (block IP, shutdown host)
- [ ] Prevent lateral movement (firewall rules)
- [ ] Preserve evidence (logs, packet captures)
- [ ] Monitor for continued activity

**Phase 3: Eradication (30 min - 2 hours)**
- [ ] Identify root cause and entry vector
- [ ] Remove malware/backdoors
- [ ] Patch vulnerabilities
- [ ] Update firewall/IPS rules

**Phase 4: Recovery (2-8 hours)**
- [ ] Restore from clean backups
- [ ] Change all credentials
- [ ] Monitor for recurrence (48 hours)
- [ ] Gradual service restoration

**Phase 5: Post-Incident (1-2 weeks)**
- [ ] Write detailed incident report
- [ ] Conduct lessons learned meeting
- [ ] Update security procedures
- [ ] Implement preventive controls

---

### Hardening Firewall Configuration

**Annual Security Review Checklist:**

```bash
# 1. Review firewall rules
# Firewall → Rules → All interfaces
# - Remove unused rules (last hit >90 days)
# - Consolidate similar rules
# - Verify logging on critical rules

# 2. Update admin password
# System → User Manager → admin → Edit
# Change password to 20+ char passphrase

# 3. Disable unused services
# System → Advanced → Admin Access
# - Disable HTTP (HTTPS only)
# - Disable SSH (or limit to management VLAN)
# - Enable anti-lockout rule: ✓

# 4. Review certificate validity
# System → Cert Manager → Certificates
# Renew any expiring within 90 days

# 5. Update IPS signatures
# Services → Suricata → Updates
# Click "Update Rules"

# 6. Review DHCP static mappings
# Services → DHCP Server → DHCP Static Mappings
# Remove mappings for decommissioned devices

# 7. Audit VPN users
# System → User Manager
# Disable accounts for users no longer requiring access

# 8. Check for firmware updates
# System → Update
# Apply if security updates available

# 9. Review firewall logs
# Status → System Logs → Firewall
# Identify anomalies or attack patterns

# 10. Test disaster recovery
# Restore config backup to spare hardware
# Verify all services function correctly
```

---

## Emergency Recovery

### Complete Firewall Failure (Hardware)

**Symptoms:**

- pfSense will not boot
- Hardware failure indicated
- Smoke/burning smell from device

**Recovery Steps:**

```bash
# 1. Prepare replacement hardware
# - Same or better CPU/RAM/NICs
# - Boot from USB installer

# 2. Install pfSense fresh
# - Download latest ISO: https://www.pfsense.org/download/
# - Create bootable USB
# - Install on replacement hardware

# 3. Restore configuration
# At "Restore pfSense Configuration" prompt:
# - Insert USB with backup config
# - Select config file: pfsense-config-<DATE>.xml
# - System will reboot

# 4. Verify interface assignments match
# If hardware has different NIC names:
# Console → Option 1: Assign Interfaces
# Map interfaces to match:
# - WAN → (ISP connection)
# - LAN → (internal switch)
# - VLANs → (as configured)

# 5. Verify services start
# - DHCP: Status → Services → dhcpd (Running)
# - DNS: Status → Services → Unbound (Running)
# - OpenVPN: Status → OpenVPN (up)

# 6. Test connectivity from each VLAN
# - VLAN 10 (Trusted): Full access
# - VLAN 20 (IoT): Internet only
# - VLAN 40 (Servers): Full access

# 7. Verify firewall rules applied
# Firewall → Rules → All interfaces
# Rule counts should match backup

# Expected downtime: 30-60 minutes
```

---

## Reference Information

### Common Port Numbers

| Port | Protocol | Service | Usage |
|------|----------|---------|-------|
| 22 | TCP | SSH | Remote administration |
| 53 | TCP/UDP | DNS | Name resolution |
| 67/68 | UDP | DHCP | IP address assignment |
| 80 | TCP | HTTP | Web traffic |
| 443 | TCP | HTTPS | Encrypted web traffic |
| 1194 | UDP | OpenVPN | VPN access |
| 1812 | UDP | RADIUS Auth | 802.1X authentication |
| 8443 | TCP | UniFi | UniFi Controller UI |

### IP Address Inventory

**Firewall & Network Infrastructure:**
- 192.168.1.1 - pfSense firewall
- 192.168.1.2 - UniFi Switch 24 POE
- 192.168.1.3 - UniFi AP1 (Living Room)
- 192.168.1.4 - UniFi AP2 (Office)

**Critical Servers (VLAN 40):**
- 192.168.40.10-12 - Proxmox Cluster
- 192.168.40.20 - TrueNAS Storage
- 192.168.40.25 - FreeIPA (RADIUS)
- 192.168.40.30 - Syslog Server
- 192.168.40.35 - Pi-hole DNS

### Useful Commands

**pfSense Shell:**
```bash

# Restart network interfaces

pfSsh.php playback interfaces

# Restart all services

pfSsh.php playback services

# View routing table

netstat -rn

# Show firewall state table

pfctl -s state

# View loaded firewall rules

pfctl -s rules

# Restart Unbound DNS

pfSsh.php playback svc restart unbound

```

**UniFi CLI (via SSH):**
```bash
# Show device info
info

# Reboot AP
reboot

# Set-inform (re-adopt to controller)
set-inform http://192.168.1.2:8080/inform

# Speed test
speedtest
```

### Configuration Backup Locations

- **pfSense Configs:** `/cf/conf/backup/` (on firewall)
- **AutoConfigBackup:** Cloud (if enabled)
- **Manual Backups:** `/mnt/backups/network/pfsense/` (TrueNAS)
- **UniFi Configs:** `/data/backup/autobackup/` (UniFi Controller)

### Escalation Contacts

**Tier 1 (Self-Service):**

- This runbook
- pfSense documentation: https://docs.netgate.com/
- UniFi forums: https://community.ui.com/

**Tier 2 (Community Support):**

- pfSense subreddit: r/PFSENSE
- UniFi subreddit: r/Ubiquiti
- HomeLab subreddit: r/homelab

**Tier 3 (Professional Support):**

- Netgate Support (paid): https://www.netgate.com/support/
- Ubiquiti Support: https://help.ui.com/

---

**End of Runbook**

*Last Reviewed: November 6, 2025*
*Next Review: February 6, 2026 (Quarterly)*
