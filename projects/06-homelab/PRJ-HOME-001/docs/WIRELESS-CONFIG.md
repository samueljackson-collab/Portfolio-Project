# Wireless Network Configuration

## SSID Configuration

### HomeNetwork-5G (Primary 5GHz Network)
- Purpose: high-performance trusted devices
- VLAN: 10
- Security: WPA3-Personal (fallback WPA2), PSK stored in 1Password
- Group rekey: 3600s, PMF required
- Radio: 5GHz only, 80MHz width, auto power ~17-22dBm, min RSSI -70dBm
- Advanced: 802.11r fast roaming enabled, multicast enhancement on, DTIM 1, beacon 100ms, client isolation off
- Typical clients: 15-20 (peak 30)

### IoT (2.4GHz/5GHz as needed)
- VLAN: 20
- Security: WPA2-Personal, strong PSK
- Client isolation: enabled to reduce lateral movement
- Band steering: enabled to favor 5GHz capable IoT where possible

### Guest
- VLAN: 30
- Security: WPA2-Personal, password rotated monthly
- Bandwidth limit: 25/10 Mbps per client
- Client isolation: enabled; LAN access blocked
- Content filtering: OpenDNS FamilyShield

## Access Point Details

### AP-Office (U6-Pro)
- Location: office ceiling; IP 192.168.1.20; PoE on switch port 13
- 2.4GHz: channel 1, 20MHz, low power 10dBm, minimum rate 18Mbps
- 5GHz: channel 149, 80MHz, 22dBm
- Clients: ~10-12 typical across SSIDs
- Performance: 400-600 Mbps throughput, <2ms latency to gateway

### AP-LivingRoom (U6-Lite)
- IP 192.168.1.21; port 14
- 2.4GHz ch6 20MHz 12dBm; 5GHz ch36 80MHz 20dBm
- Clients: 8-10

### AP-Bedroom (U6-Lite)
- IP 192.168.1.22; port 15
- 2.4GHz ch11 20MHz 10dBm; 5GHz ch149 80MHz 18dBm
- Clients: 6-8

## Channel Planning & Optimization
- Strategy: DFS/upper band use to avoid congestion; 80MHz width for WiFi6 throughput.
- Assignments: AP-Office 149, AP-LivingRoom 36, AP-Bedroom 149 (distance >30ft to limit CCI).
- Survey: WiFiman/Ekahau (2024-10-15) shows -65 dBm or better in living areas; marginal in garage (-75 dBm) as expected.
- Interference: minimal non-WiFi; neighbors limited in 5GHz.

## Guest Network Policies
- Bandwidth limit 25/10 Mbps, schedule 24/7.
- Isolation on; LAN blocked; blocked ports SMB/SSH/RDP; RFC1918 denied.
- IDS/IPS strict; DPI blocks P2P/torrents; logging retained 7 days.

## Connected Device Summary
- Trusted: 3 desktops, 2 laptops, 4 phones, 2 tablets, printer, smart TV.
- IoT: smart speakers, lights, thermostat, sensors via hub.
- Guest: variable 2-3 when visitors present.
