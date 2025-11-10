# Homelab IP Addressing Scheme

## Overview
This document defines the complete IP addressing scheme for all VLANs in the homelab network, including static assignments, DHCP pools, and IP reservations.

## Subnetting Summary

| VLAN | Name | Network | Subnet Mask | Gateway | Usable IPs | Broadcast |
|------|------|---------|-------------|---------|------------|-----------|
| 1 | Management | 192.168.1.0/24 | 255.255.255.0 | 192.168.1.1 | 192.168.1.2-254 | 192.168.1.255 |
| 10 | Trusted | 192.168.10.0/24 | 255.255.255.0 | 192.168.10.1 | 192.168.10.2-254 | 192.168.10.255 |
| 50 | IoT | 192.168.50.0/24 | 255.255.255.0 | 192.168.50.1 | 192.168.50.2-254 | 192.168.50.255 |
| 99 | Guest | 192.168.99.0/24 | 255.255.255.0 | 192.168.99.1 | 192.168.99.2-254 | 192.168.99.255 |
| 100 | Lab | 192.168.100.0/24 | 255.255.255.0 | 192.168.100.1 | 192.168.100.2-254 | 192.168.100.255 |

## VLAN 1 - Management Network (192.168.1.0/24)

**Purpose**: Network equipment management only  
**DHCP**: Disabled (static IPs only)  
**DNS**: 192.168.10.2 (Pi-hole) via firewall rules

| IP Address | Hostname | Device Type | MAC Address | Purpose | Notes |
|------------|----------|-------------|-------------|---------|-------|
| 192.168.1.1 | udmp.mgmt | UniFi Dream Machine Pro | 00:11:22:33:44:01 | Router/Firewall | Gateway for all VLANs |
| 192.168.1.2 | usw24.mgmt | UniFi Switch 24 PoE | 00:11:22:33:44:02 | Core Switch | PoE for APs, 95W budget |
| 192.168.1.3 | usw8.mgmt | UniFi Switch 8 PoE | 00:11:22:33:44:03 | Secondary Switch | Remote location |
| 192.168.1.10 | ap1.mgmt | UniFi AP AC Pro #1 | 00:11:22:33:44:04 | Access Point | Living room, all SSIDs |
| 192.168.1.11 | ap2.mgmt | UniFi AP AC Pro #2 | 00:11:22:33:44:05 | Access Point | Bedroom, trusted/guest only |
| 192.168.1.12 | ap3.mgmt | UniFi AP AC Pro #3 | 00:11:22:33:44:06 | Access Point | Office, all SSIDs |
| 192.168.1.50 | - | Reserved | - | Future AP | Expansion capacity |
| 192.168.1.51 | - | Reserved | - | Future switch | - |
| 192.168.1.254 | - | Reserved | - | - | - |

## VLAN 10 - Trusted Network (192.168.10.0/24)

**Purpose**: Personal devices, workstations, trusted servers  
**DHCP**: Enabled (192.168.10.100-200)  
**DNS**: 192.168.10.2 (Pi-hole)  
**Lease Time**: 24 hours

| IP Address | Hostname | Device Type | Assignment Type | Purpose | Notes |
|------------|----------|-------------|-----------------|---------|-------|
| 192.168.10.1 | - | Gateway | Static | VLAN gateway | UDMP interface |
| 192.168.10.2 | pihole.trusted | Raspberry Pi 4 | Static | DNS/Ad-blocking | Also responds on 192.168.1.2 |
| 192.168.10.5 | truenas.trusted | TrueNAS Server | Static | Network storage | 10G NIC, NFS/SMB shares |
| 192.168.10.10 | proxmox.trusted | Proxmox Host | Static | Virtualization | Hosts 8 VMs/containers |
| 192.168.10.20 | desktop.trusted | Desktop PC | DHCP Reservation | Workstation | Admin device, gaming |
| 192.168.10.21 | laptop1.trusted | MacBook Pro | DHCP | Personal laptop | 00:11:22:33:44:21 |
| 192.168.10.22 | laptop2.trusted | ThinkPad | DHCP | Work laptop | 00:11:22:33:44:22 |
| 192.168.10.30 | printer.trusted | HP LaserJet | Static | Network printer | - |
| 192.168.10.31 | nas-backup.trusted | External HDD | Static | Backup target | USB connected to TrueNAS |
| 192.168.10.40 | phone1.trusted | iPhone 14 | DHCP | Personal phone | 00:11:22:33:44:40 |
| 192.168.10.41 | phone2.trusted | Android Phone | DHCP | Personal phone | 00:11:22:33:44:41 |
| 192.168.10.50 | tablet.trusted | iPad Pro | DHCP | Tablet | 00:11:22:33:44:50 |
| 192.168.10.100-200 | - | DHCP Pool | DHCP | Dynamic assignments | 100 IPs available |

## VLAN 50 - IoT Network (192.168.50.0/24)

