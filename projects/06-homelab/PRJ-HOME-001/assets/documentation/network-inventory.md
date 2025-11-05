# Network Inventory and Documentation

## Overview
This document provides comprehensive information about the homelab network infrastructure, including IP address allocations, device inventory, switch port assignments, firewall rules, and wireless security policies.

---

## IP Address Allocation

### VLAN 10 - Trusted Network (192.168.1.0/24)
**Purpose:** Primary network for trusted personal devices and management interfaces.

| IP Address | Hostname | MAC Address | Device Type | Description |
|------------|----------|-------------|-------------|-------------|
| 192.168.1.1 | pfsense-fw | N/A | Gateway | pfSense Firewall |
| 192.168.1.2 | unifi-switch | fc:ec:da:11:22:33 | Switch | UniFi Switch 24 POE |
| 192.168.1.3 | u6-pro-living | fc:ec:da:aa:bb:01 | Access Point | U6 Pro - Living Room |
| 192.168.1.4 | u6-pro-office | fc:ec:da:aa:bb:02 | Access Point | U6 Pro - Office |
| 192.168.1.10 | workstation-01 | 00:11:22:33:44:55 | Workstation | Primary Desktop |
| 192.168.1.11 | laptop-01 | 00:11:22:33:44:66 | Laptop | Primary Laptop |
| 192.168.1.100-200 | DHCP Pool | Various | Dynamic | DHCP Range for Trusted Devices |

**Gateway:** 192.168.1.1  
**DNS Server:** 192.168.1.1 (pfSense)  
**DHCP Lease Time:** 24 hours (86400 seconds)  
**Domain:** homelab.local

---

### VLAN 20 - IoT Network (192.168.20.0/24)
**Purpose:** Isolated network for smart home devices and IoT equipment.

| IP Address | Hostname | MAC Address | Device Type | Description |
|------------|----------|-------------|-------------|-------------|
| 192.168.20.1 | pfsense-iot-gw | N/A | Gateway | pfSense IoT Gateway |
| 192.168.20.10-99 | Static Range | Various | Reserved | Static IoT Assignments |
| 192.168.20.100-200 | DHCP Pool | Various | IoT Devices | Smart Lights, Cameras, etc. |

**Gateway:** 192.168.20.1  
**DNS Server:** 192.168.20.1  
**DHCP Lease Time:** 24 hours (86400 seconds)  
**Domain:** iot.homelab.local  
**Security:** Client isolation enabled, restricted firewall rules

---

### VLAN 30 - Guest Network (192.168.30.0/24)
**Purpose:** Internet-only access for guest devices with complete network isolation.

| IP Address | Hostname | MAC Address | Device Type | Description |
|------------|----------|-------------|-------------|-------------|
| 192.168.30.1 | pfsense-guest-gw | N/A | Gateway | pfSense Guest Gateway |
| 192.168.30.100-200 | DHCP Pool | Various | Guest Devices | Visitor Devices |

**Gateway:** 192.168.30.1  
**DNS Server:** 192.168.30.1  
**DHCP Lease Time:** 1 hour (3600 seconds)  
**Domain:** guest.homelab.local  
**Security:** Complete isolation from internal networks, bandwidth limited to 10/5 Mbps  
**Captive Portal:** Enabled with password authentication

---

### VLAN 40 - Servers Network (192.168.40.0/24)
**Purpose:** Dedicated network for virtualization hosts and core infrastructure services.

| IP Address | Hostname | MAC Address | Device Type | Description |
|------------|----------|-------------|-------------|-------------|
| 192.168.40.1 | pfsense-srv-gw | N/A | Gateway | pfSense Servers Gateway |
| 192.168.40.10 | proxmox-01 | 00:11:22:33:55:01 | Hypervisor | Proxmox Node 1 |
| 192.168.40.11 | proxmox-02 | 00:11:22:33:55:02 | Hypervisor | Proxmox Node 2 |
| 192.168.40.12 | proxmox-03 | 00:11:22:33:55:03 | Hypervisor | Proxmox Node 3 |
| 192.168.40.20 | truenas | 00:11:22:33:55:10 | Storage | TrueNAS NAS |
| 192.168.40.25 | freeipa | 00:11:22:33:55:15 | VM | FreeIPA/RADIUS Server |
| 192.168.40.30 | syslog | 00:11:22:33:55:20 | VM | Centralized Syslog Server |
| 192.168.40.35 | pihole | 00:11:22:33:55:25 | VM | Pi-hole DNS |
| 192.168.40.40 | nginx-proxy | 00:11:22:33:55:30 | VM | Nginx Reverse Proxy |
| 192.168.40.200-250 | DHCP Pool | Various | Dynamic | Reserved for temporary VMs |

