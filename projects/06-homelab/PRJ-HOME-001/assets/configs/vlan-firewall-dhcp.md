# VLAN, Firewall, and DHCP Configuration

## VLAN Plan

| VLAN | Name | Subnet | Gateway | Purpose | Notes |
|------|------|--------|---------|---------|-------|
| 1 | Management | 192.168.1.0/24 | 192.168.1.1 | Network hardware management | DHCP disabled, static addressing only |
| 10 | Trusted | 192.168.10.0/24 | 192.168.10.1 | Workstations, NAS, hypervisor | Full access to lab VLAN on allowed ports |
| 50 | IoT | 192.168.50.0/24 | 192.168.50.1 | Smart home devices | Isolated; mDNS reflector for discovery |
| 99 | Guest | 192.168.99.0/24 | 192.168.99.1 | Visitors | Captive portal + rate limiting |
| 100 | Lab | 192.168.100.0/24 | 192.168.100.1 | Test benches and staging | Isolated from mgmt/guest/iot |

## DHCP Scopes

| VLAN | Range | DNS | Lease | Reservations |
|------|-------|-----|-------|--------------|
| 10 | 192.168.10.100-200 | 192.168.10.2 (Pi-hole) | 24h | truenas (10.5), proxmox (10.10), pihole (10.2) |
| 50 | 192.168.50.100-200 | 1.1.1.1 | 24h | smart-tv (50.10), thermostat (50.11) |
| 99 | 192.168.99.100-200 | 1.1.1.1 | 4h | none |
| 100 | 192.168.100.50-150 | 192.168.10.2 | 24h | lab-builder (100.10), k8s-node1 (100.20), k8s-node2 (100.21) |

**DHCP Options**
- Management VLAN has DHCP disabled to force static addressing and prevent rogue clients.
- mDNS reflector enabled for IoT VLAN to allow discovery from trusted VLAN only.
- Guest VLAN uses OpenDNS/Cloudflare to prevent DNS tunneling into trusted networks.

## Firewall Rule Summary (LAN IN)

| Order | Rule | Action | Source | Destination | Ports/Proto | Rationale |
|-------|------|--------|--------|-------------|-------------|-----------|
| 100 | Admin to Management | ALLOW | VLAN10 (admin group) | VLAN1 | TCP 22/443/8443 | Permit device management |
| 110 | Trusted to Lab (web) | ALLOW | VLAN10 | VLAN100 | TCP 8080/8443 | Allow app testing only |
| 120 | Trusted to IoT Control | ALLOW | VLAN10 | VLAN50 | UDP 5353, TCP 80/443 | Allow discovery + cloud control |
| 200 | Guest Isolation | DROP | VLAN99 | RFC1918 | ANY | Prevent guest lateral movement |
| 210 | IoT Isolation | DROP | VLAN50 | VLAN1/VLAN10/VLAN99/VLAN100 | ANY | Hard isolation for smart devices |
| 900 | Default Drop | DROP | ANY | ANY | ANY | Explicit deny and logging |

**WAN IN**
- Allow UDP/51820 to gateway for WireGuard.
- Drop all other unsolicited traffic with logging.

## Change Control

1. Document the requested change, owner, and rollback plan.
2. Export current UniFi config (see `../network-exports/unifi-controller-export-sanitized.json`).
3. Apply rule in staging (Lab VLAN) and validate with ping/iperf.
4. Promote to production window with maintenance notification.
5. Capture post-change validation and update runbooks.

## Validation Steps
- `ping` gateway and DNS from each VLAN.
- Confirm DHCP lease issuance from expected scopes.
- Run port scans from guest/IoT to verify drop rules.
- Validate WireGuard handshake from external client and confirm no lateral access.
