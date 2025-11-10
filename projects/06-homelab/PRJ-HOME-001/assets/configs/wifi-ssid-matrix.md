# Homelab Wi-Fi SSID Configuration Matrix

## Overview
This document outlines the wireless network configuration for the homelab, including SSID settings, VLAN mappings, security protocols, and access point placement.

## SSID Configuration Table

| SSID Name | VLAN | Security | Password Type | Band | Max Clients | Purpose | Broadcast | Guest Portal |
|-----------|------|----------|---------------|------|-------------|---------|-----------|--------------|
| Homelab-Trusted | 10 | WPA3-Personal (WPA2 fallback) | Strong passphrase (32+ chars) | 2.4 GHz + 5 GHz | 20 | Personal devices | Yes | No |
| Homelab-IoT | 50 | WPA2-Personal | Strong passphrase | 2.4 GHz only | 30 | Smart home devices | Yes | No |
| Homelab-Guest | 99 | WPA2-Personal | Simple passphrase | 2.4 GHz + 5 GHz | 10 | Visitor access | Yes | Yes |
| Homelab-Lab | 100 | WPA2-Personal | Strong passphrase | 5 GHz only | 5 | Testing & research | No | No |

## Detailed SSID Configuration

### Homelab-Trusted (VLAN 10)
**Purpose**: Personal and work devices (phones, laptops, tablets)

**Security Settings:**
- **Protocol**: WPA3-Personal with WPA2/WPA3 transition mode
- **Encryption**: AES-CCMP (WPA2) + GCMP-256 (WPA3)
- **Password**: 32-character random string stored in password manager
- **PMF**: Required (Protected Management Frames)

**Performance Settings:**
- **Band Steering**: Enabled (prefer 5 GHz)
- **Fast Roaming**: 802.11r/k/v enabled
- **MU-MIMO**: Enabled
- **Minimum Data Rate**: 12 Mbps (2.4 GHz), 24 Mbps (5 GHz)
- **UAPSD**: Enabled (power saving)

**Advanced Features:**
- **mDNS**: Enabled (for AirPlay, Chromecast within VLAN)
- **IGMP Snooping**: Enabled
- **Group Rekey Interval**: 3600 seconds

### Homelab-IoT (VLAN 50)
**Purpose**: Smart home devices (bulbs, locks, cameras, speakers)

