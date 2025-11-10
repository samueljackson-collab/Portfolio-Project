# IP Addressing Scheme – PRJ-HOME-001

This document captures static assignments, DHCP scopes, and reservation strategy for the segmented homelab network. All networks use a **/24 subnet mask (255.255.255.0)** for simplicity and predictable host math.

## VLAN 1 – Management (192.168.1.0/24)

| IP Address | Hostname | Device Type | MAC Address | Purpose | Notes |
|------------|----------|-------------|-------------|---------|-------|
| 192.168.1.1 | udmp.mgmt | UniFi Dream Machine Pro | 74:83:C2:AA:00:01 | Router, firewall, controller | Default gateway for all VLANs. |
| 192.168.1.2 | usw24.mgmt | UniFi Switch 24 PoE | 74:83:C2:AA:00:02 | Core PoE switch | Hosts wired endpoints and AP uplinks. |
| 192.168.1.3 | usw8.mgmt | UniFi Switch 8 PoE | 74:83:C2:AA:00:03 | Remote switch | Serves office/lab bench. |
| 192.168.1.10 | ap1.mgmt | UniFi AP AC Pro – Living Room | 74:83:C2:AA:10:01 | Wi-Fi AP | Ceiling mount near living room. |
| 192.168.1.11 | ap2.mgmt | UniFi AP AC Pro – Bedroom | 74:83:C2:AA:10:02 | Wi-Fi AP | Ceiling mount near bedroom hall. |
| 192.168.1.12 | ap3.mgmt | UniFi AP AC Pro – Office | 74:83:C2:AA:10:03 | Wi-Fi AP | Ceiling mount in office. |
| 192.168.1.20 | pdu.mgmt | CyberPower 1500VA UPS | 9C:C9:EB:00:10:01 | Power monitoring | SNMP for runtime alerts. |
| 192.168.1.254 | reserved.mgmt | Reserved | — | Future management appliance | Hold for out-of-band controller. |

- **DHCP**: Disabled. All management hosts use statically assigned addresses.
- **DNS**: Forward/Reverse zones maintained in Pi-hole and UDMP controller for ease of management.

## VLAN 10 – Trusted (192.168.10.0/24)

| IP Address | Hostname | Device Type | Assignment Type | Purpose | Notes |
|------------|----------|-------------|-----------------|---------|-------|
| 192.168.10.1 | gateway.trusted | UDMP SVI | Static | Default gateway | Routes to all VLANs. |
| 192.168.10.2 | pihole.trusted | Raspberry Pi 4 | Static | Primary DNS & ad blocking | Also reachable on 192.168.1.21 for management. |
| 192.168.10.5 | truenas.trusted | TrueNAS Core | Static | NAS, NFS/SMB shares | 10 GbE uplink via DAC cable. |
| 192.168.10.10 | proxmox.trusted | Proxmox VE Host | Static | Virtualization platform | Hosts production VMs/containers. |
| 192.168.10.20 | desktop.trusted | Windows 11 Workstation | DHCP Reservation | Admin workstation | MAC 40:61:86:01:20:AA. |
| 192.168.10.21 | macbook.trusted | MacBook Pro | DHCP Reservation | Personal laptop | Travels; reservation ensures DNS stability. |
| 192.168.10.22 | thinkpad.trusted | ThinkPad X1 | DHCP Reservation | Work laptop | VPN to corporate network. |
| 192.168.10.30 | printer.trusted | HP LaserJet M404 | Static | Network printer | Embedded web console secured with HTTPS. |
| 192.168.10.40-99 | reserved.trusted | — | Reserved | Future servers/appliances | Keep contiguous block for infra. |
| 192.168.10.100-200 | dhcp.trusted | DHCP Pool | DHCP | User devices | 100 dynamic leases, 24-hour duration. |
| 192.168.10.201-250 | dhcp.static | Reserved | DHCP Reservation pool | For lab or staging systems requiring persistence. |

- **DNS**: Pi-hole (192.168.10.2) primary; Cloudflare 1.1.1.1 secondary via DHCP option 6.
- **NTP**: UDMP (192.168.1.1) distributed via DHCP option 42.

## VLAN 50 – IoT (192.168.50.0/24)

| IP Address | Hostname | Device Type | Assignment Type | Purpose | Notes |
|------------|----------|-------------|-----------------|---------|-------|
| 192.168.50.1 | gateway.iot | UDMP SVI | Static | VLAN gateway | NAT to internet only. |
| 192.168.50.10 | smarttv.iot | Samsung Smart TV | DHCP Reservation | Streaming | Requires LAN control from Home Assistant. |
| 192.168.50.11 | thermostat.iot | Ecobee Thermostat | DHCP Reservation | HVAC control | Integrates with Home Assistant via cloud API. |
| 192.168.50.12 | lock-front.iot | August Lock | DHCP Reservation | Front door lock | Requires mDNS for HomeKit. |
| 192.168.50.13 | lock-back.iot | August Lock | DHCP Reservation | Back door lock | Same ACLs as front door. |
| 192.168.50.20-29 | bulb-##.iot | Philips Hue Bulbs | DHCP | Smart lighting | 10 bulbs; controlled via Hue bridge. |
| 192.168.50.30 | camera-front.iot | Wyze Cam v3 | DHCP Reservation | Exterior surveillance | Cloud recording; no LAN access. |
| 192.168.50.31 | camera-back.iot | Wyze Cam v3 | DHCP Reservation | Backyard surveillance | — |
| 192.168.50.40 | huebridge.iot | Philips Hue Bridge | DHCP Reservation | Zigbee hub | Exposed only to trusted VLAN via firewall Rule 3. |
| 192.168.50.50-89 | sensors.iot | Misc Sensors | DHCP | Smart plugs, leak detectors | Typically <5 kbps each. |
| 192.168.50.90-99 | reserved.iot | — | Reserved | Future controllers | Keep block for high-value IoT gear. |
| 192.168.50.100-200 | dhcp.iot | DHCP Pool | DHCP | General IoT devices | 100 leases, 24-hour duration. |

