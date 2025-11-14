# IP Address Allocation Table

**Purpose:** Comprehensive IP address inventory for homelab infrastructure
**Last Updated:** 2024-12-16
**Owner:** Samuel Jackson

---

## VLAN Overview

| VLAN ID | Name | Subnet | Gateway | Purpose | Trust Level |
|---------|------|--------|---------|---------|-------------|
| 10 | Management | 192.168.10.0/24 | 192.168.10.1 | Infrastructure management | High |
| 20 | Admin | 192.168.20.0/24 | 192.168.20.1 | Administrative workstations | High |
| 30 | Application | 192.168.30.0/24 | 192.168.30.1 | User-facing services | Medium |
| 40 | IoT | 192.168.40.0/24 | 192.168.40.1 | Smart home devices | Low |
| 50 | Protect | 192.168.50.0/24 | 192.168.50.1 | UniFi cameras and NVR | Low |

---

## VLAN 10: Management (192.168.10.0/24)

**Purpose:** Core infrastructure and management interfaces
**Access:** VPN-only, MFA required
**Firewall Policy:** Deny all from WAN, allow from VLAN 20

| IP Address | Hostname | Device Type | MAC Address | Purpose | Status |
|------------|----------|-------------|-------------|---------|--------|
| 192.168.10.1 | gateway.mgmt | UniFi Dream Machine Pro | TBD | Primary gateway | 🟢 Active |
| 192.168.10.2 | unifi-controller.mgmt | UniFi Controller | TBD | Network management | 🟢 Active |
| 192.168.10.10 | proxmox-01.mgmt | Proxmox VE Host | TBD | Hypervisor management | 🟢 Active |
| 192.168.10.11 | truenas-01.mgmt | TrueNAS CORE | TBD | Storage management | 🟢 Active |
| 192.168.10.12 | switch-01.mgmt | UniFi Switch 24 PoE | TBD | Core switch management | 🟢 Active |
| 192.168.10.13 | switch-02.mgmt | UniFi Switch 8 PoE | TBD | Secondary switch | 🟢 Active |
| 192.168.10.20 | pve-backup.mgmt | Proxmox Backup Server | TBD | Backup target (future) | ⚪ Planned |
| 192.168.10.50-99 | reserved-mgmt | Reserved | - | Future infrastructure | ⚪ Reserved |
| 192.168.10.100-200 | dhcp-pool-mgmt | DHCP Pool | - | Temporary management access | 🟡 DHCP |

---

## VLAN 20: Admin (192.168.20.0/24)

**Purpose:** Administrative workstations and secure access
**Access:** VPN-only for remote, local LAN for on-site
**Firewall Policy:** Allow to VLAN 10, allow to VLAN 30, deny from all others

| IP Address | Hostname | Device Type | MAC Address | Purpose | Status |
|------------|----------|-------------|-------------|---------|--------|
| 192.168.20.1 | gateway.admin | UniFi Gateway | TBD | VLAN gateway | 🟢 Active |
| 192.168.20.10 | wireguard-01.admin | WireGuard VPN Server | TBD | VPN endpoint | 🟢 Active |
| 192.168.20.15 | admin-laptop-01 | Laptop | TBD | Primary admin workstation | 🟢 Active |
| 192.168.20.16 | admin-laptop-02 | Laptop | TBD | Secondary admin workstation | ⚪ Planned |
| 192.168.20.20 | admin-desktop-01 | Desktop | TBD | Admin desktop workstation | ⚪ Planned |
| 192.168.20.50-99 | reserved-admin | Reserved | - | Future admin devices | ⚪ Reserved |
| 192.168.20.100-200 | dhcp-pool-admin | DHCP Pool | - | Temporary admin access | 🟡 DHCP |

---

## VLAN 30: Application (192.168.30.0/24)

**Purpose:** User-facing services and applications
**Access:** Accessible from VLAN 20 and via reverse proxy
**Firewall Policy:** Allow from VLAN 20, allow to VLAN 50, deny to VLAN 10

| IP Address | Hostname | Device Type | Purpose | Container/VM | Status |
|------------|----------|-------------|---------|--------------|--------|
| 192.168.30.1 | gateway.app | UniFi Gateway | VLAN gateway | - | 🟢 Active |
| 192.168.30.10 | docker-01.app | Docker Host | Container runtime | VM 100 | 🟢 Active |
| 192.168.30.15 | nginx-proxy.app | Nginx Proxy Manager | Reverse proxy & TLS | Container | 🟢 Active |
| 192.168.30.20 | monitoring.app | Monitoring Stack | Prometheus/Grafana/Loki | Container | 🟢 Active |
| 192.168.30.25 | immich.app | Immich Photo Service | Family photo service | Container | 🟢 Active |
| 192.168.30.26 | immich-db.app | PostgreSQL | Immich database | Container | 🟢 Active |
| 192.168.30.30 | wikijs.app | Wiki.js | Documentation wiki | Container | 🟢 Active |
| 192.168.30.31 | wikijs-db.app | PostgreSQL | Wiki database | Container | 🟢 Active |
| 192.168.30.35 | syncthing.app | Syncthing | Multi-site replication | Container | 🟢 Active |
| 192.168.30.40 | vaultwarden.app | Vaultwarden | Password manager | Container | ⚪ Planned |
| 192.168.30.45 | homepage.app | Homepage Dashboard | Service dashboard | Container | ⚪ Planned |
| 192.168.30.50-99 | reserved-app | Reserved | Future services | - | ⚪ Reserved |
| 192.168.30.100-200 | dhcp-pool-app | DHCP Pool | User devices | - | 🟡 DHCP |

