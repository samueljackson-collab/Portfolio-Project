# UniFi Home Network Design

**Location:** 5116 S 142nd St, Tukwila, WA 98168  \
**Revision:** 2024-06-09  \
**Author:** Sam Jackson

---

## 1. Objective
Design a resilient, security-conscious UniFi network for a two-story residential property with expansive outdoor coverage and an integrated video security system. The design must support:

- Six indoor access points (four downstairs, two upstairs)
- Five outdoor access points with co-located 4K cameras and flood lights
- Two UniFi wireless doorbell cameras
- Segmented SSIDs for trusted, IoT, and guest traffic
- Centralized management through UniFi OS (UDM-Pro)

---

## 2. High-Level Requirements
| Area | Requirement |
| --- | --- |
| Wireless | Ubiquitous indoor Wi-Fi 6 coverage; dedicated outdoor mesh for yard/driveway |
| Wired | Single consolidated PoE switching fabric feeding APs, cameras, and flood lights |
| Security | Layered VLAN segmentation with default deny between security zones |
| Observability | Telemetry and alerting for connectivity, camera recording health, and PoE budget |
| Resiliency | UPS-backed rack, documented recovery procedures, and routine configuration backups |

---

## 3. Logical Network Segmentation
| VLAN | Name | Subnet | Purpose |
| --- | --- | --- | --- |
| 10 | Management | 10.10.10.0/24 | UniFi network controllers, switches, AP adoption |
| 20 | Trusted | 10.10.20.0/24 | Family laptops, phones, TVs, wired desktops |
| 30 | IoT | 10.10.30.0/24 | Cameras, flood lights, doorbells, smart-home gear |
| 40 | Guest | 10.10.40.0/24 | Internet-only guest SSID |
| 50 | Services | 10.10.50.0/24 | NAS, hypervisor management, VPN concentrator |

Routing and firewall policies enforced on the UniFi Dream Machine Pro:
- Management VLAN reachable only from Trusted VLAN admin workstation subnet
- IoT VLAN denied east-west traffic, with explicit allows for NTP, DNS, and UniFi Protect ports
- Guest VLAN fully isolated with internet breakout only
- Services VLAN restricted to Trusted VLAN and site-to-site VPN for remote administration

---

## 4. Wireless SSIDs
| SSID | VLAN | Auth | Notes |
| --- | --- | --- | --- |
| Home-Trusted | 20 | WPA3-Enterprise | 802.1X via UniFi ID with MFA |
| Home-IoT | 30 | WPA2-PSK | Hidden SSID, MAC filtering for doorbells |
| Home-Guest | 40 | WPA2-PSK | Client isolation, bandwidth limit 25 Mbps |

Channel plan leverages RF scan data gathered during site survey; static 2.4 GHz channels (1/6/11) and DFS-enabled 5 GHz assignments minimize co-channel interference.

---

## 5. Physical Architecture
- **Headend rack (garage closet):** UDM-Pro, UniFi Switch Pro 24 PoE, Cloud Key Gen2 Plus (Protect), 24-port CAT6 patch panel, 1500VA UPS
- **Structured cabling:** CAT6A home runs for all PoE devices; outdoor runs in UV-rated conduit
- **Downstairs zone switch (optional):** UniFi Switch Lite 8 PoE for living room cluster

Each outdoor pod (AP + G5 Bullet camera + flood light) lands on a dedicated PoE port. Doorbell cameras connect wirelessly to closest outdoor AP; wiring cabinet provides 24V passive injectors where required.

---

## 6. Capacity & Performance Targets
| Metric | Target |
| --- | --- |
| Wireless RSSI | ≥ -65 dBm for indoor coverage, ≥ -70 dBm at property boundary |
| Client Count | < 30 clients per AP (average) |
| Internet Latency | < 30 ms to Seattle region test targets |
| Camera Bitrate | 4–6 Mbps per 4K camera, 1.5 Mbps per doorbell |
| PoE Budget | < 80% of 24-port switch capacity |

---

## 7. Security Controls
- MFA on UniFi OS and remote access portals
- GeoIP allow-list for management surfaces
- Automated firmware approval workflow via UniFi Network Application
- Weekly config backup exports to NAS (Services VLAN)
- syslog + UDM-Pro event forwarding to ELK stack for retention > 90 days

---

## 8. Implementation Summary
1. Rack/stack core gear; label patch panel and cable pathways
2. Configure VLANs, firewall rules, DHCP scopes on UDM-Pro
3. Adopt switches/APs; map SSIDs to VLANs; apply RF tuning profiles
4. Commission cameras/flood lights in UniFi Protect with static leases (VLAN 30)
5. Validate coverage, throughput, failover power, and alerting baselines

---

## 9. Future Enhancements
- Secondary UDM-Pro or UXG-Pro warm spare with VRRP-style failover
- Dedicated UniFi Protect NVR with RAID storage
- Outdoor point-to-point link to detached garage/workshop (if built)
- Integration with Home Assistant for automation of flood lights and alerts