- **DNS**: Cloudflare (1.1.1.1) issued via DHCP to reduce dependency on Pi-hole.
- **DHCP Options**: Option 60 (Vendor class) leveraged for select devices needing custom DNS.

## VLAN 99 – Guest (192.168.99.0/24)

| IP Address | Hostname | Device Type | Assignment Type | Purpose | Notes |
|------------|----------|-------------|-----------------|---------|-------|
| 192.168.99.1 | gateway.guest | UDMP SVI | Static | Captive portal gateway | NAT to internet with rate limiting. |
| 192.168.99.2 | portal.guest | UniFi Portal | Virtual | Landing page service | Hosted on UDMP. |
| 192.168.99.100-200 | dhcp.guest | DHCP Pool | DHCP | Guest devices | 100 leases, 4-hour duration. |

- **DNS**: Cloudflare (1.1.1.1) and Quad9 (9.9.9.9) handed out via DHCP.
- **Captive Portal**: Voucher-based authentication with per-device bandwidth limit (10 Mbps).

## VLAN 100 – Lab (192.168.100.0/24)

| IP Address | Hostname | Device Type | Assignment Type | Purpose | Notes |
|------------|----------|-------------|-----------------|---------|-------|
| 192.168.100.1 | gateway.lab | UDMP SVI | Static | Lab gateway | Rate limited to 50 Mbps per host. |
| 192.168.100.10 | kali.lab | Kali Linux VM | Static | Penetration testing | Hosted on Proxmox lab cluster. |
| 192.168.100.11 | metasploitable.lab | Metasploitable VM | Static | Vulnerability testing | Isolated except for trusted access. |
| 192.168.100.12 | ubuntu-test.lab | Ubuntu VM | DHCP Reservation | General testing | Auto rebuild nightly. |
| 192.168.100.13 | docker-host.lab | Ubuntu + Docker | DHCP Reservation | Container experiments | Uses VLAN 100 to protect production. |
| 192.168.100.20-39 | sandbox-##.lab | Various VMs | DHCP | Temporary workloads | Purged weekly. |
| 192.168.100.40-89 | reserved.lab | — | Reserved | Future lab infrastructure | Keep contiguous range for clusters. |
| 192.168.100.100-200 | dhcp.lab | DHCP Pool | DHCP | Standard lab devices | 100 leases, 1-hour duration. |

- **DNS**: Pi-hole (192.168.10.2) with conditional forwarders for lab-specific zones.
- **DHCP Options**: Custom option handing out internal domain `homelab.local`.

## Subnet Summary

| VLAN | Network | Gateway | Broadcast | Usable Host Range | Usable Hosts |
|------|---------|---------|-----------|-------------------|--------------|
| 1 | 192.168.1.0/24 | 192.168.1.1 | 192.168.1.255 | 192.168.1.1 – 192.168.1.254 | 254 |
| 10 | 192.168.10.0/24 | 192.168.10.1 | 192.168.10.255 | 192.168.10.1 – 192.168.10.254 | 254 |
| 50 | 192.168.50.0/24 | 192.168.50.1 | 192.168.50.255 | 192.168.50.1 – 192.168.50.254 | 254 |
| 99 | 192.168.99.0/24 | 192.168.99.1 | 192.168.99.255 | 192.168.99.1 – 192.168.99.254 | 254 |
| 100 | 192.168.100.0/24 | 192.168.100.1 | 192.168.100.255 | 192.168.100.1 – 192.168.100.254 | 254 |

```
IP Range Visualization (Not to scale)

VLAN 1   : 192.168.1.0 ──────────────────────────────────────────── 192.168.1.255
VLAN 10  : 192.168.10.0 ────────────────────────────────────────── 192.168.10.255
VLAN 50  : 192.168.50.0 ────────────────────────────────────────── 192.168.50.255
VLAN 99  : 192.168.99.0 ────────────────────────────────────────── 192.168.99.255
VLAN 100 : 192.168.100.0 ───────────────────────────────────────── 192.168.100.255
```

## DHCP Lease Policies
- Trusted & IoT: 24-hour lease time keeps address churn predictable without exhausting the pool.
- Guest: 4-hour lease aligns with 24-hour vouchers and prevents stale leases from blocking new visitors.
- Lab: 1-hour lease ensures compromised lab nodes lose access quickly when powered off.

## Adding New Reservations
1. Identify VLAN and confirm available address in its reserved range.
2. Create DHCP reservation in UniFi (Settings → Networks → [VLAN] → DHCP → Reservations) using device MAC.
3. Update this document and the configuration management repository with the new hostname/IP.
4. If the device needs management access, ensure firewall rules permit the required flows.

Keep this addressing plan synchronized with UniFi controller exports and infrastructure-as-code definitions to avoid configuration drift.