---

## VLAN 40: IoT (192.168.40.0/24)

**Purpose:** Smart home and IoT devices
**Access:** Internet only, isolated from other VLANs
**Firewall Policy:** Deny to all RFC1918, allow to WAN only

| IP Address | Hostname | Device Type | Purpose | Status |
|------------|----------|-------------|---------|--------|
| 192.168.40.1 | gateway.iot | UniFi Gateway | VLAN gateway | 🟢 Active |
| 192.168.40.10 | homeassistant.iot | Home Assistant | IoT hub (future) | ⚪ Planned |
| 192.168.40.20-50 | reserved-iot | Reserved | Future IoT integration | ⚪ Reserved |
| 192.168.40.100-200 | dhcp-pool-iot | DHCP Pool | Smart devices | 🟡 DHCP |

**Typical IoT Devices (DHCP):**
- Smart lights (Philips Hue, etc.)
- Smart plugs
- Smart speakers
- Thermostats
- Sensors

---

## VLAN 50: Protect (192.168.50.0/24)

**Purpose:** UniFi Protect cameras and NVR
**Access:** Application VLAN for viewing, isolated otherwise
**Firewall Policy:** Allow from VLAN 30 only, deny all other inter-VLAN

| IP Address | Hostname | Device Type | Purpose | Status |
|------------|----------|-------------|---------|--------|
| 192.168.50.1 | gateway.protect | UniFi Gateway | VLAN gateway | 🟢 Active |
| 192.168.50.10 | nvr-01.protect | UniFi NVR | Network Video Recorder | ⚪ Planned |
| 192.168.50.20 | camera-front.protect | G4 Doorbell | Front door camera | ⚪ Planned |
| 192.168.50.21 | camera-back.protect | G4 Bullet | Backyard camera | ⚪ Planned |
| 192.168.50.22 | camera-garage.protect | G4 Bullet | Garage camera | ⚪ Planned |
| 192.168.50.23 | camera-side.protect | G4 Bullet | Side yard camera | ⚪ Planned |
| 192.168.50.30-99 | reserved-protect | Reserved | Future cameras | ⚪ Reserved |

---

## VPN Network (WireGuard)

**Subnet:** 10.10.10.0/24
**Gateway:** 10.10.10.1 (WireGuard server)

| IP Address | Hostname | Device Type | Owner | Purpose | Status |
|------------|----------|-------------|-------|---------|--------|
| 10.10.10.1 | wg0-server | WireGuard Server | - | VPN gateway | 🟢 Active |
| 10.10.10.10 | wg-admin-laptop | Admin Laptop | Samuel Jackson | Primary remote access | 🟢 Active |
| 10.10.10.11 | wg-admin-phone | Admin Phone | Samuel Jackson | Mobile remote access | 🟢 Active |
| 10.10.10.20 | wg-sponsor-laptop | Sponsor Laptop | Andrew Vongsady | Secondary admin access | 🟢 Active |
| 10.10.10.30-50 | reserved-vpn | Reserved | - | Future VPN clients | ⚪ Reserved |

**VPN Client Access:**
- Full access to VLAN 20 (Admin)
- Full access to VLAN 10 (Management) via VLAN 20
- No direct access to other VLANs (routing through firewalls)

---

## Special Purpose Networks

### Proxmox Cluster Network (Future)

**Subnet:** 10.0.10.0/24 (Dedicated NIC)
**Purpose:** Corosync/cluster communication
**Status:** ⚪ Planned for future expansion

### iSCSI Storage Network (Future)

**Subnet:** 10.0.20.0/24 (Dedicated NIC)
**Purpose:** High-performance storage traffic
**Status:** ⚪ Planned for future expansion

---

## DNS Records (Internal)

**Primary DNS Server:** 192.168.10.1 (UniFi Gateway)
**Secondary DNS:** 1.1.1.1 (Cloudflare)

### Internal DNS Zones

**Zone:** homelab.local

| Record | Type | Value | Purpose |
|--------|------|-------|---------|
| gateway.homelab.local | A | 192.168.10.1 | Gateway |
| proxmox.homelab.local | A | 192.168.10.10 | Proxmox web UI |
| truenas.homelab.local | A | 192.168.10.11 | TrueNAS web UI |
| photos.homelab.local | A | 192.168.30.15 | Immich service (via proxy) |
| grafana.homelab.local | A | 192.168.30.15 | Grafana (via proxy) |
| prometheus.homelab.local | A | 192.168.30.15 | Prometheus (via proxy) |
| wiki.homelab.local | A | 192.168.30.15 | Wiki.js (via proxy) |
| proxy.homelab.local | A | 192.168.30.15 | Nginx Proxy Manager |
| vpn.homelab.local | A | 192.168.20.10 | WireGuard VPN |

