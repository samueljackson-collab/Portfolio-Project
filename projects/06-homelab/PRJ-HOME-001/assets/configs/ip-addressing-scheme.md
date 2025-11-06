# Homelab IP Addressing Scheme

## Overview
Complete IP addressing plan for all VLANs with static assignments, DHCP pools, and reservations.

## Subnetting Summary

| VLAN | Name | Network | Gateway | DHCP Pool | Usable IPs |
|------|------|---------|---------|-----------|------------|
| 1 | Management | 192.168.1.0/24 | 192.168.1.1 | None (static only) | 254 |
| 10 | Trusted | 192.168.10.0/24 | 192.168.10.1 | 100-200 | 254 |
| 50 | IoT | 192.168.50.0/24 | 192.168.50.1 | 100-200 | 254 |
| 99 | Guest | 192.168.99.0/24 | 192.168.99.1 | 100-200 | 254 |
| 100 | Lab | 192.168.100.0/24 | 192.168.100.1 | 100-200 | 254 |

## VLAN 1 - Management Network (192.168.1.0/24)

**Purpose**: Network equipment management only  
**DHCP**: Disabled (static IPs only)

| IP Address | Hostname | Device | Purpose |
|------------|----------|--------|---------|
| 192.168.1.1 | udmp.mgmt | UniFi Dream Machine Pro | Router/Firewall/Gateway |
| 192.168.1.2 | usw24.mgmt | UniFi Switch 24 PoE | Core Switch (95W PoE) |
| 192.168.1.3 | usw8.mgmt | UniFi Switch 8 PoE | Secondary Switch |
| 192.168.1.10 | ap1.mgmt | UniFi AP AC Pro #1 | Living Room AP |
| 192.168.1.11 | ap2.mgmt | UniFi AP AC Pro #2 | Bedroom AP |
| 192.168.1.12 | ap3.mgmt | UniFi AP AC Pro #3 | Office AP |
| 192.168.1.50-254 | - | Reserved | Future expansion |

## VLAN 10 - Trusted Network (192.168.10.0/24)

**Purpose**: Personal devices, workstations, servers  
**DHCP Pool**: 192.168.10.100-200  
**DNS**: 192.168.10.2 (Pi-hole)  
**Lease Time**: 24 hours

### Static Assignments
| IP Address | Hostname | Device | Purpose |
|------------|----------|--------|---------|
| 192.168.10.1 | - | Gateway | VLAN gateway (UDMP) |
| 192.168.10.2 | pihole.trusted | Raspberry Pi 4 | DNS/Ad-blocking |
| 192.168.10.5 | truenas.trusted | TrueNAS Server | Network storage (10G NIC) |
| 192.168.10.10 | proxmox.trusted | Proxmox Host | Virtualization (8 VMs) |
| 192.168.10.30 | printer.trusted | HP LaserJet | Network printer |

### DHCP Reservations
| IP Address | Device | MAC Address | Purpose |
|------------|--------|-------------|---------|
| 192.168.10.20 | desktop.trusted | 00:11:22:33:44:20 | Workstation |
| 192.168.10.21 | laptop1.trusted | 00:11:22:33:44:21 | MacBook Pro |
| 192.168.10.22 | laptop2.trusted | 00:11:22:33:44:22 | ThinkPad |
| 192.168.10.40 | phone1.trusted | 00:11:22:33:44:40 | iPhone 14 |
| 192.168.10.41 | phone2.trusted | 00:11:22:33:44:41 | Android Phone |

## VLAN 50 - IoT Network (192.168.50.0/24)

**Purpose**: Smart home devices (isolated)  
**DHCP Pool**: 192.168.50.100-200  
**DNS**: 1.1.1.1 (Cloudflare, bypass Pi-hole)  
**mDNS Reflector**: Enabled

