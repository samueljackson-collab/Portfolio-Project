# Homelab Network Build - Deployment Runbook

## Runbook Information

- **Version**: 2.0
- **Last Updated**: 2024-11-06
- **Purpose**: Complete homelab network deployment procedure

## 1. Prerequisites

### Hardware Checklist

- [ ] UniFi Dream Machine Pro (UDMP)
- [ ] UniFi Switch 24 PoE
- [ ] UniFi Switch 8 PoE  
- [ ] 3x UniFi AP AC Pro
- [ ] 12U Wall-Mount Rack
- [ ] 24-port Cat6a Patch Panel
- [ ] Cat6a Ethernet Cables
- [ ] UPS Battery Backup (1500VA+)
- [ ] Cable Tester

### Pre-Deployment Tasks

- [ ] Rack cabinet installed and secured
- [ ] Cable runs planned and measured
- [ ] Power outlets available
- [ ] ISP modem in bridge mode
- [ ] Network design reviewed

## 2. Physical Installation (Day 1)

### Step 2.1: Rack Equipment Mounting

**Mounting Order (Top to Bottom):**

1. Patch Panel (RU 1-2)
2. UniFi Dream Machine Pro (RU 3)
3. UniFi Switch 24 PoE (RU 4-5)
4. Cable Management (RU 6, 8, 10)
5. UPS (RU 11-12)

**Procedure:**

```bash
# Use cage nuts and M6 screws
# Torque: Hand-tight only
# Verify: Equipment secure, no wobbling
```

### Step 2.2: Cable Termination
1. Run Cat6a cables from rooms to patch panel
2. Terminate with keystone jacks (T568B)
3. Label each port:
   - Port 1: "Living Room TV"
   - Port 2: "Living Room AP"
   - Port 5: "Proxmox Server"
   - Port 6: "TrueNAS Server"
4. Test all cables with tester

**Expected**: All 8 wires green (pass), Gigabit+ rated

### Step 2.3: Access Point Installation
1. Mount APs to ceiling (Living Room, Bedroom, Office)
2. Run Cat6 cables to each location
3. Connect to patch panel (ports 2, 3, 4)
4. Verify PoE power budget (~12W per AP)

**Validation**: AP LEDs show white (provisioning) then blue (connected)

## 3. UDMP Initial Configuration (Day 1)

### Step 3.1: Factory Setup
1. Connect laptop to UDMP LAN port 1
2. Navigate to https://192.168.1.1
3. Complete setup wizard:
   - Country: United States
   - Timezone: America/New_York
   - Device Name: UDMP-Homelab
   - Admin Account: Create strong password

### Step 3.2: WAN Configuration
1. Connect UDMP WAN port to ISP modem
2. Configure WAN as DHCP
3. Wait for internet connectivity

**Verification:**
```bash

ssh admin@192.168.1.1
ping -c 4 1.1.1.1
ping -c 4 google.com

```

**Expected Output:**
```

4 packets transmitted, 4 received, 0% packet loss

```

### Step 3.3: Adopt Network Devices
1. Power on UniFi Switch 24 PoE
2. In UniFi Controller → Devices → Pending
3. Adopt each device
4. Wait for firmware updates (10-20 min per device)

## 4. VLAN Configuration (Day 2)

### Step 4.1: Create VLANs
**Settings → Networks → Create New Network**

**VLAN 1 (Management):**
- Name: Management
- VLAN ID: 1
- Gateway: 192.168.1.1/24
- DHCP: Disabled

**VLAN 10 (Trusted):**
- Name: Trusted
- VLAN ID: 10
- Gateway: 192.168.10.1/24
- DHCP: Enabled (100-200)
- DNS: 192.168.10.2

**VLAN 50 (IoT):**
- Name: IoT
- VLAN ID: 50
- Gateway: 192.168.50.1/24
- DHCP: Enabled (100-200)
- DNS: 1.1.1.1
- mDNS: Enabled

**VLAN 99 (Guest):**
- Name: Guest
- VLAN ID: 99
- Gateway: 192.168.99.1/24
- DHCP: Enabled (100-200)
- Guest Policy: Enabled

**VLAN 100 (Lab):**
- Name: Lab
- VLAN ID: 100
- Gateway: 192.168.100.1/24
- DHCP: Enabled (100-200)

**Validation**: Settings → Networks shows 5 networks active

## 5. Wi-Fi SSID Configuration (Day 2)

### Settings → WiFi → Create New WiFi Network

**Homelab-Trusted:**
- Security: WPA3-Personal
- Password: [Strong 32-char password]
- Network: VLAN 10
- Band: 2.4 + 5 GHz
- Band Steering: Enabled
- Fast Roaming: 802.11r enabled

**Homelab-IoT:**
- Security: WPA2-Personal
- Password: [Different strong password]
- Network: VLAN 50
- Band: 2.4 GHz only

**Homelab-Guest:**
- Security: WPA2-Personal
- Password: [Simple password]
- Network: VLAN 99
- Guest Policy: Enabled
- Client Isolation: Enabled
- Rate Limit: 10 Mbps

