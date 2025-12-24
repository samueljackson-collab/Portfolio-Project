# Homelab Network Architecture (PRJ-HOME-001)

## Executive Summary
- **Size & Scale**: Single-location homelab in a two-floor residence; 1× 12U rack, 1× wall-mount patch panel, ~45 active clients (15 wired, 30 wireless), peak simultaneous clients ~28, sustained WAN throughput ~850 Mbps on a 1 Gbps symmetrical fiber circuit.
- **Design Principles**: Layered segmentation (management/trusted/IoT/guest/lab), default deny with explicit allow, minimize east-west trust, WPA3/802.1X where possible, observability-first (NetFlow/DPI, syslog, SNMP), and change-controlled backups before edits.
- **Stack**: UniFi Dream Machine Pro (UniFi OS 4.0.6, Network 8.3.32), UniFi Switch 24 PoE Gen2 (v6.6.82), UniFi Switch 8 PoE (v6.6.82), three UniFi 6 Long-Range APs (U6-LR, v6.5.39), Pi-hole on Raspberry Pi 4 for DNS, TrueNAS for storage, Proxmox host for virtualization.
- **Capacity Targets**: WAN 1 Gbps symmetric; LAN backplane 24 Gbps switching fabric with 95 W PoE budget; APs tuned for 80 MHz @ 5 GHz (channel 149/36/157) and 20 MHz @ 2.4 GHz (channels 1/6/11) with medium TX power; VPN WireGuard 500 Mbps aggregate; DHCP scope sized for 60% headroom per VLAN.

## Physical Infrastructure
### ISP Edge
- **Carrier**: Fiber 1 Gbps symmetrical.
- **Public IP**: Static /30 assigned by ISP (203.0.113.10/30, gateway 203.0.113.9).
- **Service Demarcation**: SFP GPON ONT provided by ISP, operating in bridge mode to pass the public IP to CPE.

### Modem/ONT
- **Model**: Calix 844G ONT (bridge).
- **Physical**: SFP uplink to UDMP WAN; powered via UPS (600 VA).
- **Management**: Provider-managed; no local DHCP/NAT; heartbeat LED monitored by smart PDU.

### UniFi Dream Machine Pro (UDMP)
- **Firmware**: UniFi OS 4.0.6; UniFi Network Application 8.3.32.
- **WAN**: Port WAN (SFP) → ISP ONT; static IP 203.0.113.10/30; DNS 1.1.1.1/8.8.8.8; Smart Queues disabled (line rate).
- **LAN**: LAN1 (Port 1) → USW-24-PoE; LAN2 (Port 2) → USW-8-PoE (uplink failover).
- **Services**: DPI/Threat Mgmt (Balanced), GeoIP block (RU,CN,KP,IR,SY), WireGuard VPN (UDP/51820), L2TP disabled, SNMP v2c RO community `homelab-snmp`, syslog to 192.168.10.5:514 (TrueNAS).
- **Backups**: Nightly automatic backup to 192.168.10.5 via SMB share `\\truenas\unifi-backups`.

### Switching
- **Core**: UniFi Switch 24 PoE Gen2 (firmware 6.6.82) — uplink 1: Port 1 (Cat6a) to UDMP LAN1; uplink 2: Port 2 (Cat6a) to UDMP LAN2 (disabled by default; manual failover). PoE budget 95 W; fanless under 45°C.
- **Access**: UniFi Switch 8 PoE (firmware 6.6.82) — uplink 8 to UDMP LAN2; used for office lab bench and AP3.
- **Port Profiles**:
  - Trunk (All VLANs): Tagged 1/10/50/99/100, native VLAN 1.
  - Access-Trusted: VLAN 10 untagged; voice VLAN none.
  - Access-IoT: VLAN 50 untagged; block multicast except mDNS.
  - Access-Lab: VLAN 100 untagged.
  - Access-Guest: VLAN 99 untagged; client isolation enforced at WLAN.

