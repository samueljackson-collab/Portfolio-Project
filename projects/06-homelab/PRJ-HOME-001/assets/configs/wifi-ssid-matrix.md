# Homelab Wi-Fi SSID Configuration Matrix

## Overview
Wireless network configuration for homelab with 4 SSIDs mapped to different VLANs for security segmentation.

## SSID Configuration Table

| SSID Name | VLAN | Security | Password Type | Band | Max Clients | Purpose | Broadcast | Guest Portal |
|-----------|------|----------|---------------|------|-------------|---------|-----------|--------------|
| Homelab-Trusted | 10 | WPA3-Personal | Strong (32+ chars) | 2.4 + 5 GHz | 20 | Personal devices | Yes | No |
| Homelab-IoT | 50 | WPA2-Personal | Strong | 2.4 GHz only | 30 | Smart home | Yes | No |
| Homelab-Guest | 99 | WPA2-Personal | Simple | 2.4 + 5 GHz | 10 | Visitors | Yes | Yes |
| Homelab-Lab | 100 | WPA2-Personal | Strong | 5 GHz only | 5 | Testing | No | No |

## Detailed Configuration

### Homelab-Trusted (VLAN 10)
**Purpose**: Personal and work devices

**Security**:
- Protocol: WPA3-Personal with WPA2 fallback
- Encryption: AES-CCMP / GCMP-256
- PMF: Required

**Performance**:
- Band Steering: Enabled (prefer 5 GHz)
- Fast Roaming: 802.11r/k/v enabled
- MU-MIMO: Enabled
- Min Data Rate: 12 Mbps (2.4G), 24 Mbps (5G)

### Homelab-IoT (VLAN 50)
**Purpose**: Smart home devices

**Security**:
- Protocol: WPA2-Personal
- PMF: Optional

**Performance**:
- Band: 2.4 GHz only (IoT compatibility)
- Channel Width: 20 MHz
- mDNS Reflector: Enabled
- DTIM: 3 (better battery life)

### Homelab-Guest (VLAN 99)
**Purpose**: Visitor internet access

**Access Control**:
- Client Isolation: Enabled
- Rate Limiting: 10/5 Mbps (down/up)
- Session Duration: 24 hours
- Data Cap: 5 GB (optional)

**Guest Portal**:
- Type: Password or voucher-based
- Landing Page: Custom with ToS
- Redirect: After auth to original URL

### Homelab-Lab (VLAN 100)
**Purpose**: Testing and research

**Features**:
- Hidden SSID: Enabled
- Band: 5 GHz only
- Manual channel selection

## Access Point Placement

### AP #1 - Living Room
- Channels: 1 (2.4GHz), 36 (5GHz)
- SSIDs: All 4
- Power: Auto (medium)

### AP #2 - Bedroom
- Channels: 6 (2.4GHz), 149 (5GHz)
- SSIDs: Trusted, Guest only
- Power: Low

### AP #3 - Office
- Channels: 11 (2.4GHz), 161 (5GHz)
- SSIDs: All 4
- Power: Auto (medium)

## Channel Planning

### 2.4 GHz
- AP #1: Channel 1
- AP #2: Channel 6
- AP #3: Channel 11
- Strategy: Non-overlapping channels only

### 5 GHz
- AP #1: Channel 36 (UNII-1)
- AP #2: Channel 149 (UNII-3)
- AP #3: Channel 161 (UNII-3)
- DFS Channels: Avoided

## Roaming Configuration

### Fast Roaming (802.11r)
- Enabled for: Homelab-Trusted
- Mobility Domain: Same across APs
- Reassociation Deadline: 20 seconds

### Assisted Roaming (802.11k/v)
- 802.11k: Enabled (neighbor reports)
- 802.11v: Enabled (BSS transition)
- Minimum RSSI: -70 dBm

## Troubleshooting

**IoT device won't connect**
- Ensure WPA2 support
- Try 2.4 GHz only
- Check for special characters in password

**Slow speeds on Guest**
- Check rate limiting settings
- Verify client isolation overhead
- Test with single device

**Roaming not working**
- Verify 802.11r/k/v enabled
- Check minimum RSSI settings
- Ensure channels don't overlap

**Hidden SSID not found**
- Manually add network
- Use exact SSID name (case-sensitive)

## Performance Testing
```bash
# Test connection speed
speedtest-cli

# Test roaming
ping -t 192.168.10.1  # Continuous ping while moving

# Check wireless clients (SSH to UDMP)
show wireless clients
```

## QR Code for Guest Access
```bash
# Generate QR code for easy guest connection
echo "WIFI:S:Homelab-Guest;T:WPA;P:guestpassword123;;" | qrencode -o guest-wifi-qr.png
```

For complete wireless configuration with advanced features and troubleshooting, see the full Wi-Fi documentation.
