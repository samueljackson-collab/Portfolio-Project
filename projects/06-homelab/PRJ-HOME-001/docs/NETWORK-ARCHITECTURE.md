# Home Network Architecture (PRJ-HOME-001)

## Executive Summary
- **Network Size & Scale**: 6 VLANs (Mgmt, Trusted, IoT, Guest, Servers, Cameras), ~85 active devices (peak 110), 6 routed subnets, 1 WAN uplink, 1 core gateway, 1 distribution switch, 3 access points, 4 PoE cameras, 3 hypervisor/servers.
- **Design Principles**: Security-zone segmentation (Trusted, Restricted, Isolated), default-deny with explicit allows, microsegmentation for IoT and cameras, PoE power budgeting, standardized port profiles, and controller-based management via UniFi Dream Machine Pro (UDMP).
- **Technology Stack**: UniFi ecosystem (UDMP gateway/controller + USW-24-POE + U6-Pro access points), UniFi Protect NVR, IDS/IPS with DPI, VLAN-backed WLANs, DHCP/DNS on UDMP, Cloudflare/OpenDNS upstream DNS.
- **Capacity & Growth**: Current utilization ~55% switch port count, 63% PoE budget, <40% WLAN client capacity; designed for +50% device growth (adds 1 AP + 2 servers) without rearchitecture. 1 Gbps WAN with option for second WAN/SFP+ for failover; single SFP+ uplink reserved for future 10G backhaul.

## Physical Infrastructure

### Internet Edge
- **ISP Connection**: Comcast cable, 1 Gbps down / 35 Mbps up, single coax drop; SLA: residential, typical 99.5% monthly availability.
- **Redundancy**: No secondary ISP; failover design path reserved via UDMP WAN2/SFP+ for LTE/5G modem.
- **Modem/ONT**: Arris SB8200 DOCSIS 3.1, dual Ethernet outputs (one used), bridge mode enabled, local mgmt 192.168.100.1.
- **WAN IP Addressing**: Dynamic public IPv4 via DHCP (sticky lease ~30 days); IPv6 prefix delegation /60, not currently used internally.

### Core Network Equipment

#### UniFi Dream Machine Pro (UDMP)
- **Model**: UDM-Pro
- **Role**: Router, gateway, UniFi Network/Protect controller, firewall, IDS/IPS, DHCP/DNS server, VPN termination.
- **Specifications**:
  - 1x 1 Gbps RJ45 WAN, 1x SFP+ WAN2 (unused), 8x LAN (1x SFP+) switching fabric.
  - Built-in IDS/IPS hardware offload.
  - NVR bay with 8TB HDD for Protect (camera storage ~14 days retention @ 4 cams / 1080p / medium bitrate).
- **Management IP**: 192.168.1.1 (VLAN 1 interface).
- **Firmware Version**: 3.2.12 (documented from latest update as of 2024-11-10).
- **Configuration**:
  - **WAN**: DHCP, hostname `udmp-home`, MTU 1500, IPv6 PD disabled, UPnP disabled, Threat Management enabled in IDS/IPS mode (balanced ruleset), Geo-IP block high-risk countries.
  - **Internal Networks**: VLAN interfaces for 1/10/20/30/40/50 with DHCP enabled per scopes below.
  - **Threat Management**: IDS/IPS on WAN in block mode; LAN in alert-only; Auto-update signatures daily 03:00.
  - **DPI**: Enabled for all VLANs; categories blocked on Guest (P2P, Adult); monitored on others.

### Switching Infrastructure

#### UniFi Switch 24 PoE (Primary Distribution)
- **Model**: USW-24-POE
- **Location**: Rack position 15U (4-post rack), front-facing patch panel above.
- **Role**: Primary distribution for wired endpoints and PoE delivery.
- **Specifications**: 24x 1G RJ45, 16x PoE+ (802.3at, 30W/port), 2x SFP uplinks, 95W PoE budget.
- **Management IP**: 192.168.1.10 (VLAN 1).
- **Port Configuration**: See [Switch Port Map](./SWITCH-PORT-MAP.md) for per-port VLANs and profiles.
- **PoE Devices**: 3x APs (15.4W/13.2W/14.1W), 4x cameras (4.2W/3.8W/4.5W/5.1W); total 60.3W.

### Wireless Infrastructure

