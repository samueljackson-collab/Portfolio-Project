# Wireless Network Configuration

## SSID Configuration

### HomeNetwork-5G (Primary 5GHz Network)
**Purpose**: High-performance network for trusted devices  
**VLAN Assignment**: VLAN 10 (Trusted)  
**Broadcasting APs**: AP-Office, AP-LivingRoom, AP-Bedroom  

#### Security Settings
- **Security Protocol**: WPA3-Personal (SAE)
- **Fallback**: WPA2-Personal (AES) for legacy compatibility
- **Pre-Shared Key**: Stored in 1Password "Home Network PSK"
- **Group Rekey Interval**: 3600 seconds
- **PMF (802.11w)**: Required

#### Radio Settings
- **Band**: 5GHz only
- **Channel Width**: 80MHz
- **Transmit Power**: Auto (17-22 dBm depending on AP)
- **Minimum RSSI**: -70 dBm (forces roaming)
- **Protocols**: 802.11ac/ax only

#### Advanced Features
- **Fast Roaming (802.11r)**: Enabled
- **Band Steering**: Disabled (5GHz-only SSID)
- **Multicast Enhancement**: Enabled
- **DTIM Period**: 1
- **Beacon Interval**: 100ms
- **Client Isolation**: Disabled (trusted peer-to-peer allowed)

#### Client Statistics
- **Average Clients**: 15-20
- **Peak Clients**: 30
- **Typical Devices**: 40% laptops, 40% smartphones, 20% IoT/TV

---

### IoT (Smart Device Network)
**Purpose**: Dedicated WLAN for smart-home devices requiring 2.4GHz reach  
**VLAN Assignment**: VLAN 20 (IoT)  
**Broadcasting APs**: All APs  

#### Security Settings
- **Security Protocol**: WPA2-Personal (AES)
- **Pre-Shared Key**: Stored in 1Password "IoT PSK"
- **Group Rekey Interval**: 3600 seconds
- **PMF**: Optional (many IoT clients lack support)

#### Radio Settings
- **Bands**: Dual (2.4GHz + 5GHz) to cover diverse IoT hardware
- **Channel Width**: 20MHz on 2.4GHz, 40MHz on 5GHz
- **Transmit Power**: Medium (2.4GHz ~12 dBm; 5GHz auto)
- **Minimum RSSI**: -75 dBm
- **Protocols**: 802.11n/ax on 2.4GHz; 802.11ac/ax on 5GHz

#### Advanced Features
- **Band Steering**: Enabled (encourage 5GHz capable IoT)
- **Proxy ARP**: Enabled to reduce broadcast load
- **Client Isolation**: Enabled at AP level (reduces lateral risk)

#### Client Statistics
- **Average Clients**: 18-22
- **Peak Clients**: 30+
- **Typical Devices**: Speakers, displays, thermostat, smart plugs, hubs

---

### Guest (Visitor Network)
**Purpose**: Internet-only guest access with strict isolation  
**VLAN Assignment**: VLAN 30 (Guest)  
**Broadcasting APs**: All APs  

#### Security Settings
- **Security Protocol**: WPA2-Personal
- **Pre-Shared Key**: Stored in 1Password "Guest PSK" (rotated monthly)
- **Client Isolation**: Enabled
- **Guest Policies**: Captive portal disabled; apply bandwidth limits and content filtering at controller.

#### Radio Settings
- **Bands**: Dual-band
- **Channel Width**: 40MHz on 5GHz, 20MHz on 2.4GHz
- **Transmit Power**: Auto

#### Traffic Controls
- **Bandwidth Limit**: 25 Mbps down / 10 Mbps up per client
- **Content Filtering**: OpenDNS FamilyShield + DPI block P2P/Adult
- **LAN Access**: Block all RFC1918; only internet allowed

---

## Access Point Details

### AP-Office (Primary Coverage)
- **Model**: U6-Pro
- **Location**: Office ceiling
- **Management IP**: 192.168.1.20
- **MAC**: XX:XX:XX:XX:XX:20
- **Firmware**: 6.5.55.14637
- **Adoption**: Managed by UDMP
- **Uplink**: Switch Port 13 (Trunk, PoE+)
- **PoE Draw**: 15.4W

#### Radio Configuration
- **2.4GHz**: Channel 11, 20MHz, 10 dBm, min rate 18 Mbps
- **5GHz**: Channel 149 (DFS upper), 80MHz, 22 dBm
- **Client Load**: 8-12 typical, utilization 15-30%

#### Client Distribution
| SSID | VLAN | Typical Clients | Devices |
|------|------|-----------------|---------|
| HomeNetwork-5G | 10 | 10 | Laptops, phones, tablets |
| IoT | 20 | 3 | Smart displays, printers |
| Guest | 30 | 0-2 | Visitor devices |

#### Performance Metrics
- Throughput: 400-600 Mbps typical
- Latency: <2ms to gateway
- Packet Loss: <0.1%
- Retry Rate: 2-4%

### AP-LivingRoom (Secondary Coverage)
- **Model**: U6-Pro
- **Location**: Living room ceiling
- **Management IP**: 192.168.1.21
- **Firmware**: 6.5.55.14637
- **Uplink**: Switch Port 14 (Trunk, PoE+)
- **PoE Draw**: 13.2W

#### Radio Configuration
- **2.4GHz**: Channel 1, 20MHz, 10 dBm
- **5GHz**: Channel 36, 80MHz, 20 dBm
- **Client Load**: 10-15 typical

### AP-Bedroom (Tertiary Coverage)
- **Model**: U6-Pro
- **Location**: Master bedroom ceiling
- **Management IP**: 192.168.1.22
- **Firmware**: 6.5.55.14637
- **Uplink**: Switch Port 15 (Trunk, PoE+)
- **PoE Draw**: 14.1W

#### Radio Configuration
- **2.4GHz**: Channel 6, 20MHz, 8 dBm
- **5GHz**: Channel 149, 80MHz, 18 dBm
- **Client Load**: 6-10 typical

## Channel Planning & Optimization

### 5GHz Channel Plan
- **Strategy**: Mix DFS upper (149) and lower (36) to reduce co-channel interference; reuse 149 where separation >30ft and walls provide attenuation.
- **Assignments**: AP-Office 149, AP-LivingRoom 36, AP-Bedroom 149.
- **Rationale**: 80MHz channels maximize WiFi 6 throughput; DFS-capable clients validated; lower band AP reduces overlap in central area.

### 2.4GHz Plan
- **Channels**: 1/6/11 reuse across APs with low power to minimize overlap.
- **Rationale**: Provide compatibility for legacy IoT while minimizing contention.

### Site Survey Highlights (2024-10-15)
- **Tools**: WiFiman + Ekahau free tier.
- **Coverage**: Office -35 to -50 dBm, Living Room -40 to -60 dBm, Kitchen -50 to -65 dBm, Bedrooms -45 to -70 dBm, Garage -65 to -75 dBm.
- **Interference**: Minimal on 5GHz; heavy overlap on 2.4GHz from neighbors; no notable non-WiFi interferers.

## Guest Network Policies
- **Isolation**: Client isolation enabled; firewall blocks RFC1918; no LAN access.
- **Bandwidth**: 25/10 Mbps per client enforced at controller.
- **Blocked Services**: SMB/RDP/SSH/all RFC1918; DoH/DoT blocked via SNI; IDS/IPS strict mode.
- **Monitoring**: DPI categories blocked (P2P, Torrents, Adult); alerts on bandwidth >50 Mbps sustained.