**Purpose**: Smart home devices (isolated)  
**DHCP**: Enabled (192.168.50.100-200)  
**DNS**: 1.1.1.1 (Cloudflare, bypass Pi-hole)  
**Lease Time**: 24 hours  
**mDNS Reflector**: Enabled

| IP Address | Hostname | Device Type | Assignment Type | Purpose | Notes |
|------------|----------|-------------|-----------------|---------|-------|
| 192.168.50.1 | - | Gateway | Static | VLAN gateway | UDMP interface |
| 192.168.50.10 | smart-tv.iot | Samsung TV | Static | Entertainment | Isolated from trusted |
| 192.168.50.11 | thermostat.iot | Ecobee Smart Thermostat | DHCP Reservation | HVAC control | 00:11:22:33:44:51 |
| 192.168.50.12 | lock-front.iot | August Smart Lock | DHCP Reservation | Front door lock | HomeKit compatible |
| 192.168.50.13 | lock-back.iot | August Smart Lock | DHCP Reservation | Back door lock | HomeKit compatible |
| 192.168.50.14 | garage.iot | MyQ Garage Opener | DHCP Reservation | Garage control | 00:11:22:33:44:54 |
| 192.168.50.20-29 | bulb-*.iot | Philips Hue Bulbs | DHCP | Smart lighting | 10 bulbs, bridge at .20 |
| 192.168.50.30 | camera-front.iot | Wyze Cam v3 | DHCP Reservation | Security camera | Cloud recording |
| 192.168.50.31 | camera-back.iot | Wyze Cam v3 | DHCP Reservation | Security camera | Cloud recording |
| 192.168.50.32 | camera-garage.iot | Wyze Cam Pan | DHCP Reservation | Security camera | 00:11:22:33:44:62 |
| 192.168.50.40 | echo1.iot | Amazon Echo Dot | DHCP Reservation | Smart speaker | Alexa |
| 192.168.50.41 | echo2.iot | Amazon Echo Show | DHCP Reservation | Smart display | 00:11:22:33:44:71 |
| 192.168.50.42 | google-home.iot | Google Home Mini | DHCP Reservation | Smart speaker | Google Assistant |
| 192.168.50.50 | vacuum.iot | Roborock S7 | DHCP Reservation | Robot vacuum | 00:11:22:33:44:80 |
| 192.168.50.100-200 | - | DHCP Pool | DHCP | Dynamic assignments | 100 IPs available |

## VLAN 99 - Guest Network (192.168.99.0/24)

**Purpose**: Visitor internet access  
**DHCP**: Enabled (192.168.99.100-200)  
**DNS**: 1.1.1.1 (Cloudflare)  
**Lease Time**: 4 hours  
**Client Isolation**: Enabled  
**Captive Portal**: Enabled

| IP Address | Hostname | Device Type | Assignment Type | Purpose | Notes |
|------------|----------|-------------|-----------------|---------|-------|
| 192.168.99.1 | - | Gateway | Static | VLAN gateway | UDMP with captive portal |
| 192.168.99.100-200 | - | DHCP Pool | DHCP | Guest devices | 100 IPs, 4-hour lease |

## VLAN 100 - Lab Network (192.168.100.0/24)

**Purpose**: Testing, experimentation, security research  
**DHCP**: Enabled (192.168.100.100-200)  
**DNS**: 192.168.10.2 (Pi-hole)  
**Lease Time**: 1 hour  
**Rate Limiting**: 50 Mbps total

| IP Address | Hostname | Device Type | Assignment Type | Purpose | Notes |
|------------|----------|-------------|-----------------|---------|-------|
| 192.168.100.1 | - | Gateway | Static | VLAN gateway | UDMP interface |
| 192.168.100.10 | kali.lab | Kali Linux VM | Static | Penetration testing | On Proxmox host |
| 192.168.100.11 | vulnerable.lab | Metasploitable VM | Static | Intentionally vulnerable | Isolated testing |
| 192.168.100.12 | ubuntu-test.lab | Ubuntu Server VM | DHCP Reservation | Testing | 00:11:22:33:44:A0 |
| 192.168.100.13 | windows-test.lab | Windows 10 VM | DHCP Reservation | Testing | 00:11:22:33:44:A1 |
| 192.168.100.14 | docker-test.lab | Docker Host VM | DHCP Reservation | Container testing | 00:11:22:33:44:A2 |
| 192.168.100.20 | pi-zero.lab | Raspberry Pi Zero | Static | IoT testing | Wireless connected |
| 192.168.100.100-200 | - | DHCP Pool | DHCP | Test VMs | 100 IPs, 1-hour lease |

## DNS Configuration

### DNS Servers by VLAN
| VLAN | Primary DNS | Secondary DNS | Purpose |
|------|-------------|---------------|---------|
| 1 (Management) | 192.168.10.2 | 1.1.1.1 | Pi-hole + fallback |
| 10 (Trusted) | 192.168.10.2 | 1.1.1.1 | Ad-blocking + fallback |
| 50 (IoT) | 1.1.1.1 | 8.8.8.8 | Bypass Pi-hole for IoT |
| 99 (Guest) | 1.1.1.1 | 8.8.8.8 | No internal DNS |
| 100 (Lab) | 192.168.10.2 | 1.1.1.1 | Pi-hole for testing |

