# Wi-Fi Network Configuration

## SSID Overview

| SSID Name | VLAN | Security | Band | Purpose | Broadcast |
|-----------|------|----------|------|---------|-----------|
| HomeNet | 10 | WPA3-Personal | 2.4 + 5 GHz | Trusted devices | Yes |
| HomeNet-IoT | 50 | WPA2-Personal | 2.4 GHz only | IoT devices | Yes |
| HomeNet-Guest | 99 | WPA2-Personal | 2.4 + 5 GHz | Guest access | Yes |
| HomeNet-Mgmt | 30 | WPA3-Personal | 5 GHz only | Network management | No (hidden) |

## Detailed SSID Configuration

### HomeNet (Trusted SSID)

**Basic Settings:**
- **SSID:** HomeNet
- **VLAN:** 10 (Trusted)
- **Security:** WPA3-Personal (WPA2 fallback for compatibility)
- **Password:** [Strong 20+ character passphrase]
- **Broadcast:** Enabled
- **Band:** 2.4 GHz + 5 GHz

**Advanced Settings:**
- **Band Steering:** Enabled (prefer 5 GHz)
- **Fast Roaming:** Enabled (802.11r)
- **Minimum RSSI:** -75 dBm
- **Client Device Isolation:** Disabled
- **Multicast Enhancement:** Enabled
- **BSS Transition:** Enabled (802.11v)
- **Proxy ARP:** Disabled

**Performance Settings:**
- **2.4 GHz Channel:** Auto (1, 6, or 11)
- **2.4 GHz Channel Width:** 20 MHz
- **2.4 GHz Transmit Power:** High
- **5 GHz Channel:** Auto (36, 40, 44, 48, 149, 153, 157, 161)
- **5 GHz Channel Width:** 80 MHz (VHT80)
- **5 GHz Transmit Power:** High
- **Data Rate Control:** 12 Mbps minimum (disable legacy rates)

**Typical Connected Devices:**
- Laptops, phones, tablets
- Personal devices of household members

---

### HomeNet-IoT (IoT SSID)

