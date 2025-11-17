# Home Network Architecture

## Executive Summary
- **Scale:** 6 VLANs, 25+ wired devices, 30+ wireless clients.
- **Design Principles:** Security zoning, VLAN segmentation, centralized UniFi management, and capacity headroom for growth.
- **Technology Stack:** UniFi Dream Machine Pro (routing/firewall/controller), UniFi Switch 24 PoE distribution, UniFi WiFi 6 access points, Proxmox/TrueNAS servers.
- **Growth:** Spare PoE budget and trunk ports reserved for additional APs/cameras; subnetting allows ~150 DHCP leases per user zone.

## Physical Infrastructure
### Internet Edge
- **ISP:** Comcast 1 Gbps/35 Mbps cable
- **Modem:** Arris SB8200 (DOCSIS 3.1)
- **WAN IP:** Dynamic; DDNS configured on UDMP
- **Redundancy:** Single link, UPS-backed power

### UniFi Dream Machine Pro (UDMP)
- **Role:** Router, Gateway, Controller, NVR
- **Specs:** 1 Gbps WAN, 8x LAN (1 SFP+), IDS/IPS
- **Mgmt IP:** 192.168.1.1
- **WAN Config:** DHCP from ISP, DDNS enabled
- **Internal Networks:** VLANs 1/10/20/30/40/50
- **Threat Management:** IDS/IPS on, balanced profile
- **DPI:** Enabled for visibility

### UniFi Switch 24 PoE (Primary Distribution)
- **Model:** USW-24-POE, rack position 15U
- **Mgmt IP:** 192.168.1.10
- **PoE Budget:** 95W (63% used)
- **Port Configuration:** Access/trunk mapping documented in SWITCH-PORT-MAP.md
- **PoE Devices:** 3x APs, 4x cameras, 1x smart hub

### UniFi Access Points
- **AP-1 U6-Pro (Office):** 192.168.1.20, covers ~800 sqft, SSIDs HomeNetwork-5G (VLAN10), IoT (VLAN20), Guest (VLAN30)
- **AP-2 U6-Lite (Living Room):** 192.168.1.21, covers living area, same SSIDs
- **AP-3 U6-Pro (Bedroom):** 192.168.1.22, bedroom coverage, same SSIDs

## Logical Network Architecture
### VLAN Table
| VLAN ID | VLAN Name | Subnet | Gateway | DHCP Range | Purpose | Security Zone | Devices |
|---------|-----------|--------|---------|------------|---------|---------------|---------|
| 1 | Management | 192.168.1.0/24 | 192.168.1.1 | .100-.199 | Network infrastructure mgmt | Trusted-Admin | UDMP, Switches, APs |
| 10 | Trusted | 192.168.10.0/24 | 192.168.10.1 | .100-.249 | Primary user devices | Trusted | Workstations, phones, tablets |
| 20 | IoT | 192.168.20.0/24 | 192.168.20.1 | .100-.249 | Smart home devices | Restricted | Speakers, lights, sensors |
| 30 | Guest | 192.168.30.0/24 | 192.168.30.1 | .100-.249 | Visitor devices | Isolated | Guest phones, tablets |
| 40 | Servers | 192.168.40.0/24 | 192.168.40.1 | .10-.99 | Infrastructure servers | Trusted-Services | Proxmox, NAS |
| 50 | Cameras | 192.168.50.0/24 | 192.168.50.1 | .100-.249 | Security cameras | Isolated | IP cameras |

### VLAN 10: Trusted Network
- **Purpose:** Primary network for owned devices with broad access.
- **Security:** High trust; inbound limited to established traffic plus management/servers.
- **IPAM:** Gateway 192.168.10.1; DHCP 100-249; reserved 2-99 for statics.
- **DHCP Options:** DNS 192.168.1.1; NTP 192.168.1.1; domain home.local.
- **Static Assignments:** 192.168.10.10 workstation-01; 192.168.10.11 laptop-01; 192.168.10.50 printer-office.
- **Firewall Inbound:** allow ESTABLISHED/RELATED; allow HTTP/HTTPS/SMB/SSH from Servers/Management; deny rest.
- **Outbound:** allow Internet, Servers, Management; deny IoT/Guest/Cameras.
- **WiFi SSID:** HomeNetwork-5G WPA3 mapped to VLAN10.
- **Monitoring:** Alerts for new device, high bandwidth >500Mbps.

### VLAN 20: IoT
- **Purpose:** Segregate less-trusted devices.
- **Security:** Restricted; outbound HTTP/S + DNS/NTP; inbound only mDNS and specific control ports from Trusted.
- **IPAM:** 192.168.20.0/24 gateway .1; DHCP 100-249; reserved 2-99.
- **Firewall:** Deny RFC1918 outbound; allow Internet HTTP/S; allow discovery/control from Trusted.
- **WiFi SSID:** IoT WPA2 mapped to VLAN20.

### VLAN 30: Guest
- **Purpose:** Isolated visitor access.
- **Security:** Internet only; client isolation on APs.
- **IPAM:** 192.168.30.0/24 gateway .1; DHCP 100-249.
- **Firewall:** Allow HTTP/S + DNS to WAN; deny all RFC1918.
- **Bandwidth:** 25/10 Mbps per-client shaping.

### VLAN 40: Servers
- **Purpose:** Infrastructure services (Proxmox, TrueNAS).
- **Security:** Admin access from Management; user services from Trusted; no IoT/Guest reach.
- **IPAM:** 192.168.40.0/24 gateway .1; DHCP 10-99 for statics.
- **Firewall:** Allow SSH/HTTPS/SMB/NFS from Trusted/Management; allow monitoring from Management; deny Internet inbound.

### VLAN 50: Cameras
- **Purpose:** CCTV isolation.
- **Security:** Cameras talk only to NVR; no Internet.
- **IPAM:** 192.168.50.0/24 gateway .1; DHCP 100-249.
- **Firewall:** Allow RTSP/HTTP from Servers; deny outbound Internet; allow DNS/NTP.

### Inter-VLAN Routing Matrix
| Source VLAN | Destination VLAN | Allowed Services | Business Justification | Rule Priority |
|-------------|------------------|------------------|------------------------|---------------|
| Trusted | Internet | All | User internet access | 100 |
| Trusted | Servers | HTTP/S, SSH, SMB, NFS | Access to services | 200 |
| Trusted | Management | HTTP/S, SSH | Admin UI/SSH | 300 |
| IoT | Internet | HTTP/S only | Cloud connectivity | 400 |
| Guest | Internet | HTTP/S only | Guest browsing | 500 |
| ALL | IoT | Denied | Restrict lateral movement | 1000 |
| ALL | Guest | Denied | Isolate guest devices | 1000 |

## Diagram Specifications
See `docs/diagrams/network-topology-description.md` for detailed physical and logical diagram guidance including color codes, grouping, and annotations.