### Local DNS Records (Pi-hole)
| Hostname | IP Address | Type | Purpose |
|----------|------------|------|---------|
| homelab.local | 192.168.10.1 | A | Local domain |
| udmp.homelab.local | 192.168.1.1 | A | UniFi Controller |
| pihole.homelab.local | 192.168.10.2 | A | DNS/Ad-blocking |
| truenas.homelab.local | 192.168.10.5 | A | Network storage |
| proxmox.homelab.local | 192.168.10.10 | A | Virtualization |
| grafana.homelab.local | 192.168.10.11 | A | Monitoring dashboards |
| prometheus.homelab.local | 192.168.10.12 | A | Metrics collection |

## DHCP Configuration Details

### Global DHCP Settings
- **Domain Name**: homelab.local
- **NTP Server**: 192.168.1.1 (UDMP syncs from pool.ntp.org)
- **Lease Time**: Configurable per VLAN (see above)

### DHCP Options
| Option | Value | Purpose |
|--------|-------|---------|
| 3 | Router IP | Gateway for each VLAN |
| 6 | DNS Servers | As specified per VLAN |
| 15 | homelab.local | Domain name |
| 42 | 192.168.1.1 | NTP server |

## IP Allocation Strategy

### Static IP Assignment Criteria
- **Network Infrastructure**: Always static (switches, APs, gateways)
- **Servers**: Always static (Proxmox, TrueNAS, Pi-hole)
- **Critical Services**: Static if they provide network services
- **Printers**: Static for reliable network printing

### DHCP Reservation Criteria
- **IoT Devices**: Reservations for tracking and management
- **Regularly Used Devices**: Reservations for consistent access
- **Test Devices**: Reservations during development phases

### Dynamic DHCP Criteria
- **Guest Devices**: Always dynamic (temporary access)
- **Mobile Devices**: Dynamic when not needing fixed IP
- **Temporary Test VMs**: Dynamic for lab environment

## Visual Subnet Map

```
Management VLAN (1)
192.168.1.0/24
├── 192.168.1.1      UDMP Gateway
├── 192.168.1.2      Switch 24
├── 192.168.1.3      Switch 8
├── 192.168.1.10-12  Access Points
└── 192.168.1.50+    Reserved

Trusted VLAN (10)  
192.168.10.0/24
├── 192.168.10.1     Gateway
├── 192.168.10.2-19  Infrastructure (static)
├── 192.168.10.20-49 User devices (reservations)
└── 192.168.10.100-200 DHCP pool

IoT VLAN (50)
192.168.50.0/24
├── 192.168.50.1     Gateway
├── 192.168.50.10-99 IoT devices (static/reservations)
└── 192.168.50.100-200 DHCP pool

Guest VLAN (99)
192.168.99.0/24
├── 192.168.99.1     Gateway + Captive Portal
└── 192.168.99.100-200 DHCP pool (4-hour leases)

Lab VLAN (100)
192.168.100.0/24
├── 192.168.100.1    Gateway
├── 192.168.100.10-49 Test VMs (static/reservations)
└── 192.168.100.100-200 DHCP pool (1-hour leases)
```

## Adding New Devices

### Procedure for Static IP Assignment
1. **Determine if static IP is needed** (server, infrastructure, critical service)
2. **Choose available IP** from appropriate VLAN range
3. **Configure device** with static IP, subnet, gateway, DNS
4. **Update this document** with new device information
5. **Test connectivity** from multiple VLANs (if needed)

### Procedure for DHCP Reservation
1. **Find device MAC address** (usually on label or via DHCP leases)
2. **Login to UniFi Controller** → Networks → DHCP Reservations
3. **Add reservation** (MAC → IP) in appropriate VLAN
4. **Update this document** with reservation details
5. **Renew DHCP lease** on device to get reserved IP

### Procedure for Dynamic DHCP
1. **Connect device** to appropriate VLAN/SSID
2. **Verify IP assignment** from correct DHCP pool
3. **Monitor device** in UniFi Controller if needed
4. **No documentation update required** for temporary devices

## IP Address Conservation

### Reserved Ranges by VLAN
| VLAN | Reserved Range | Purpose |
|------|----------------|---------|
| 1 | 192.168.1.50-254 | Future network equipment |
| 10 | 192.168.10.60-99 | Future servers/services |
| 50 | 192.168.50.60-99 | Future IoT devices |
| 100 | 192.168.100.50-99 | Future lab equipment |

### Monitoring and Cleanup
- **Weekly**: Review DHCP leases for stale entries
- **Monthly**: Audit static IP assignments
- **Quarterly**: Review and update this IP scheme document
- **Annually**: Consider renumbering if significant changes occur

This IP addressing scheme provides organized, scalable addressing with clear documentation for ongoing network management and troubleshooting.