**Gateway:** 192.168.40.1  
**DNS Server:** 192.168.40.1  
**DHCP Lease Time:** 24 hours (86400 seconds)  
**Domain:** servers.homelab.local  
**Security:** Accessible from Trusted VLAN, inter-server communication allowed

---

### VLAN 50 - DMZ Network (192.168.50.0/24)
**Purpose:** Demilitarized zone for public-facing services with restricted internal access.

| IP Address | Hostname | MAC Address | Device Type | Description |
|------------|----------|-------------|-------------|-------------|
| 192.168.50.1 | pfsense-dmz-gw | N/A | Gateway | pfSense DMZ Gateway |
| 192.168.50.10 | web-server | 00:11:22:33:66:10 | VM | Public Web Server |
| 192.168.50.100-150 | DHCP Pool | Various | Dynamic | Reserved for DMZ VMs |

**Gateway:** 192.168.50.1  
**DNS Server:** 192.168.50.1  
**DHCP Lease Time:** 24 hours (86400 seconds)  
**Domain:** dmz.homelab.local  
**Security:** Blocked from all internal networks, IPS monitoring enabled

---

## Hardware Inventory

### Network Equipment

#### pfSense Firewall
- **Model:** Custom Build / Protectli Vault
- **Hostname:** pfsense-fw
- **Management IP:** 192.168.1.1
- **Interfaces:**
  - igb0 (WAN): ISP Connection
  - igb1 (LAN): VLAN 10 - Trusted
  - igb2 (OPT1): VLAN 20 - IoT
  - igb3 (OPT2): VLAN 30 - Guest
  - igb4 (OPT3): VLAN 40 - Servers
  - igb5 (OPT4): VLAN 50 - DMZ
- **Services:** Firewall, NAT, DHCP, DNS (Unbound), Suricata IPS, OpenVPN, Traffic Shaping
- **Specifications:**
  - CPU: Intel Quad-Core
  - RAM: 8GB
  - Storage: 128GB SSD

#### UniFi Switch 24 POE (US24P250)
- **Model:** US24P250
- **Hostname:** unifi-switch
- **Management IP:** 192.168.1.2
- **MAC Address:** fc:ec:da:11:22:33
- **Ports:** 24x Gigabit Ethernet (16x PoE+)
- **PoE Budget:** 250W
- **Features:**
  - Layer 2 switching
  - VLAN support (all 5 VLANs configured)
  - Port security with MAC filtering
  - RSTP enabled
  - Jumbo frames enabled

#### UniFi U6 Pro - Living Room
- **Model:** U6-Pro
- **Hostname:** u6-pro-living
- **Management IP:** 192.168.1.3
- **MAC Address:** fc:ec:da:aa:bb:01
- **Radio Configuration:**
  - 2.4 GHz: Channel 1, 20 MHz
  - 5 GHz: Channel 36, 80 MHz
- **Power:** 802.3at PoE+
- **Capacity:** Up to 300 clients
- **SSIDs:** Homelab-Secure, Homelab-IoT, Homelab-Guest

#### UniFi U6 Pro - Office
- **Model:** U6-Pro
- **Hostname:** u6-pro-office
- **Management IP:** 192.168.1.4
- **MAC Address:** fc:ec:da:aa:bb:02
- **Radio Configuration:**
  - 2.4 GHz: Channel 6, 20 MHz
  - 5 GHz: Channel 149, 80 MHz
- **Power:** 802.3at PoE+
- **Capacity:** Up to 300 clients
- **SSIDs:** Homelab-Secure, Homelab-IoT, Homelab-Guest

---

## Switch Port Assignments

### UniFi Switch 24 POE Port Map

| Port | VLAN | Profile | Device | MAC Address | PoE | Description |
|------|------|---------|--------|-------------|-----|-------------|
| 1 | Trunk | Uplink | pfSense | N/A | Off | Uplink to Firewall (All VLANs) |
| 2 | 10 | AP PoE | U6 Pro Living Room | fc:ec:da:aa:bb:01 | Auto | Access Point (Tagged: 10,20,30) |
| 3 | 10 | AP PoE | U6 Pro Office | fc:ec:da:aa:bb:02 | Auto | Access Point (Tagged: 10,20,30) |
| 4 | 40 | Server | Proxmox-01 | 00:11:22:33:55:01 | Off | Proxmox Node 1 |
| 5 | 40 | Server | Proxmox-02 | 00:11:22:33:55:02 | Off | Proxmox Node 2 |
| 6 | 40 | Server | Proxmox-03 | 00:11:22:33:55:03 | Off | Proxmox Node 3 |
| 7 | 40 | Server | TrueNAS | 00:11:22:33:55:10 | Off | Network Storage |
| 8 | 10 | Trusted | Workstation | 00:11:22:33:44:55 | Off | Primary Desktop |
| 9-24 | - | - | Available | - | - | Unassigned |

