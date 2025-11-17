# Wireless Network Configuration

## SSID Configuration
### HomeNetwork-5G (Primary 5GHz Network)
- Purpose: High-performance trusted devices
- VLAN: 10 (Trusted)
- Security: WPA3-Personal (SAE) with WPA2 fallback; PSK stored in 1Password
- Radio: 5GHz only, 80MHz width, transmit power auto (17-22dBm), min RSSI -70dBm
- Advanced: 802.11r fast roaming enabled, multicast enhancement enabled, DTIM 1, beacon 100ms
- Client Isolation: Disabled

### IoT (2.4GHz/5GHz)
- VLAN: 20 (IoT)
- Security: WPA2-Personal, strong PSK rotated yearly
- Radio: Dual-band, 20MHz width on 2.4GHz to reduce interference
- Features: Client isolation disabled (allows hub control), band steering enabled

### Guest
- VLAN: 30 (Guest)
- Security: WPA2-Personal, password rotated monthly
- Policies: Client isolation enabled, bandwidth limit 25/10 Mbps, content filtering via OpenDNS FamilyShield

## Access Point Details
### AP-Office (U6-Pro)
- Location: Office ceiling; Mgmt IP 192.168.1.20
- 5GHz: Channel 149, 80MHz, power high (22dBm)
- 2.4GHz: Auto channel, 20MHz, power low (10dBm)
- Typical Clients: 10 (laptops/phones/tablets)
- Metrics: Throughput 400-600 Mbps, latency <2ms, retry rate 2-4%

### AP-LivingRoom (U6-Lite)
- Location: Living room ceiling; Mgmt IP 192.168.1.21
- 5GHz: Channel 36, 80MHz, power medium
- 2.4GHz: Channel 1/6/11 auto, power medium
- Clients: 8-12 across TVs and phones

### AP-Bedroom (U6-Pro)
- Location: Master bedroom ceiling; Mgmt IP 192.168.1.22
- 5GHz: Channel 149 shared with office (distance >30ft)
- 2.4GHz: Auto channel, low power to reduce overlap

## Channel Planning & Optimization
- Strategy: DFS upper band where possible to avoid congestion; upper band fallback (149+) stable locally.
- Assignments: Office 149, LivingRoom 36, Bedroom 149 with spatial separation to limit co-channel interference.
- Site Survey (2024-10-15): -35 to -60 dBm across living areas; marginal -70 dBm in garage acceptable.

## Guest Network Policies
- Internet only, LAN blocked; firewall denies RFC1918 and common lateral movement ports.
- DPI categories blocked: P2P, torrents, adult content; alerts on bandwidth >50Mbps sustained.
- Client isolation enforced on APs; schedules unrestricted.