### Wireless (UniFi APs)
- **AP Models/Firmware**: 3× U6-LR on firmware 6.5.39.
- **Placement**: AP1 (Living Room ceiling), AP2 (Primary Bedroom), AP3 (Office).
- **RF Design**: 5 GHz 80 MHz on channels 149/36/157; 2.4 GHz 20 MHz on 1/6/11; TX power medium; band steering on; minimum RSSI -75 dBm; BSS coloring enabled.
- **SSID to VLAN Mapping**:
  - `HL-Trusted` (WPA3-Personal, VLAN 10)
  - `HL-IoT` (WPA2-Personal, VLAN 50, mDNS reflector)
  - `HL-Guest` (WPA2-Personal + Guest Policy, VLAN 99, captive portal disabled, rate limit 10 Mbps/client)
  - `HL-Lab` (WPA2-Personal, VLAN 100, no band steering)

## Logical Architecture
### VLAN & Subnet Summary
| VLAN | Name | Subnet | Gateway | DHCP Pool | DNS | SSID/Port Profile |
|------|------|--------|---------|-----------|-----|-------------------|
| 1 | Management | 192.168.1.0/24 | 192.168.1.1 | None (static) | 192.168.10.2 / 1.1.1.1 | Trunk native |
| 10 | Trusted | 192.168.10.0/24 | 192.168.10.1 | 192.168.10.100-200 | 192.168.10.2 | `HL-Trusted` / Access-Trusted |
| 50 | IoT | 192.168.50.0/24 | 192.168.50.1 | 192.168.50.100-200 | 1.1.1.1 / 8.8.8.8 | `HL-IoT` / Access-IoT |
| 99 | Guest | 192.168.99.0/24 | 192.168.99.1 | 192.168.99.100-200 | 1.1.1.1 / 8.8.8.8 | `HL-Guest` / Access-Guest |
| 100 | Lab | 192.168.100.0/24 | 192.168.100.1 | 192.168.100.100-200 | 192.168.10.2 / 1.1.1.1 | `HL-Lab` / Access-Lab |

### VLAN Deep-Dive
#### VLAN 1 — Management (192.168.1.0/24)
- **Firewall Rules**:
  - Allow TCP 22/443/8443 from VLAN10 to VLAN1 (admin management).
  - Deny any from VLAN50/99/100 to VLAN1.
  - Allow WireGuard management from VPN subnet 10.10.10.0/24 to 192.168.1.0/24 TCP 22/443.
- **IPAM**: Static only; UDMP 192.168.1.1, USW24 192.168.1.2, USW8 192.168.1.3, AP1-3 192.168.1.10-12; reserve 192.168.1.50-254 for future.
- **DHCP**: Disabled on UDMP network definition.
- **SSID/Ports**: No SSID; management reachable only via wired trunk/native VLAN.
- **Monitoring**: SNMP enabled on UDMP and switches; syslog to 192.168.10.5; device heartbeat alerts in UniFi.

#### VLAN 10 — Trusted (192.168.10.0/24)
- **Firewall Rules**:
  - Allow any from VLAN10 to internet.
  - Allow TCP 22/443/8443 to VLAN1 (admin).
  - Allow any from VLAN10 to VLAN100 (lab) for testing.
  - Deny any from VLAN10 to VLAN99 (guest).
- **IPAM**: Gateway 192.168.10.1; static: 192.168.10.2 Pi-hole, 10.5 TrueNAS, 10.10 Proxmox, 10.30 Printer; reservations 10.20-10.22 (workstations/laptops), 10.40-10.41 (phones).
- **DHCP**: Pool 192.168.10.100-200; lease 24h; options 3 (192.168.10.1), 6 (192.168.10.2,1.1.1.1), 15 (homelab.local), 42 (192.168.1.1).
- **SSID/Ports**: `HL-Trusted` WPA3-Personal; Access-Trusted ports.
- **Monitoring**: NetFlow export to 192.168.10.5:2055; DPI enabled; Pi-hole query logging retained 90 days.

#### VLAN 50 — IoT (192.168.50.0/24)
- **Firewall Rules**:
  - Allow TCP 80/443 and UDP 53 from VLAN50 to internet.
  - Allow UDP 5353 and TCP 80/443 from VLAN10 to VLAN50 (control path).
  - Deny VLAN50 to VLAN1/10/99/100 (explicit isolation).