#### AP-1: UniFi 6 Professional (Office)
- **Model**: U6-Pro
- **Location**: Office ceiling (center), covers ~800 sq ft including hallway.
- **Capabilities**: WiFi 6, dual-band, 4x4 MU-MIMO, 300+ clients max.
- **Management IP**: 192.168.1.20.
- **SSIDs**: HomeNetwork-5G (VLAN10), IoT (VLAN20), Guest (VLAN30).
- **Channel Config**: 2.4GHz Ch11 20MHz @10 dBm; 5GHz Ch149 80MHz @22 dBm.
- **Connected Devices**: 8-12 typical (peak 20).

#### AP-2: UniFi 6 Professional (Living Room)
- **Model**: U6-Pro
- **Location**: Living room ceiling, covers living/kitchen (~900 sq ft).
- **Management IP**: 192.168.1.21.
- **SSIDs**: HomeNetwork-5G (VLAN10), IoT (VLAN20), Guest (VLAN30).
- **Channel Config**: 2.4GHz Ch1 20MHz @10 dBm; 5GHz Ch36 80MHz @20 dBm.
- **Connected Devices**: 10-15 typical (peak 25).

#### AP-3: UniFi 6 Professional (Bedroom)
- **Model**: U6-Pro
- **Location**: Master bedroom ceiling, covers bedrooms (~700 sq ft) and garage edge.
- **Management IP**: 192.168.1.22.
- **SSIDs**: HomeNetwork-5G (VLAN10), IoT (VLAN20), Guest (VLAN30).
- **Channel Config**: 2.4GHz Ch6 20MHz @8 dBm; 5GHz Ch149 80MHz @18 dBm.
- **Connected Devices**: 6-10 typical (peak 15).

## Logical Network Architecture

### VLAN Configuration Table
| VLAN ID | VLAN Name | Subnet | Gateway | DHCP Range | Purpose | Security Zone | Devices |
|---------|-----------|--------|---------|------------|---------|---------------|---------|
| 1 | Management | 192.168.1.0/24 | 192.168.1.1 | .100-.199 | Network infrastructure management | Trusted-Admin | UDMP, Switches, APs |
| 10 | Trusted | 192.168.10.0/24 | 192.168.10.1 | .100-.249 | Primary user devices | Trusted | Workstations, phones, tablets |
| 20 | IoT | 192.168.20.0/24 | 192.168.20.1 | .100-.249 | Smart home devices | Restricted | Smart speakers, lights, sensors |
| 30 | Guest | 192.168.30.0/24 | 192.168.30.1 | .100-.249 | Visitor devices | Isolated | Guest phones, tablets |
| 40 | Servers | 192.168.40.0/24 | 192.168.40.1 | .10-.99 | Infrastructure servers | Trusted-Services | Proxmox hosts, NAS |
| 50 | Cameras | 192.168.50.0/24 | 192.168.50.1 | .100-.249 | Security cameras | Isolated | IP cameras |

### VLAN 1: Management Network
#### Purpose
Management plane for infrastructure devices (UDMP, switches, APs, out-of-band IPMI). No user endpoints.

#### Security Posture
- Trust Level: Highest (admin only). Internet egress limited to updates.
- Inbound: ESTABLISHED/RELATED only; SSH/HTTPS permitted from Trusted VLAN.
- Outbound: Firmware updates, NTP, DNS allowed; all else denied.

#### IP Address Management
- Subnet: 192.168.1.0/24; Gateway: 192.168.1.1
- DHCP Scope: .100-.199 for temp devices; static for infra: UDMP .1, switch .10, APs .20-.22.
- Utilization: ~15 addresses (<10% of scope).

#### Static IP Assignments
| IP | Hostname | MAC | Device Type | Notes |
|----|----------|-----|-------------|-------|
| 192.168.1.1 | udmp | xx:xx:xx:xx:xx:01 | Gateway/Controller | Default route, DNS, DHCP|
| 192.168.1.10 | usw24poe | xx:xx:xx:xx:xx:10 | Switch | PoE core |
| 192.168.1.20 | ap-office | xx:xx:xx:xx:xx:20 | AP | Uplink port 13 |
| 192.168.1.21 | ap-lr | xx:xx:xx:xx:xx:21 | AP | Uplink port 14 |
| 192.168.1.22 | ap-br | xx:xx:xx:xx:xx:22 | AP | Uplink port 15 |