**Basic Settings:**
- **SSID:** HomeNet-IoT
- **VLAN:** 50 (IoT)
- **Security:** WPA2-Personal (many IoT devices don't support WPA3)
- **Password:** [Different from HomeNet]
- **Broadcast:** Enabled
- **Band:** 2.4 GHz only (IoT devices often 2.4 GHz only)

**Advanced Settings:**
- **Band Steering:** Disabled (2.4 GHz only)
- **Fast Roaming:** Disabled (IoT devices have poor roaming)
- **Minimum RSSI:** -80 dBm
- **Client Device Isolation:** Enabled
- **Multicast Enhancement:** Disabled (reduces attack surface)
- **BSS Transition:** Disabled
- **Proxy ARP:** Disabled

**Performance Settings:**
- **2.4 GHz Channel:** Auto (1, 6, or 11)
- **2.4 GHz Channel Width:** 20 MHz (better range for IoT)
- **2.4 GHz Transmit Power:** High
- **Data Rate Control:** 6 Mbps minimum

**Security Hardening:**
- **Client Device Isolation:** Enabled (IoT devices can't talk to each other)
- **Firewall Rules:** Internet-only access (see firewall matrix)
- **DNS Filtering:** Enabled (Pi-hole with IoT blocklists)

**Typical Connected Devices:**
- Smart plugs, smart lights
- Thermostats, door sensors
- IP cameras
- Smart speakers
- Other IoT devices requiring Wi-Fi

---

### HomeNet-Guest (Guest SSID)

**Basic Settings:**
- **SSID:** HomeNet-Guest
- **VLAN:** 99 (Guest)
- **Security:** WPA2-Personal
- **Password:** [Simple, shareable password - rotated monthly]
- **Broadcast:** Enabled
- **Band:** 2.4 GHz + 5 GHz

**Advanced Settings:**
- **Band Steering:** Enabled
- **Fast Roaming:** Disabled
- **Minimum RSSI:** -70 dBm
- **Client Device Isolation:** Enabled
- **Multicast Enhancement:** Disabled
- **BSS Transition:** Disabled
- **Proxy ARP:** Disabled

**Performance Settings:**
- **2.4 GHz Channel:** Auto
- **2.4 GHz Channel Width:** 20 MHz
- **2.4 GHz Transmit Power:** Medium
- **5 GHz Channel:** Auto
- **5 GHz Channel Width:** 40 MHz (VHT40)
- **5 GHz Transmit Power:** Medium
- **Data Rate Control:** 12 Mbps minimum

**Security Hardening:**
- **Client Device Isolation:** Enabled (guests can't see each other)
- **Access Schedule:** 24/7 (can be limited if desired)
- **Bandwidth Limit:** 50 Mbps download, 10 Mbps upload
- **Firewall Rules:** Internet-only access (see firewall matrix)

**Guest Access Management:**
- **Password Rotation:** Monthly or after events
- **Temporary Access:** Can enable/disable quickly via UniFi Controller
- **Guest Portal:** Optional (can enable captive portal for terms acceptance)

**Typical Connected Devices:**
- Visitor phones
- Visitor laptops
- Contractor devices

---

### HomeNet-Mgmt (Management SSID)

**Basic Settings:**
- **SSID:** HomeNet-Mgmt
- **VLAN:** 30 (Management)
- **Security:** WPA3-Personal
- **Password:** [Extremely strong 30+ character passphrase]
- **Broadcast:** Disabled (hidden SSID)
- **Band:** 5 GHz only

**Advanced Settings:**
- **Band Steering:** N/A (5 GHz only)
- **Fast Roaming:** Enabled
- **Minimum RSSI:** -65 dBm
- **Client Device Isolation:** Disabled
- **Multicast Enhancement:** Disabled
- **BSS Transition:** Enabled
- **Proxy ARP:** Disabled

**Performance Settings:**
- **5 GHz Channel:** Auto
- **5 GHz Channel Width:** 80 MHz
- **5 GHz Transmit Power:** Medium
- **Data Rate Control:** 24 Mbps minimum

**Security Hardening:**
- **MAC Address Filtering:** Enabled (whitelist admin devices)
- **Firewall Rules:** Full access to all management interfaces
- **Access Schedule:** 24/7 (for emergency access)

**Typical Connected Devices:**
- Admin laptop for network troubleshooting
- Phone with network management apps

---

## Access Point Configuration

### AP-Main-Floor (UniFi AP-AC-Pro)

**Location:** Main floor living room ceiling  
**IP Address:** 192.168.30.10  
**Coverage Area:** Main floor (living room, kitchen, dining)

**SSIDs Enabled:**
- HomeNet (2.4 + 5 GHz)
- HomeNet-IoT (2.4 GHz)
- HomeNet-Guest (2.4 + 5 GHz)
- HomeNet-Mgmt (5 GHz, hidden)

**Radio Configuration:**
- **2.4 GHz Power:** High
- **5 GHz Power:** High
- **Channel Optimization:** Auto

---

### AP-Upper-Floor (UniFi AP-AC-Lite)

**Location:** Upper floor hallway ceiling  
**IP Address:** 192.168.30.11  
**Coverage Area:** Bedrooms, upper floor bathroom

**SSIDs Enabled:**
- HomeNet (2.4 + 5 GHz)
- HomeNet-IoT (2.4 GHz)
- HomeNet-Guest (2.4 + 5 GHz)

**Radio Configuration:**
- **2.4 GHz Power:** Medium (to prevent co-channel interference with AP-Main-Floor)
- **5 GHz Power:** High
- **Channel Optimization:** Auto (coordinator with AP-Main-Floor)

---

## Wi-Fi Best Practices

### Channel Planning
- **2.4 GHz:** Use only channels 1, 6, and 11 (non-overlapping)
- **5 GHz:** Prefer DFS channels (52-144) if supported by all devices
- **Auto Channel:** Enabled with periodic optimization

### Power Settings
- **General Guideline:** Start at Medium, increase only if coverage gaps exist
- **Avoid:** Maximum power on all APs (causes co-channel interference)
- **Goal:** -67 dBm minimum signal strength in all areas

### Security Best Practices
1. **Use WPA3:** Where possible (with WPA2 fallback)
2. **Disable WPS:** Push-button config disabled
3. **Disable WEP/WPA:** Only WPA2/WPA3 allowed
4. **Rotate Passwords:** Guest network monthly, others annually
5. **Monitor Rogues:** Enable rogue AP detection

### Performance Optimization
1. **Band Steering:** Prefer 5 GHz for dual-band devices
2. **Fast Roaming (802.11r):** Enabled for seamless handoff
3. **Airtime Fairness:** Enabled (prevent slow devices from hogging airtime)
4. **Disable Legacy Rates:** Set minimum to 12 Mbps (disables 802.11b)
5. **DFS Channels:** Utilize DFS channels for less congestion

## Wi-Fi Troubleshooting

### Poor Performance
1. Check for channel congestion using UniFi WiFiman app
2. Verify signal strength (should be > -67 dBm)
3. Check for interference (neighboring APs, microwave, etc.)
4. Verify client supports current band/channel width

### Connection Drops
1. Check for roaming issues (minimum RSSI too low)
2. Verify AP firmware is up to date
3. Check for intermittent interference
4. Review Wi-Fi logs for disconnect reasons

### IoT Device Connection Issues
1. Verify device is 2.4 GHz and trying to connect to HomeNet-IoT
2. Disable band steering (if device tries to connect to 5 GHz)
3. Temporarily increase 2.4 GHz power
4. Check if device is too far from AP

## Wi-Fi Monitoring

### Key Metrics
- **Client Count:** Monitor per-SSID and per-AP
- **Interference:** < 50% channel utilization
- **Signal Strength:** > -67 dBm for 95% of area
- **Roaming Events:** Successful vs. failed roaming
- **Error Rates:** < 1% retransmission rate

### Alert Thresholds
- AP offline for > 5 minutes
- Client count > 50 per AP
- Channel utilization > 70%
- Failed authentication attempts > 10/hour (rogue detection)

## Wi-Fi Maintenance

### Weekly
- Review client connection logs
- Check for unauthorized SSIDs (rogue APs)

### Monthly
- Rotate guest Wi-Fi password
- Review coverage heatmap (using UniFi app)
- Check AP firmware updates

### Quarterly
- Perform site survey with Wi-Fi analyzer
- Optimize channel assignments
- Review and update minimum RSSI settings
- Test roaming between APs

### Annually
- Rotate trusted SSID passwords
- Review security settings for new vulnerabilities
- Assess if additional APs needed
