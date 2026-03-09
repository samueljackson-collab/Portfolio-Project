# IP Addressing Scheme

## Network Overview

| VLAN | Network | Subnet Mask | Gateway | DHCP Range | Static Range | Purpose |
|------|---------|-------------|---------|------------|--------------|---------|
| 10 | 192.168.10.0/24 | 255.255.255.0 | 192.168.10.1 | .100-.200 | .1-.99 | Trusted devices |
| 30 | 192.168.30.0/24 | 255.255.255.0 | 192.168.30.1 | N/A | .1-.50 | Management only |
| 50 | 192.168.50.0/24 | 255.255.255.0 | 192.168.50.1 | .100-.250 | .1-.99 | IoT devices |
| 99 | 192.168.99.0/24 | 255.255.255.0 | 192.168.99.1 | .100-.250 | .1-.99 | Guest network |

## VLAN 10 - Trusted Network (192.168.10.0/24)

### Reserved/Infrastructure (.1-.9)
| IP Address | Hostname | Device Type | MAC Address | Notes |
|------------|----------|-------------|-------------|-------|
| 192.168.10.1 | gateway-vlan10 | UDMP (SVI) | N/A | Default gateway |
| 192.168.10.2 | pihole-primary | Pi-hole DNS | 00:11:22:33:44:55 | Primary DNS server |
| 192.168.10.3 | pihole-secondary | Pi-hole DNS | 00:11:22:33:44:56 | Secondary DNS (optional) |

### Servers & Infrastructure (.10-.49)
| IP Address | Hostname | Device Type | MAC Address | Notes |
|------------|----------|-------------|-------------|-------|
| 192.168.10.10 | proxmox-host | Proxmox VE Host | AA:BB:CC:DD:EE:01 | Hypervisor host |
| 192.168.10.11 | proxmox-host2 | Proxmox VE Host | AA:BB:CC:DD:EE:02 | Second host (future) |
| 192.168.10.12 | pbs-01 | Proxmox Backup Server | AA:BB:CC:DD:EE:03 | Backup server |
| 192.168.10.15 | truenas | TrueNAS Core | AA:BB:CC:DD:EE:04 | NAS/Storage server |
| 192.168.10.20 | wiki | Wiki.js Container | N/A (virtual) | Documentation wiki |
| 192.168.10.21 | immich | Immich Container | N/A (virtual) | Photo management |
| 192.168.10.22 | nextcloud | Nextcloud Container | N/A (virtual) | Cloud storage (future) |
| 192.168.10.25 | nginx-proxy | Nginx Proxy Manager | N/A (virtual) | Reverse proxy |
| 192.168.10.30 | monitoring | Observability Stack | N/A (virtual) | Prometheus/Grafana |

### Workstations (.50-.99)
| IP Address | Hostname | Device Type | MAC Address | Notes |
|------------|----------|-------------|-------------|-------|
| 192.168.10.50 | desktop-main | Desktop PC | 11:22:33:44:55:01 | Primary workstation |
| 192.168.10.51 | desktop-gaming | Gaming PC | 11:22:33:44:55:02 | Secondary workstation |
| 192.168.10.60 | laptop-work | Laptop | 11:22:33:44:55:03 | Work laptop |

### DHCP Pool (.100-.200)
Reserved for dynamic assignment to trusted devices:
- Phones, tablets
- Temporary devices
- Guest trusted devices

## VLAN 30 - Management Network (192.168.30.0/24)

### Network Equipment (.1-.20)
| IP Address | Hostname | Device Type | MAC Address | Notes |
|------------|----------|-------------|-------------|-------|
| 192.168.30.1 | udmp | UniFi Dream Machine Pro | BB:CC:DD:EE:FF:01 | Gateway/Firewall |
| 192.168.30.2 | switch-core | UniFi Pro Switch 24 | BB:CC:DD:EE:FF:02 | Core switch |
| 192.168.30.3 | switch-access | UniFi Pro Switch 8 | BB:CC:DD:EE:FF:03 | Access switch |
| 192.168.30.10 | ap-main-floor | UniFi AP-AC-Pro | BB:CC:DD:EE:FF:04 | Main floor AP |
| 192.168.30.11 | ap-upper-floor | UniFi AP-AC-Lite | BB:CC:DD:EE:FF:05 | Upper floor AP |
| 192.168.30.12 | ap-garage | UniFi AP-FlexHD | BB:CC:DD:EE:FF:06 | Garage AP (future) |

### Out-of-Band Management (.21-.50)
| IP Address | Hostname | Device Type | MAC Address | Notes |
|------------|----------|-------------|-------------|-------|
| 192.168.30.21 | proxmox-ipmi | IPMI Interface | CC:DD:EE:FF:00:01 | Server IPMI |
| 192.168.30.22 | truenas-ipmi | IPMI Interface | CC:DD:EE:FF:00:02 | NAS IPMI (if equipped) |

## VLAN 50 - IoT Network (192.168.50.0/24)

### Smart Home Hub (.10-.19)
| IP Address | Hostname | Device Type | MAC Address | Notes |
|------------|----------|-------------|-------------|-------|
| 192.168.50.10 | homeassistant | Home Assistant VM | N/A (virtual) | Smart home controller |
| 192.168.50.11 | zigbee2mqtt | Zigbee2MQTT | N/A (container) | Zigbee gateway |
| 192.168.50.12 | zwave | Z-Wave Controller | N/A (add-on) | Z-Wave gateway |