#### Firewall Rules
- Inbound: Allow ESTABLISHED/RELATED; Allow HTTPS/SSH from VLAN10; Deny all else (log).
- Outbound: Allow DNS/NTP/HTTPS; Deny all other destinations (log critical).

### VLAN 10: Trusted Network
(See detailed profile below.)

#### Purpose
Primary network for trusted personal devices including workstations, personal phones, tablets, and development laptops. Devices have broad access to servers and printers.

#### Security Posture
- Trust Level: High. Internet access unrestricted via NAT.
- Inbound: ESTABLISHED/RELATED only; HTTP/HTTPS/SMB from Servers; SSH from Management.
- Outbound: Allow Internet; allow Servers (full); allow Mgmt (SSH/HTTPS/HTTP); deny IoT/Guest/Cameras.
- DNS Servers: 192.168.1.1, 1.1.1.1, 8.8.8.8 (served via UDMP with forwarding).

#### IP Address Management
- Subnet: 192.168.10.0/24; Gateway: 192.168.10.1.
- DHCP: 192.168.10.100-249; Lease 86400s; domain home.local; NTP 192.168.1.1.
- Reserved: .2-.99 for statics. Utilization: ~45 devices (~30%).

#### Static Assignments
| IP | Hostname | MAC | Device | Notes |
|----|----------|-----|--------|-------|
| 192.168.10.10 | workstation-01 | xx:xx:xx:xx:10:10 | Desktop | Primary dev |
| 192.168.10.11 | laptop-01 | xx:xx:xx:xx:10:11 | Laptop | Mobile dev |
| 192.168.10.50 | printer-office | xx:xx:xx:xx:10:50 | Printer | HP LaserJet |

#### Firewall Rules (Inter-VLAN)
Inbound to VLAN10:
1. Allow ESTABLISHED/RELATED from ANY
2. Allow HTTP/HTTPS from VLAN40 (servers)
3. Allow SMB (139,445) from VLAN40
4. Allow SSH from VLAN1 (mgmt)
5. Deny all (log)

Outbound from VLAN10:
1. Allow Internet (any)
2. Allow VLAN40 (all)
3. Allow VLAN1 ports 22,80,443
4. Deny to VLAN20
5. Deny to VLAN30
6. Deny to VLAN50

#### WiFi SSID Mapping
- SSID "HomeNetwork-5G" tagged to VLAN10, WPA3-Personal, 5GHz-only, key stored in 1Password.

#### Monitoring & Maintenance
- DPI enabled; alerts for new device, suspicious traffic, sustained >500 Mbps.
- Review quarterly; change control via Git commits.

### VLAN 20: IoT Network
- **Purpose**: Segregate untrusted smart-home devices; allow cloud control while preventing lateral movement.
- **Security Posture**: Restricted. Inbound limited to ESTABLISHED/RELATED and discovery/control from Trusted via mDNS/HTTP to specific hubs. Outbound limited to HTTP/HTTPS/DNS/NTP; RFC1918 blocked.
- **IPAM**: 192.168.20.0/24, gateway .1, DHCP .100-.249, reserve .2-.99; utilization ~25 devices (lights, speakers, thermostats).
- **Firewall Rules**:
  - Inbound: Allow ESTABLISHED/RELATED; Allow mDNS from VLAN10 (5353); Allow Home Assistant (8123) + Zigbee hub (8099) from VLAN10; Deny all.
  - Outbound: Allow HTTP/HTTPS (80/443) to Internet; Allow DNS (53); Allow NTP (123); Deny all RFC1918; Deny all else.
- **WiFi**: SSID "IoT" tagged VLAN20 (WPA2-Personal, unique key), broadcast on all APs.

### VLAN 30: Guest Network
- **Purpose**: Provide internet-only access for visitors.
- **Security Posture**: Isolated. Client isolation enabled; blocked to all RFC1918. Outbound limited to HTTP/HTTPS/DNS. Content filtering enabled (OpenDNS FamilyShield + DPI blocks P2P/Adult).
- **IPAM**: 192.168.30.0/24, gateway .1, DHCP .100-.249; utilization ~10 devices peak.
- **WiFi**: SSID "Guest" VLAN30 WPA2-Personal 16+ char, monthly rotation.