**Wildcard:** *.homelab.local → 192.168.30.15 (Nginx Proxy Manager)

---

## Port Allocations

### Standard Services

| Service | Port | Protocol | VLAN | Notes |
|---------|------|----------|------|-------|
| SSH | 22 | TCP | 10, 20 | Key auth only |
| DNS | 53 | UDP | All | Internal DNS |
| HTTP | 80 | TCP | 30 | Redirect to HTTPS |
| HTTPS | 443 | TCP | 30 | Primary web access |
| NFS | 2049 | TCP | 10, 30 | TrueNAS exports |
| Proxmox Web | 8006 | TCP | 10 | Management UI |
| TrueNAS Web | 80/443 | TCP | 10 | Management UI |
| WireGuard VPN | 51820 | UDP | 20 | VPN endpoint |

### Application-Specific Ports

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Immich | 3001 | TCP | Photo service API |
| Prometheus | 9090 | TCP | Metrics collection |
| Grafana | 3000 | TCP | Dashboard UI |
| Loki | 3100 | TCP | Log aggregation |
| Node Exporter | 9100 | TCP | System metrics |
| cAdvisor | 8080 | TCP | Container metrics |
| Alertmanager | 9093 | TCP | Alert management |
| PostgreSQL | 5432 | TCP | Database (internal) |
| Redis | 6379 | TCP | Cache (internal) |
| Syncthing | 22000 | TCP | File sync |
| Syncthing GUI | 8384 | TCP | Admin interface |

---

## DHCP Pools and Reservations

### DHCP Server: UniFi Gateway (192.168.10.1)

| VLAN | DHCP Range | Lease Time | DNS Server | Gateway |
|------|------------|------------|------------|---------|
| 10 | 192.168.10.100-200 | 24 hours | 192.168.10.1 | 192.168.10.1 |
| 20 | 192.168.20.100-200 | 12 hours | 192.168.10.1 | 192.168.20.1 |
| 30 | 192.168.30.100-200 | 24 hours | 192.168.10.1 | 192.168.30.1 |
| 40 | 192.168.40.100-200 | 24 hours | 192.168.10.1 | 192.168.40.1 |
| 50 | 192.168.50.100-200 | 24 hours | 192.168.10.1 | 192.168.50.1 |

### Static Reservations (by MAC)

**Format:** `[hostname] - [MAC] - [IP] - [VLAN]`

*To be populated as devices are deployed*

---

## Network Diagram Reference

```
┌─────────────────────────────────────────────────────────┐
│                    Internet (WAN)                       │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────▼──────────────┐
        │   UniFi Dream Machine    │
        │   192.168.10.1 (Mgmt)    │
        │   Gateway for all VLANs  │
        └───────────┬──────────────┘
                    │ Trunk (VLANs 10,20,30,40,50)
        ┌───────────▼──────────────┐
        │   UniFi Switch 24 PoE    │
        │   192.168.10.12 (Mgmt)   │
        └─┬────────┬────────┬──────┘
          │        │        │
    ┌─────▼───┐ ┌─▼─────┐ ┌▼──────────┐
    │Proxmox  │ │TrueNAS│ │ VPN Server│
    │.10.10   │ │.10.11 │ │ .20.10    │
    │VLAN 10  │ │VLAN 10│ │ VLAN 20   │
    └─────────┘ └───────┘ └───────────┘

    VMs on Proxmox (VLAN 30):
    ├─ Docker Host (.30.10)
    │  ├─ Nginx Proxy (.30.15)
    │  ├─ Monitoring (.30.20)
    │  ├─ Immich (.30.25)
    │  └─ Wiki.js (.30.30)
```

---

## IP Allocation Best Practices

### Allocation Strategy
- **.1-.9:** Network infrastructure (gateways, DNS, DHCP)
- **.10-.49:** Static server allocations
- **.50-.99:** Reserved for future static allocations
- **.100-.200:** DHCP pools for dynamic devices
- **.201-.254:** Reserved for expansion

### Naming Convention
- **Hostname format:** `[service]-[number].[vlan-name]`
- **Examples:**
  - proxmox-01.mgmt
  - immich.app
  - camera-front.protect

### Change Management
- All IP changes require:
  1. Update this document
  2. Update DNS records
  3. Update firewall rules
  4. Update monitoring targets
  5. Commit to Git repository

---

## Audit Trail

| Date | Change | Requested By | Approved By | Notes |
|------|--------|--------------|-------------|-------|
| 2024-12-16 | Initial allocation | Samuel Jackson | Samuel Jackson | Baseline configuration |
| | | | | |

---

## Related Documentation

- [Network Topology Diagram](./network-topology.md)
- [Firewall Rules](../../configs/networking/unifi-firewall-rules.json)
- [VLAN Configuration](../../configs/networking/vlan-config.md)
- [DNS Configuration](./dns-configuration.md)

---

**Last Updated:** 2024-12-16
**Owner:** Samuel Jackson
**Review Frequency:** Monthly
**Next Review:** January 2026