### Static/Reserved IPs
| IP Address | Hostname | Device | Purpose |
|------------|----------|--------|---------|
| 192.168.50.1 | - | Gateway | VLAN gateway |
| 192.168.50.10 | smart-tv.iot | Samsung TV | Entertainment |
| 192.168.50.11 | thermostat.iot | Ecobee | HVAC control |
| 192.168.50.12 | lock-front.iot | August Lock | Front door |
| 192.168.50.13 | lock-back.iot | August Lock | Back door |
| 192.168.50.20-29 | bulb-*.iot | Philips Hue | Smart lighting (10 bulbs) |
| 192.168.50.30-31 | camera-*.iot | Wyze Cam | Security cameras |
| 192.168.50.40-42 | speaker-*.iot | Echo/Google Home | Smart speakers |

## VLAN 99 - Guest Network (192.168.99.0/24)

**Purpose**: Visitor internet access  
**DHCP Pool**: 192.168.99.100-200  
**DNS**: 1.1.1.1  
**Lease Time**: 4 hours  
**Client Isolation**: Enabled

| IP Address | Assignment |
|------------|-----------|
| 192.168.99.1 | Gateway with captive portal |
| 192.168.99.100-200 | DHCP pool for guest devices |

## VLAN 100 - Lab Network (192.168.100.0/24)

**Purpose**: Testing, experimentation, security research  
**DHCP Pool**: 192.168.100.100-200  
**DNS**: 192.168.10.2  
**Lease Time**: 1 hour

### Static IPs
| IP Address | Hostname | Device | Purpose |
|------------|----------|--------|---------|
| 192.168.100.1 | - | Gateway | VLAN gateway |
| 192.168.100.10 | kali.lab | Kali Linux VM | Pentesting |
| 192.168.100.11 | vulnerable.lab | Metasploitable | Vulnerable target |
| 192.168.100.12-14 | test-*.lab | Test VMs | Development testing |

## DNS Configuration

### DNS Servers by VLAN
| VLAN | Primary DNS | Secondary DNS | Purpose |
|------|-------------|---------------|---------|
| 1 | 192.168.10.2 | 1.1.1.1 | Pi-hole + fallback |
| 10 | 192.168.10.2 | 1.1.1.1 | Ad-blocking |
| 50 | 1.1.1.1 | 8.8.8.8 | Bypass Pi-hole for IoT |
| 99 | 1.1.1.1 | 8.8.8.8 | No internal DNS |
| 100 | 192.168.10.2 | 1.1.1.1 | Pi-hole for testing |

### Local DNS Records (Pi-hole)
| Hostname | IP | Purpose |
|----------|---------|---------|
| homelab.local | 192.168.10.1 | Local domain |
| udmp.homelab.local | 192.168.1.1 | UniFi Controller |
| pihole.homelab.local | 192.168.10.2 | DNS server |
| truenas.homelab.local | 192.168.10.5 | Storage |
| proxmox.homelab.local | 192.168.10.10 | Virtualization |

## DHCP Options
| Option | Value | Purpose |
|--------|-------|---------|
| 3 | Router IP | Gateway for each VLAN |
| 6 | DNS Servers | As specified per VLAN |
| 15 | homelab.local | Domain name |
| 42 | 192.168.1.1 | NTP server |

## IP Allocation Strategy

### Static IP Criteria
- Network infrastructure (switches, APs, routers)
- Servers (Proxmox, TrueNAS, Pi-hole)
- Critical services

### DHCP Reservation Criteria
- IoT devices (tracking and management)
- Regularly used devices
- Test devices during development

### Dynamic DHCP Criteria
- Guest devices (temporary access)
- Mobile devices
- Temporary test VMs

## Adding New Devices

### For Static IP
1. Choose available IP from appropriate VLAN
2. Configure device with static IP, subnet, gateway, DNS
3. Update this document
4. Test connectivity

### For DHCP Reservation
1. Find device MAC address
2. Login to UniFi Controller → Networks → DHCP Reservations
3. Add reservation (MAC → IP)
4. Update this document
5. Renew DHCP lease on device

### For Dynamic DHCP
1. Connect device to appropriate VLAN/SSID
2. Verify IP assignment from correct pool
3. No documentation update needed

## Monitoring and Cleanup
- **Weekly**: Review DHCP leases
- **Monthly**: Audit static IPs
- **Quarterly**: Update this document
- **Annually**: Consider renumbering if needed

For subnet calculator and detailed IP planning, see network design documentation.