**Notes:**
- Port 1 is configured as a trunk port carrying all VLANs
- Ports 2-3 have port security enabled with MAC address filtering
- Ports 4-7 have port security and LLDP-MED enabled
- All server ports use native VLAN 40

---

## Firewall Rule Matrix

### Inter-VLAN Access Matrix

| Source VLAN | → Trusted (10) | → IoT (20) | → Guest (30) | → Servers (40) | → DMZ (50) | → Internet |
|-------------|---------------|-----------|-------------|---------------|-----------|-----------|
| **Trusted (10)** | ✅ Full | ✅ Full | ❌ Denied | ✅ Full | ❌ Denied | ✅ Full |
| **IoT (20)** | ❌ Denied | ❌ Isolated | ❌ Denied | ❌ Denied | ❌ Denied | ⚠️ Limited* |
| **Guest (30)** | ❌ Denied | ❌ Denied | ❌ Isolated | ❌ Denied | ❌ Denied | ⚠️ Limited** |
| **Servers (40)** | ❌ Denied | ❌ Denied | ❌ Denied | ✅ Full | ❌ Denied | ⚠️ Updates*** |
| **DMZ (50)** | ❌ Denied | ❌ Denied | ❌ Denied | ❌ Denied | ✅ Internal | ⚠️ Updates*** |
| **Internet** | ❌ Blocked | ❌ Blocked | ❌ Blocked | ❌ Blocked | ✅ 80/443 | N/A |

**Legend:**
- ✅ Full Access - All protocols allowed
- ⚠️ Limited - Specific protocols only
- ❌ Denied - All traffic blocked

**Notes:**
- *IoT Limited: HTTP (80), HTTPS (443), DNS (53), NTP (123) only
- **Guest Limited: HTTP (80), HTTPS (443), DNS (53) only, 10/5 Mbps bandwidth limit
- ***Updates: HTTP (80), HTTPS (443), DNS (53), NTP (123) for system updates only

### Firewall Rule Justification

#### WAN Rules
1. **Block All Inbound (Default):** Default deny stance for security
2. **Allow HTTP to DMZ:** Public web service access
3. **Allow HTTPS to DMZ:** Secure public web service access

#### Trusted VLAN Rules
1. **Allow All Outbound:** Trusted devices have full internet access
2. **Allow to IoT VLAN:** Administrative access to manage IoT devices
3. **Allow to Servers VLAN:** Access to internal services and management

#### IoT VLAN Rules (Principle of Least Privilege)
1. **Allow HTTP/HTTPS:** Required for cloud services and firmware updates
2. **Allow DNS:** Required for name resolution
3. **Allow NTP:** Required for time synchronization
4. **Block Internal Networks:** Prevents lateral movement in case of compromise
5. **Block All Other:** Default deny for security

#### Guest VLAN Rules (Internet-Only Access)
1. **Allow HTTP/HTTPS:** Basic web browsing
2. **Allow DNS:** Name resolution
3. **Block All Internal:** Complete isolation from homelab resources
4. **Block All Other:** Restricted to web browsing only

#### Servers VLAN Rules
1. **Allow Inter-Server:** Required for cluster communication and services
2. **Allow HTTP/HTTPS:** Package updates and repositories
3. **Allow DNS:** Name resolution
4. **Allow NTP:** Time synchronization critical for logging and auth

#### DMZ VLAN Rules (Defense in Depth)
1. **Allow Outbound Updates:** Required for security patches
2. **Allow DNS:** Name resolution
3. **Block All Internal:** Prevents compromised DMZ from accessing internal resources
4. **Block All Other:** Minimizes attack surface

---

## Wireless Security Policies

### SSID: Homelab-Secure (VLAN 10)

**Security Level:** High  
**Authentication:** WPA3 Enterprise (802.1X)  
**Encryption:** AES-CCMP  
**PMF (802.11w):** Required  

**Features:**
- Band steering enabled (optimize client roaming)
- Fast roaming (802.11r) enabled
- Minimum data rate: 6 Mbps (2.4 GHz and 5 GHz)
- RADIUS authentication via FreeIPA (192.168.40.25)
- Per-user VLAN assignment capable
- RADIUS accounting enabled

**Use Case:** Primary network for trusted personal devices with strong authentication

---

### SSID: Homelab-IoT (VLAN 20)

**Security Level:** Medium  
**Authentication:** WPA2-PSK  
**Encryption:** AES-CCMP  
**PMF (802.11w):** Optional  

**Features:**
- Client isolation enabled (devices cannot see each other)
- Layer 2 isolation enabled
- Minimum data rate: 1 Mbps (2.4 GHz only - IoT compatibility)
- Band steering disabled (many IoT devices are 2.4 GHz only)
- Scheduled access: 6:00 AM - 11:00 PM daily
- Pre-shared key rotation: Quarterly

