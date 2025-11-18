# Wireless Network Configuration

## SSID Configuration

### HomeNetwork-5G (Primary 5GHz Network)
- Purpose: High-performance trusted network
- VLAN: 10
- Security: WPA3-Personal (SAE) with WPA2 fallback; PSK stored in password manager; PMF required
- Radio: 5GHz only, 80MHz width, channel 149 on AP-Office/AP-Bedroom and 36 on AP-LivingRoom; transmit power auto (17-22 dBm)
- Advanced: 802.11r fast roaming enabled, multicast enhancement on, DTIM 1, beacon 100ms, min RSSI -70 dBm
- Clients: 15-20 avg; laptops/phones/tablets primary

### IoT (2.4/5GHz)
- VLAN: 20
- Security: WPA2-Personal strong passphrase; PMF optional for legacy sensors
- Band Steering: Enabled to keep higher capability devices on 5GHz when possible
- Client Isolation: Disabled (allows hub control) but inter-VLAN restricted via firewall

### Guest
- VLAN: 30
- Security: WPA2-Personal rotated monthly; client isolation enabled
- Bandwidth Limit: 25/10 Mbps per client; DPI blocks P2P/torrents/adult content
- Access: Internet only; RFC1918 blocked

## Access Point Details

### AP-Office (U6-Pro)
- Location: Office ceiling; management IP 192.168.1.20; uplink Switch port 13 (PoE+)
- 2.4GHz: Auto channel, 20MHz, low power 10 dBm, minimum rate 18 Mbps
- 5GHz: Channel 149, 80MHz, high power 22 dBm; typical 8-12 clients; throughput 400-600 Mbps

### AP-LivingRoom (U6-Pro)
- Uplink port 14; 5GHz channel 36, 80MHz, medium power 18 dBm to avoid overlap with office
- Serves living areas; typical 6-10 clients; coverage extends to kitchen

### AP-Bedroom (U6-Lite)
- Uplink port 15; 5GHz channel 149 low power 16 dBm to minimize interference; serves bedrooms/hallway

## Channel Planning
- Strategy: DFS/upper band preference to reduce congestion; stagger channels 36/149 for spatial reuse.
- Survey Results (Oct 2024): Excellent coverage (-35 to -60 dBm) in living areas; marginal (-70 dBm) in garage; minimal non-WiFi interference.

## Guest Network Policies
- Isolation: Enabled; LAN blocked; RFC1918 addresses denied.
- Filtering: OpenDNS FamilyShield DNS; DPI blocks P2P/gaming for bandwidth preservation.
- Monitoring: Alerts on bandwidth >50 Mbps sustained and repeated auth failures.