**Security Settings:**
- **Protocol**: WPA2-Personal (IoT device compatibility)
- **Encryption**: AES-CCMP
- **Password**: Different 32-character random string
- **PMF**: Optional (some IoT devices don't support)

**Performance Settings:**
- **Band**: 2.4 GHz only (most IoT devices lack 5 GHz)
- **Channel Width**: 20 MHz (better range, IoT compatibility)
- **Minimum Data Rate**: 1 Mbps (for low-power devices)
- **Fast Roaming**: Disabled (IoT devices don't roam)

**IoT-Specific Features:**
- **mDNS Reflector**: Enabled (allows cross-VLAN discovery)
- **DTIM Period**: 3 (better battery life for IoT)
- **BSS Transition**: Disabled

### Homelab-Guest (VLAN 99)
**Purpose**: Visitor internet access

**Security Settings:**
- **Protocol**: WPA2-Personal (simple for guests)
- **Encryption**: AES-CCMP
- **Password**: 12-character simple phrase (shared verbally/QR code)
- **PMF**: Disabled (guest device compatibility)

**Access Control:**
- **Client Isolation**: Enabled (devices can't see each other)
- **Rate Limiting**: 10 Mbps download, 5 Mbps upload per client
- **Data Cap**: 5 GB per device (optional)
- **Session Duration**: 24 hours (re-authentication required)

**Guest Portal Configuration:**
- **Type**: Password-based (simple) or voucher-based (advanced)
- **Landing Page**: Custom HTML with terms of service
- **Redirect**: After authentication, redirect to original URL
- **Custom Fields**: Optional (name, email for visitors)

### Homelab-Lab (VLAN 100)
**Purpose**: Testing, research, and security experiments

**Security Settings:**
- **Protocol**: WPA2-Personal
- **Encryption**: AES-CCMP
- **Password**: 32-character random string
- **PMF**: Disabled (for compatibility with security tools)

**Lab-Specific Features:**
- **Hidden SSID**: Enabled (security through obscurity)
- **Band**: 5 GHz only (higher throughput for testing)
- **Channel**: Manual selection (avoiding interference)
- **WPA2-Enterprise**: Test configuration available

## Access Point Placement and Configuration

### AP #1 - Living Room (Main Coverage)
**Location**: Central ceiling mount, living room
**Channels**:
- 2.4 GHz: Channel 1 (HT20)
- 5 GHz: Channel 36 (VHT80)

**SSIDs Broadcast**: All 4 SSIDs
**Transmit Power**: Auto (medium)
**Antenna Gain**: 3 dBi (2.4 GHz), 3 dBi (5 GHz)

### AP #2 - Bedroom (Secondary Coverage)
**Location**: Ceiling mount, bedroom hallway
**Channels**:
- 2.4 GHz: Channel 6 (HT20)
- 5 GHz: Channel 149 (VHT80)

**SSIDs Broadcast**: Homelab-Trusted, Homelab-Guest only
**Transmit Power**: Low (to avoid interference with AP #1)
**Antenna Gain**: 3 dBi (2.4 GHz), 3 dBi (5 GHz)

### AP #3 - Office (Work Area Coverage)
**Location**: Wall mount, office
**Channels**:
- 2.4 GHz: Channel 11 (HT20)
- 5 GHz: Channel 161 (VHT80)

**SSIDs Broadcast**: All 4 SSIDs
**Transmit Power**: Auto (medium)
**Antenna Gain**: 3 dBi (2.4 GHz), 3 dBi (5 GHz)

## Channel Planning Strategy

### 2.4 GHz Band (Channels 1, 6, 11 only)
```
AP #1: Channel 1 ────→ 5 MHz guard ────→ AP #2: Channel 6 ────→ 5 MHz guard ────→ AP #3: Channel 11
```

### 5 GHz Band (Non-Overlapping)
- **AP #1**: Channel 36 (UNII-1, 5180-5240 MHz)
- **AP #2**: Channel 149 (UNII-3, 5745-5825 MHz)
- **AP #3**: Channel 161 (UNII-3, 5745-5825 MHz)

**DFS Channels**: Avoided for compatibility (radar detection issues)

## Roaming Configuration

### Fast Roaming (802.11r)
- **Enabled for**: Homelab-Trusted only
- **Mobility Domain**: Same across all APs
- **Reassociation Deadline**: 20 seconds

### Assisted Roaming (802.11k/v)
- **802.11k**: Enabled (neighbor reports)
- **802.11v**: Enabled (BSS transition management)
- **Minimum RSSI**: -70 dBm (trigger for roaming)

### Roaming Aggressiveness
- **Voice**: High (seamless VoIP calls)
- **Data**: Medium (balance performance and stability)
- **IoT**: Low (devices typically stationary)

## Advanced Features

### Band Steering
- **Prefer 5 GHz**: Enabled for Homelab-Trusted and Homelab-Guest
- **Balance Load**: Enabled (distribute clients across bands)
- **Steering Strength**: Medium

### AirTime Fairness
- **Enabled**: Yes (prevents slow clients from hogging airtime)
- **Per-SSID**: Configured individually

### Client Device Fingerprinting
- **Enabled**: Yes (for monitoring and statistics)
- **OS Detection**: Yes (Android, iOS, Windows, macOS, Linux)
- **Device Type**: Yes (phone, laptop, tablet, IoT)

## Troubleshooting Guide

### Common Issues and Solutions

**Issue: IoT device won't connect to Homelab-IoT**
- **Solution**: Ensure device supports WPA2, try 2.4 GHz only, check for special characters in password

**Issue: Slow speeds on Homelab-Guest**
- **Solution**: Check rate limiting settings, verify client isolation isn't causing overhead

**Issue: Roaming between APs not working**
- **Solution**: Verify 802.11r/k/v enabled, check minimum RSSI settings, ensure channels don't overlap

**Issue: Hidden SSID (Homelab-Lab) not found**
- **Solution**: Manually add network with exact SSID name, case-sensitive

### Performance Testing Commands
```bash
# Test connection speed from trusted device
speedtest-cli

# Test roaming between APs
ping -t 192.168.10.1  # Continuous ping to gateway while moving

# Check wireless client information
ssh admin@192.168.1.1
show wireless clients
```

### Monitoring and Maintenance

**Daily Checks:**
- AP status (online/offline)
- Client count per SSID
- Channel utilization

**Weekly Tasks:**
- Review connected devices (remove unknown devices)
- Check for firmware updates
- Review performance metrics

**Monthly Tasks:**
- Site survey (check for dead zones)
- Channel optimization (scan for interference)
- Security review (check for unauthorized access points)

## QR Code Generation for Guest Access

Generate QR codes for easy guest connection:

```bash
# Generate QR code for Homelab-Guest
echo "WIFI:S:Homelab-Guest;T:WPA;P:guestpassword123;;" | qrencode -o guest-wifi-qr.png
```

This Wi-Fi configuration provides secure, segmented wireless access tailored to different device types and use cases while maintaining performance and manageability.