### Security Cameras (.20-.39)
| IP Address | Hostname | Device Type | MAC Address | Notes |
|------------|----------|-------------|-------------|-------|
| 192.168.50.20 | camera-front | IP Camera | DD:EE:FF:00:11:01 | Front door |
| 192.168.50.21 | camera-back | IP Camera | DD:EE:FF:00:11:02 | Backyard |
| 192.168.50.22 | camera-garage | IP Camera | DD:EE:FF:00:11:03 | Garage |
| 192.168.50.23 | camera-side | IP Camera | DD:EE:FF:00:11:04 | Side yard |
| 192.168.50.30 | nvr | Frigate NVR | N/A (container) | Video recording |

### Smart Home Devices (.40-.99)
| IP Address | Hostname | Device Type | MAC Address | Notes |
|------------|----------|-------------|-------------|-------|
| 192.168.50.40 | thermostat | Smart Thermostat | EE:FF:00:11:22:01 | HVAC control |
| 192.168.50.41 | doorbell | Video Doorbell | EE:FF:00:11:22:02 | Smart doorbell |
| 192.168.50.50 | tv-living | Smart TV | EE:FF:00:11:22:03 | Living room TV |
| 192.168.50.51 | tv-bedroom | Smart TV | EE:FF:00:11:22:04 | Bedroom TV |

### DHCP Pool (.100-.250)
Reserved for:
- Smart plugs
- Smart lights (Philips Hue, etc.)
- Smart speakers
- Other IoT devices

## VLAN 99 - Guest Network (192.168.99.0/24)

### Infrastructure (.1-.9)
| IP Address | Hostname | Device Type | MAC Address | Notes |
|------------|----------|-------------|-------------|-------|
| 192.168.99.1 | gateway-guest | UDMP (SVI) | N/A | Default gateway |

### DHCP Pool (.100-.250)
Reserved for guest devices:
- Visitor phones
- Visitor laptops
- Visitor tablets
- Client isolation enabled

## DNS Configuration

### Primary DNS Servers
- **Primary:** 192.168.10.2 (Pi-hole)
- **Secondary:** 192.168.10.3 (Pi-hole) or 1.1.1.1 (Cloudflare)

### DNS Resolution Flow
1. Client queries 192.168.10.2
2. Pi-hole checks blocklist
3. If not blocked, forwards to upstream (1.1.1.1 or 1.0.0.1)
4. Result cached and returned to client

### Local DNS Records

| FQDN | IP Address | Type | Purpose |
|------|------------|------|---------|
| gateway.homelab.local | 192.168.10.1 | A | Gateway |
| proxmox.homelab.local | 192.168.10.10 | A | Hypervisor |
| truenas.homelab.local | 192.168.10.15 | A | NAS |
| wiki.homelab.local | 192.168.10.20 | A | Wiki |
| photos.homelab.local | 192.168.10.21 | A | Immich |
| proxy.homelab.local | 192.168.10.25 | A | Nginx Proxy Manager |
| homeassistant.homelab.local | 192.168.50.10 | A | Home Assistant |
| *.homelab.local | 192.168.10.25 | CNAME | Wildcard to proxy |

## IP Reservation Management

### Static Assignments
- Manually configured on device: Infrastructure and servers
- DHCP reservation: Workstations and important IoT devices

### DHCP Lease Time
- **VLAN 10 (Trusted):** 24 hours
- **VLAN 30 (Management):** N/A (all static)
- **VLAN 50 (IoT):** 12 hours
- **VLAN 99 (Guest):** 4 hours

## IP Address Change Procedure

When changing a static IP:
1. Update device configuration
2. Update DNS records (Pi-hole)
3. Update Prometheus targets (if monitored)
4. Update firewall rules (if referenced)
5. Update documentation (this file)
6. Test connectivity
7. Update runbooks/playbooks

## Capacity Planning

| VLAN | Total IPs | Reserved | DHCP Pool | Utilization | Headroom |
|------|-----------|----------|-----------|-------------|----------|
| 10 | 254 | 99 | 101 | ~30% | 70% |
| 30 | 254 | 50 | 0 | ~8% | 92% |
| 50 | 254 | 99 | 151 | ~25% | 75% |
| 99 | 254 | 99 | 151 | ~5% | 95% |

### Growth Projections
- **VLAN 10:** Current 20 static + 10 DHCP = 30 total. Projected growth: 5-10 devices/year.
- **VLAN 30:** Current 5 devices. Projected growth: 2-3 devices/year.
- **VLAN 50:** Current 15 static + 20 DHCP = 35 total. Projected growth: 10-15 devices/year.
- **VLAN 99:** Variable (0-20 concurrent guests). No growth projection needed.

## IP Addressing Best Practices

1. **Sequential Assignment:** Assign IPs sequentially within ranges
2. **Gap Management:** Leave gaps for future expansion in each category
3. **Documentation:** Update this document immediately upon changes
4. **MAC Binding:** Use DHCP reservations for semi-permanent devices
5. **Monitoring:** Alert on DHCP pool >80% utilization
