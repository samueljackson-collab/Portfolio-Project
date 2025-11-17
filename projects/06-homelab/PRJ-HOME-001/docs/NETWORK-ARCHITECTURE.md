# Home Network Architecture

## Executive Summary
- Scale: 6 VLANs, ~80 devices across Proxmox servers, APs, IoT, and cameras.
- Design principles: segmentation by trust (Trusted/IoT/Guest/Servers/Cameras/Management), defense-in-depth with UDMP firewall, PoE budgeting, and redundancy via multiple APs.
- Stack: UniFi Dream Machine Pro gateway/controller, UniFi Switch 24 PoE distribution, multiple UniFi 6 APs.
- Growth plan: spare PoE budget (37%) and open ports for additional AP/camera deployments.

## Physical Infrastructure

### Internet Edge
- ISP: Comcast 1 Gbps down / 35 Mbps up; DOCSIS over coax.
- Modem: Arris SB8200; bridge mode; WAN IP dynamic.
- UDMP WAN port connected via Cat6 to modem; IDS/IPS enabled.

### UniFi Dream Machine Pro (UDMP)
- **Model**: UDM-Pro
- **Role**: Router, Gateway, Controller, Protect NVR
- **Specs**: 1 Gbps WAN, 8x LAN (1 SFP+), IDS/IPS hardware offload
- **Mgmt IP**: 192.168.1.1
- **Firmware**: 3.2.x (document exact on audit)
- **Config**: WAN DHCP, LAN networks for VLANs 1/10/20/30/40/50, Threat Mgmt IDS/IPS enabled, DPI categories monitored.

### UniFi Switch 24 PoE (Primary Distribution)
- **Model**: USW-24-POE
- **Location**: Rack 15U
- **Role**: Primary distribution for wired + PoE
- **Specs**: 24x1G (16 PoE+), 2x SFP, PoE budget 95W
- **Mgmt IP**: 192.168.1.10
- **Port Config**: Port profiles per VLAN table (see SWITCH-PORT-MAP.md)
- **PoE Devices**: APs and cameras documented per port.

### UniFi Access Points
#### AP-1: UniFi 6 Professional (Office)
- Location: Office ceiling
- Coverage: ~800 sq ft
- Mgmt IP: 192.168.1.20
- SSIDs: HomeNetwork-5G (VLAN10), IoT (VLAN20), Guest (VLAN30)
- Channels: 2.4GHz ch1 20MHz 10dBm, 5GHz ch149 80MHz 22dBm
- Typical clients: 10-12

#### AP-2: UniFi 6 Lite (Living Room)
- Mgmt IP: 192.168.1.21
- Coverage: Living areas
- Channels: 2.4GHz ch6 20MHz 12dBm, 5GHz ch36 80MHz 20dBm
- Typical clients: 8-10

#### AP-3: UniFi 6 Lite (Bedroom)
- Mgmt IP: 192.168.1.22
- Coverage: Bedrooms
- Channels: 2.4GHz ch11 20MHz 10dBm, 5GHz ch149 80MHz 18dBm
- Typical clients: 6-8

## Logical Network Architecture

### VLAN Table
| VLAN ID | VLAN Name   | Subnet          | Gateway       | DHCP Range         | Purpose                        | Security Zone      | Devices |
|--------|-------------|-----------------|---------------|--------------------|--------------------------------|--------------------|---------|
| 1      | Management  | 192.168.1.0/24  | 192.168.1.1   | .100-.199          | Network infrastructure admin   | Trusted-Admin      | UDMP, Switch, APs |
| 10     | Trusted     | 192.168.10.0/24 | 192.168.10.1  | .100-.249          | Personal devices               | Trusted            | Workstations, phones |
| 20     | IoT         | 192.168.20.0/24 | 192.168.20.1  | .100-.249          | Smart home devices             | Restricted         | Speakers, lights |
| 30     | Guest       | 192.168.30.0/24 | 192.168.30.1  | .100-.249          | Visitor internet               | Isolated           | Guest devices |
| 40     | Servers     | 192.168.40.0/24 | 192.168.40.1  | .10-.99            | Infrastructure servers         | Trusted-Services   | Proxmox, NAS |
| 50     | Cameras     | 192.168.50.0/24 | 192.168.50.1  | .100-.249          | Security cameras               | Isolated           | IP cameras |

### VLAN 10: Trusted Network (example)
- Purpose: personal devices with broad access.
- Security posture: outbound unrestricted, inbound restricted to ESTABLISHED/RELATED, SSH/HTTP/S to management/servers.
- IPAM: gateway 192.168.10.1, DHCP 100-249, static 2-99.
- Firewall: allow to Internet, allow HTTP/S+SMB+SSH to Servers, allow SSH/HTTPS to Management, deny to IoT/Guest/Cameras.
- WiFi SSID: HomeNetwork-5G (WPA3, VLAN10).
- Typical devices: ~30 peak.
- Monitoring: alerts for new device joins and high bandwidth >500 Mbps sustained.

*Apply equivalent detail for VLANs 1,20,30,40,50 following same pattern above.*

### Inter-VLAN Routing Matrix
| Source VLAN | Destination VLAN | Allowed Services                | Business Justification                      | Rule Priority |
|-------------|------------------|---------------------------------|---------------------------------------------|---------------|
| Trusted     | Internet         | All                             | User browsing                               | 100 |
| Trusted     | Servers          | HTTP/S, SSH, SMB, NFS           | Access infrastructure services              | 200 |
| Trusted     | Management       | HTTP/S, SSH                     | Admin management                            | 300 |
| IoT         | Internet         | HTTP/S only                     | Cloud connectivity                          | 400 |
| Guest       | Internet         | HTTP/S only                     | Visitor access                              | 500 |
| ALL         | IoT              | Denied                          | Reduce lateral movement                     | 1000 |
| ALL         | Guest            | Denied                          | Complete isolation                          | 1000 |

## Notes
- Change control: update Git docs for any VLAN/firewall changes.
- Capacity: DHCP scopes sized at ~60% utilization to allow growth.
- Redundancy: multiple APs with staggered channels; PoE budget reserved.
