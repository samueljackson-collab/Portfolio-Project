# Homelab Network Architecture

## Executive Summary
- **Scale**: 6 VLANs, 1 core router, 1 distribution switch, 3 wireless APs, and 4 Proxmox/TrueNAS servers.
- **Design Principles**: Security zones with strict inter-VLAN ACLs, PoE budget tracking, and redundant storage paths. Segmentation contains IoT and guest traffic away from trusted assets.
- **Technology Stack**: UniFi Dream Machine Pro gateway/controller, UniFi Switch 24 PoE, UniFi 6 access points, and Proxmox/TrueNAS servers.
- **Growth Plan**: Spare trunk/PoE capacity allows additional AP and cameras; subnets sized /24 with reserved static ranges.

## Physical Infrastructure

### Internet Edge
- **ISP**: Comcast 1 Gbps/35 Mbps DOCSIS connection with Arris SB8200 modem.
- **WAN IP**: Dynamic DHCP; DDNS enabled on UDMP for remote VPN.
- **Resilience**: Surge protector and UPS-backed rack; failover supported via UDMP dual WAN if secondary link added.

### UniFi Dream Machine Pro (UDMP)
- **Role**: Router, firewall, UniFi controller, UniFi Protect NVR.
- **Specs**: 1 Gbps WAN, 8x1G LAN (1x SFP+), IDS/IPS capable.
- **Management IP**: 192.168.1.1
- **Config Highlights**: VLAN interfaces for all segments, DPI enabled, IDS/IPS balanced profile, DHCP services per subnet.

### UniFi Switch 24 PoE (Primary Distribution)
- **Location**: Rack 15U; management IP 192.168.1.10.
- **Specs**: 24x1G, 16 PoE+ ports, 2 SFP uplinks, 95W PoE budget.
- **Port Plan**: Ports 1-8 Trusted access, 9-12 Servers, 13-16 AP trunks, 17-20 Cameras, 21 IoT, 22 Printer, 23 uplink to UDMP, 24 spare trunk.
- **PoE Devices**: Three APs plus four cameras; 60W used of 95W budget.

### Wireless Infrastructure
- **AP-Office (U6-Pro)**: Office ceiling, VLANs 1/10/20/30, management IP 192.168.1.20, channels 149 (5GHz) and auto 2.4GHz.
- **AP-LivingRoom (U6-Pro)**: Living room ceiling, trunk port 14, balanced power, 5GHz channel 36.
- **AP-Bedroom (U6-Lite)**: Bedroom, trunk port 15, 5GHz channel 149, low power for minimal bleed.

### Servers
- **Proxmox-01/02** on VLAN 40 with static IPs 192.168.40.10/11.
- **TrueNAS** on VLAN 40 static 192.168.40.20 for NFS/SMB storage.

## Logical Network Architecture

### VLAN Table
| VLAN ID | VLAN Name | Subnet | Gateway | DHCP Range | Purpose | Security Zone | Devices |
|---------|-----------|--------|---------|------------|---------|---------------|---------|
| 1 | Management | 192.168.1.0/24 | 192.168.1.1 | .100-.199 | Network infrastructure management | Trusted-Admin | UDMP, Switches, APs |
| 10 | Trusted | 192.168.10.0/24 | 192.168.10.1 | .100-.249 | Primary user devices | Trusted | Workstations, phones, tablets |
| 20 | IoT | 192.168.20.0/24 | 192.168.20.1 | .100-.249 | Smart home devices | Restricted | Speakers, lights, sensors |
| 30 | Guest | 192.168.30.0/24 | 192.168.30.1 | .100-.249 | Visitor devices | Isolated | Guest phones, tablets |
| 40 | Servers | 192.168.40.0/24 | 192.168.40.1 | .10-.99 | Infrastructure servers | Trusted-Services | Proxmox, NAS |
| 50 | Cameras | 192.168.50.0/24 | 192.168.50.1 | .100-.249 | Security cameras | Isolated | IP cameras |

### VLAN 10: Trusted Network
- **Purpose**: Daily-use devices needing broad access.
- **Security**: Inbound limited to established traffic; SSH/HTTPS allowed from Management; outbound unrestricted except IoT/Guest/Cameras denied.
- **DHCP**: 192.168.10.100-249, 24h lease, DNS 192.168.1.1/1.1.1.1/8.8.8.8.
- **Static IPs**: 192.168.10.10 workstation-01, 10.11 laptop-01, 10.50 printer-office.
- **Firewall**: Allow HTTP/S + SMB to Servers, SSH to Management, deny rest inbound.
- **WiFi**: SSID HomeNetwork-5G (VLAN 10) WPA3-Personal.

### VLAN 20: IoT
- **Purpose**: Contain smart devices with cloud dependencies.
- **Security**: Inbound only established/mDNS/controlled app ports from Trusted; outbound HTTP/HTTPS/DNS/NTP; RFC1918 blocked.
- **DHCP**: 192.168.20.100-249, 12h lease.
- **Firewall**: Deny lateral movement to Trusted/Guest/Servers; allow minimal control from Trusted via Home Assistant.

### VLAN 30: Guest
- **Purpose**: Isolated internet-only access for visitors.
- **Security**: Client isolation enabled; outbound limited to HTTP/HTTPS/DNS; RFC1918 blocked.
- **DHCP**: 192.168.30.100-249.
- **Firewall**: Deny all inter-VLAN; allow internet only.

### VLAN 40: Servers
- **Purpose**: Proxmox, TrueNAS, and monitoring stack.
- **Security**: SSH from Management/Trusted, HTTP/S/SMB/NFS to Trusted, internet allowed for updates.
- **DHCP/Static**: Mostly static assignments .10-.30; DHCP for test VMs .50-.99.
- **Firewall**: Deny access to Guest/IoT/Cameras.

### VLAN 50: Cameras
- **Purpose**: Video surveillance, isolated from internet.
- **Security**: Allow RTSP/HTTP from Servers VLAN only; DNS/NTP allowed; internet denied.
- **Firewall**: Enforce one-way access to NVR; block all else.

### Inter-VLAN Matrix
| Source VLAN | Destination VLAN | Allowed Services | Business Justification | Rule Priority |
|-------------|------------------|------------------|------------------------|---------------|
| Trusted | Internet | All | Users need browsing/API access | 100 |
| Trusted | Servers | HTTP/S, SSH, SMB, NFS | Access infrastructure services | 200 |
| Trusted | Management | SSH, HTTPS | Admin access to gear | 300 |
| IoT | Internet | HTTP/S | Cloud control | 400 |
| Guest | Internet | HTTP/S | Guest internet | 500 |
| All | IoT | Deny | Prevent lateral movement | 1000 |
| All | Guest | Deny | Enforce isolation | 1000 |
| Cameras | Servers | RTSP/HTTP | Stream to NVR | 250 |

## Diagram Guidance
See `diagrams/network-topology-description.md` for rendering instructions covering physical and logical layouts, color keys, and annotations.

## Monitoring & Alerting
- UDMP DPI and IDS/IPS enabled with automatic signature updates.
- NetFlow exports to monitoring stack; alerts on new device join, WAN failover, and PoE overload.

## Maintenance Notes
- Config backups exported nightly from UDMP to TrueNAS via SCP.
- Quarterly review of firewall rules and DHCP scopes; monthly firmware checks for UDMP and switch/APs.