### VLAN 40: Servers Network
- **Purpose**: Host critical services (Proxmox, TrueNAS, NVR virtual machine if needed).
- **Security Posture**: Trusted-Services. Inbound allowed from Mgmt (SSH) and Trusted (user services). Outbound allowed to Internet for updates and to Mgmt for SNMP/monitoring.
- **IPAM**: 192.168.40.0/24, gateway .1; DHCP .10-.99; statics: Proxmox1 .10, Proxmox2 .11, TrueNAS .12; utilization ~8 addresses.
- **Firewall Rules**:
  - Inbound: Allow ESTABLISHED/RELATED; Allow SSH from VLAN1 & VLAN10; Allow HTTP/HTTPS/SMB/NFS from VLAN10; Allow Proxmox console (8006) from VLAN10; Deny all else.
  - Outbound: Allow Internet; Allow Mgmt (SNMP/SSH/HTTPS); Deny IoT/Guest/Cameras unless initiated.

### VLAN 50: Cameras Network
- **Purpose**: Isolate security cameras; only communicate with NVR/Protect.
- **Security Posture**: Isolated. No internet; only allowed to Servers VLAN for RTSP/HTTP to NVR. Outbound DNS/NTP allowed via UDMP for time sync.
- **IPAM**: 192.168.50.0/24, gateway .1; DHCP .100-.249; cameras static DHCP mapped: Front .110, Back .111, Garage .112, Driveway .113.
- **Firewall Rules**:
  - Inbound: Allow ESTABLISHED/RELATED; Allow RTSP (554) & HTTP (80) from VLAN40; Deny all else.
  - Outbound: Allow to VLAN40 ports 554/80; Allow DNS 53; Allow NTP 123; Deny Internet; Deny other VLANs.

## Inter-VLAN Routing Matrix
| Source VLAN | Destination VLAN | Allowed Services | Justification | Priority |
|-------------|------------------|------------------|---------------|----------|
| Trusted | Internet | All | Users require unrestricted internet | 100 |
| Trusted | Servers | HTTP/S, SSH, SMB, NFS | Access infrastructure services | 200 |
| Trusted | Management | HTTP/S, SSH | Admin access to network equipment | 300 |
| IoT | Internet | HTTP/S only | Cloud connectivity for IoT | 400 |
| Guest | Internet | HTTP/S only | Visitor internet access | 500 |
| All | IoT | Denied | Limit lateral movement to IoT devices | 1000 |
| All | Guest | Denied | Keep guest fully isolated | 1000 |
| Cameras | Servers | RTSP/HTTP only | Stream video to NVR | 210 |
| Servers | Management | SNMP/SSH/HTTPS | Monitoring and admin | 320 |

## Capacity & Growth Planning
- **Switch Ports**: 16/24 used; growth headroom 8 ports; plan: add second 24-port or 48-port with SFP+ if utilization >80%.
- **PoE Budget**: 60.3W of 95W; available 34.7W; enough for 1 AP + 3 cameras.
- **Wireless**: Client capacity ~300 per AP; current peak 30; can add U6-LR to garage if coverage gaps noted.
- **Routing Performance**: UDMP supports ~3.5 Gbps IDS/IPS; current WAN 1 Gbps <30% CPU under load.

## Monitoring, Logging, and Backups
- **Monitoring**: UniFi controller health checks; SNMP to TrueNAS/Influx (planned); syslog export to TrueNAS for long-term retention.
- **Backups**: UDMP automatic config backup nightly to TrueNAS; weekly offsite copy to cloud storage via rclone.
- **Alerts**: Push + email for critical (WAN down, device offline, IDS high severity); weekly summary reports archived.

## Change Management
- All configuration changes documented via Git in `/projects/06-homelab/PRJ-HOME-001/docs` with timestamps and rationales.
- Quarterly review of firewall rules and VLAN scopes; annual penetration-style assessment for segmentation.

## Disaster Recovery Notes
- If UDMP fails: replace with spare gateway using exported backup; restore config, verify DHCP scopes, firewall rules, VPN.
- If switch fails: move critical devices to spare 8-port PoE switch; trunk to UDMP; restore port profiles.
- If AP fails: swap with spare U6-Lite temporarily; adopt via UDMP; reassign SSIDs.