**Use Case:** Smart home devices with restricted network access

---

### SSID: Homelab-Guest (VLAN 30)

**Security Level:** Low  
**Authentication:** Open with Captive Portal  
**Encryption:** None (Open Network)  

**Features:**
- Captive portal with password authentication
- Client isolation enabled
- Layer 2 isolation enabled
- Bandwidth limit: 10 Mbps download / 5 Mbps upload per client
- Content filtering enabled (adult, gambling, malware, phishing)
- Safe search enforced
- Session timeout: 4 hours
- Minimum data rate: 1 Mbps (2.4 GHz), 6 Mbps (5 GHz)

**Use Case:** Visitor access with complete network isolation

---

## Channel Planning

### 2.4 GHz Band
- **Living Room AP:** Channel 1 (Non-overlapping)
- **Office AP:** Channel 6 (Non-overlapping)
- **Channel Width:** 20 MHz (reduced interference)
- **Transmit Power:** Auto (optimized by UniFi controller)

### 5 GHz Band
- **Living Room AP:** Channel 36 (UNII-1, Lower band)
- **Office AP:** Channel 149 (UNII-3, Upper band)
- **Channel Width:** 80 MHz (high throughput)
- **Transmit Power:** Auto (optimized by UniFi controller)

**Strategy:** Non-overlapping channels with spatial separation to minimize interference

---

## Network Services Configuration

### DHCP Service
- **Provider:** pfSense built-in DHCP server
- **Scope:** Per-VLAN configuration
- **Static Mappings:** Critical infrastructure and servers
- **Lease Times:** 
  - Trusted: 24 hours
  - IoT: 24 hours
  - Guest: 1 hour
  - Servers: 24 hours (mostly static)
  - DMZ: 24 hours

### DNS Service
- **Provider:** Unbound (pfSense DNS Resolver)
- **Local Domain:** homelab.local
- **DNSSEC:** Enabled
- **DNS Forwarding:** Enabled (1.1.1.1, 8.8.8.8)
- **Registration:** DHCP static mappings and leases registered
- **Cache:** Optimized for performance
- **Privacy:** Identity and version hidden

### VPN Service
- **Type:** OpenVPN (Remote Access)
- **Protocol:** UDP
- **Port:** 1194
- **Encryption:** AES-256-GCM
- **Authentication:** SHA256
- **Tunnel Network:** 10.8.0.0/24
- **Access:** Trusted (VLAN 10) and Servers (VLAN 40) networks
- **Max Clients:** 10 concurrent

### IPS/IDS Service
- **Provider:** Suricata
- **Interfaces Monitored:**
  - WAN (all inbound traffic)
  - DMZ (public-facing services)
- **Mode:** IPS (Inline blocking)
- **Rulesets:** Emerging Threats (threats, malware, exploits, scans)
- **Auto-update:** Daily

### Traffic Shaping
- **Scheduler:** HFSC (Hierarchical Fair Service Curve)
- **Queues:**
  - VoIP/Real-time: 20% (Priority 7)
  - Default Traffic: 60% (Priority 3)
  - Bulk Downloads: 20% (Priority 1)

---

## Backup and Disaster Recovery

### Configuration Backups
- **pfSense:** Automatic daily backups to 192.168.40.20 (TrueNAS)
- **UniFi Controller:** Automatic daily backups (7-day retention)
- **Retention Policy:** 7 daily, 4 weekly, 12 monthly

### Recovery Procedures
1. **pfSense Failure:** Restore from config backup, re-apply licenses
2. **Switch Failure:** Replace hardware, adopt in UniFi Controller
3. **AP Failure:** Replace hardware, adopt in UniFi Controller

### Documentation Updates
- **Frequency:** After any configuration change
- **Repository:** Git repository with version control
- **Review Schedule:** Quarterly

---

## Maintenance Schedule

### Daily
- Monitor Suricata alerts
- Review DHCP lease usage
- Check VPN access logs

### Weekly
- Review firewall logs for anomalies
- Check bandwidth utilization per VLAN
- Verify backup completion

### Monthly
- Update Suricata rulesets
- Review and rotate guest network password
- Audit static DHCP mappings
- Test VPN connectivity

### Quarterly
- Update pfSense to latest stable
- Update UniFi firmware
- Review and adjust firewall rules
- Rotate IoT network PSK
- Security audit and penetration testing

---

## Contact Information

**Network Administrator:** Samuel Jackson  
**Emergency Contact:** [On-Call Phone]  
**Documentation Repository:** https://github.com/homelab/network-docs  
**Last Updated:** November 5, 2025

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2025-11-05 | 1.0 | Initial comprehensive documentation | Samuel Jackson |