**Homelab-Lab:**
- Security: WPA2-Personal
- Password: [Strong password]
- Network: VLAN 100
- Band: 5 GHz only
- Hide SSID: Yes

**Validation**: Test each SSID connection with smartphone

## 6. Firewall Rules Configuration (Day 3)

### Settings → Firewall & Security → Rules

**Key Rules to Create:**

**Rule 1: Trusted → Management**
- Type: LAN IN
- Source: VLAN 10
- Destination: VLAN 1
- Port: 22, 443, 8443
- Action: Accept
- Logging: Enabled

**Rule 2: IoT → Internet Only**
- Type: LAN IN
- Source: VLAN 50
- Destination: Internet
- Port: 80, 443, 53
- Action: Accept

**Rule 3: IoT → All VLANs DENY**
- Type: LAN IN
- Source: VLAN 50
- Destination: 192.168.0.0/16
- Action: Drop
- Logging: Enabled

**Rule 4: Guest → Internal DENY**
- Type: LAN IN
- Source: VLAN 99
- Destination: 192.168.0.0/16
- Action: Drop
- Logging: Enabled

**Test Firewall:**
```bash
# From IoT device
ping 8.8.8.8          # Should work
ping 192.168.10.10    # Should fail

# From Trusted device
ping 192.168.1.1      # Should work
ping 192.168.50.10    # Should work
```

## 7. Static IP and DHCP Reservations (Day 3)

### Step 7.1: Configure Static IPs

**Proxmox Server:**

```bash
# Edit /etc/network/interfaces
auto eth0
iface eth0 inet static
    address 192.168.10.10
    netmask 255.255.255.0
    gateway 192.168.10.1
    dns-nameservers 192.168.10.2 1.1.1.1
```

**TrueNAS**: Configure via web UI Network → Interfaces

### Step 7.2: Create DHCP Reservations
**Settings → Networks → [VLAN] → DHCP → Reservations**

- Desktop: MAC → 192.168.10.20
- Smart TV: MAC → 192.168.50.10
- Thermostat: MAC → 192.168.50.11

**Validation**: Renew DHCP lease and verify IPs

## 8. DNS Configuration with Pi-hole (Day 4)

### Step 8.1: Install Pi-hole
```bash

ssh pi@192.168.10.2
curl -sSL https://install.pi-hole.net | bash

# Follow prompts:

# - Interface: eth0

# - Static IP: 192.168.10.2

# - Upstream DNS: 1.1.1.1

# - Admin interface: Yes

```

### Step 8.2: Configure DHCP to Use Pi-hole
- UniFi Settings → Networks → Trusted
- DHCP Name Server: 192.168.10.2
- Secondary: 1.1.1.1

### Step 8.3: Test Ad Blocking
```bash
nslookup doubleclick.net 192.168.10.2
# Expected: 0.0.0.0 (blocked)

nslookup google.com 192.168.10.2
# Expected: Real IP (allowed)
```

## 9. VPN Configuration (WireGuard) (Day 4)

### Step 9.1: Enable WireGuard

- Settings → VPN → WireGuard → Enable
- Listen Port: 51820
- Network: 192.168.10.0/24

### Step 9.2: Create VPN User

1. Add user account
2. Generate WireGuard config
3. Download .conf file

### Step 9.3: Test VPN

```bash
# From external network with VPN connected
ping 192.168.10.1    # Should work
```

## 10. Verification and Testing (Day 5)

### Step 10.1: Connectivity Tests
- [ ] Each VLAN can reach internet
- [ ] Trusted devices can ping each other
- [ ] IoT devices CANNOT ping trusted
- [ ] Guest devices CANNOT reach internal

### Step 10.2: Performance Tests
```bash

# Internal speed test

iperf3 -s  # Server
iperf3 -c 192.168.10.10  # Client

# Expected: 900+ Mbps

```

### Step 10.3: Backup Configuration
- Settings → Backup → Download Backup
- Store securely (external drive + cloud)
- Set auto-backup schedule (daily, 7 days retention)

## 11. Documentation and Labeling (Day 5)

- [ ] Label all patch panel ports
- [ ] Label switch ports
- [ ] Document Wi-Fi passwords
- [ ] Create network diagram
- [ ] Store documentation securely

## 12. Ongoing Maintenance

**Weekly:**
- Check UniFi alerts
- Review Pi-hole logs

**Monthly:**
- Update firmware
- Review firewall logs
- Test backup restore

**Quarterly:**
- Review and update firewall rules
- Audit DHCP reservations
- Test VPN

## Rollback Procedure

If deployment fails:
1. Stop at failed step
2. Revert to previous backup (Settings → Backup → Restore)
3. Identify failure point (check logs)
4. Retry failed step
5. Escalate if needed (UniFi community forums)

## Sign-Off Criteria

- ✅ All VLANs operational
- ✅ All SSIDs broadcasting
- ✅ Firewall rules tested
- ✅ Internet connectivity verified
- ✅ VPN tested
- ✅ Backup completed
- ✅ Documentation updated

**Deployment completed by**: [Name]  
**Date**: [Date]  
**Next review**: [Date + 30 days]