- **IPAM**: Gateway 192.168.50.1; statics 50.10 TV, 50.11 thermostat, 50.12-13 locks, 50.20-29 Hue, 50.30-31 cameras, 50.40-42 speakers.
- **DHCP**: Pool 192.168.50.100-200; lease 24h; DNS 1.1.1.1/8.8.8.8; mDNS reflector enabled.
- **SSID/Ports**: `HL-IoT` WPA2-Personal; Access-IoT ports with mDNS allowed, other multicast filtered.
- **Monitoring**: UniFi client insights with anomaly detection; camera uptime checks via HTTP GET from 192.168.10.2 every 5 minutes.

#### VLAN 99 — Guest (192.168.99.0/24)
- **Firewall Rules**:
  - Allow TCP 80/443 and UDP 53 from VLAN99 to internet.
  - Deny VLAN99 to RFC1918 (192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12).
  - Enforce per-client rate limit 10 Mbps/2 Mbps (down/up).
- **IPAM**: Gateway 192.168.99.1; DHCP-only clients; captive portal disabled (passworded WPA2 only).
- **DHCP**: Pool 192.168.99.100-200; lease 4h; DNS 1.1.1.1/8.8.8.8; client isolation enabled at SSID.
- **SSID/Ports**: `HL-Guest` WPA2-Personal + Guest Policy; Access-Guest ports for wired guest events.
- **Monitoring**: UniFi guest analytics; blocklists auto-updated weekly; alerts for >20 clients concurrent.

#### VLAN 100 — Lab (192.168.100.0/24)
- **Firewall Rules**:
  - Allow any from VLAN100 to internet.
  - Allow TCP 8080/8443 from VLAN100 to VLAN10 (web services only).
- **IPAM**: Gateway 192.168.100.1; static: 100.10 Kali, 100.11 Metasploitable, 100.12-14 test VMs; DHCP for transient VMs.
- **DHCP**: Pool 192.168.100.100-200; lease 1h; DNS 192.168.10.2/1.1.1.1.
- **SSID/Ports**: `HL-Lab` WPA2-Personal; Access-Lab ports.
- **Monitoring**: IDS signatures set to “Balanced”; span port mirror on USW-24 (Port 24) for packet capture; SIEM forward via syslog to 192.168.10.5.

### UniFi Controller Configuration Notes
- **Networks**: Each VLAN configured as “Corporate” with gateways listed above; IGMP snooping enabled globally; DHCP Guard enabled on all ports except UDMP.
- **Port Profiles**: Apply Trunk profile to AP uplinks; apply Access profiles per drop; enable PoE on AP ports with 802.3af.
- **Wi-Fi**: Enable PMF required on `HL-Trusted`, optional on others; set minimum data rate 12 Mbps; enable fast roaming on Trusted and Lab SSIDs.
- **VPN**: WireGuard peer subnet 10.10.10.0/24; allowed IPs include 192.168.1.0/24 and 192.168.10.0/24 for admin access.

## Inter-VLAN Routing Matrix
| Source \\ Dest | VLAN1 Mgmt | VLAN10 Trusted | VLAN50 IoT | VLAN99 Guest | VLAN100 Lab | Internet |
|----------------|------------|----------------|------------|--------------|-------------|----------|
| **VLAN1 Mgmt** | N/A | Admin only (SSH/HTTPS) | Deny | Deny | Deny | Allow |
| **VLAN10 Trusted** | Allow TCP 22/443/8443 | N/A | Allow UDP 5353, TCP 80/443 | Deny | Allow Any | Allow |
| **VLAN50 IoT** | Deny | Deny | N/A | Deny | Deny | Allow 80/443/53 |
| **VLAN99 Guest** | Deny | Deny | Deny | N/A | Deny | Allow 80/443/53 |
| **VLAN100 Lab** | Deny | Allow TCP 8080/8443 | Deny | Deny | N/A | Allow |

**Routing Enforcement**: Implemented via UDMP firewall policies (LAN IN/LAN LOCAL) matching the matrix above; default deny follows final rule. Logging enabled for inter-VLAN denies to support auditing and tuning.
