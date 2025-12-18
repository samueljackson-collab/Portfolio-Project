# VLAN, Firewall, and DHCP Configuration

Sanitized configuration values for rebuilding the homelab network. Replace placeholder MAC addresses and hostnames with your own.

## VLANs & Subnets

| VLAN | Name    | Subnet           | Gateway       | Purpose  |
| ---- | ------- | ---------------- | ------------- | -------- |
| 10   | Trusted | 192.168.1.0/24   | 192.168.1.1   | Admin + trusted clients |
| 20   | IoT     | 192.168.20.0/24  | 192.168.20.1  | Segmented IoT devices |
| 30   | Guest   | 192.168.30.0/24  | 192.168.30.1  | Captive portal guest access |
| 40   | Servers | 192.168.40.0/24  | 192.168.40.1  | Hypervisors, storage, services |
| 50   | DMZ     | 192.168.50.0/24  | 192.168.50.1  | Public-facing services |

## DHCP Scopes

| VLAN | Pool Range                | Reservation Examples                | DNS/NTP              |
| ---- | ------------------------- | ----------------------------------- | -------------------- |
| 10   | 192.168.1.50 – 192.168.1.200   | `00:00:00:00:AA:10` → 192.168.1.10 (RADIUS) | DNS: 192.168.1.1; NTP: 192.168.1.1 |
| 20   | 192.168.20.50 – 192.168.20.200 | `00:00:00:00:BB:20` → 192.168.20.10 (IoT hub) | DNS: 192.168.1.1; NTP: 192.168.1.1 |
| 30   | 192.168.30.50 – 192.168.30.200 | None (guest) | DNS: 192.168.1.1; NTP: 192.168.1.1 |
| 40   | 192.168.40.50 – 192.168.40.200 | `00:00:00:00:CC:40` → 192.168.40.10 (Proxmox) | DNS: 192.168.1.1; NTP: 192.168.1.1 |
| 50   | 192.168.50.50 – 192.168.50.150 | `00:00:00:00:DD:50` → 192.168.50.10 (Reverse proxy) | DNS: 192.168.1.1; NTP: 192.168.1.1 |

## Firewall Policy (pfSense)

- **Default posture:** Block inter-VLAN traffic unless explicitly allowed; allow established/related.
- **Trusted → Servers:** Allow HTTPS/SSH/Proxmox UI to `SERVERS_NET` alias; allow NFS/iSCSI to storage hosts.
- **Trusted → WAN:** Allow all outbound with DNS to local resolver only.
- **IoT → Servers/Trusted:** Block except allow MQTT to `iot-broker` (192.168.20.10) and HTTPS to `media-gateway` (192.168.40.20).
- **Guest → Internal:** Block; allow DNS to pfSense and HTTPS to captive portal host; allow WAN HTTP/HTTPS only.
- **Servers → Internet:** Allow package updates (80/443) and NTP; block outbound SMTP except via relay alias.
- **DMZ → Internal:** Block; allow reverse proxy health checks to `SERVERS_NET` over HTTPS via pinned alias.
- **VPN (OpenVPN) → Trusted/Servers:** Allow administrative subnets 10.8.0.0/24 to TRUST+SERVERS aliases; block lateral to IoT/Guest.

## Services & Overrides

- **DNS Overrides:**
  - `unifi.lab.local` → 192.168.1.15 (controller)
  - `proxmox.lab.local` → 192.168.40.10
  - `truenas.lab.local` → 192.168.40.11
- **NTP:** pfSense advertises itself; upstream `pool.ntp.org`.
- **Captive Portal:** Hosted at `https://guest-portal.example.local` pinned to 192.168.30.2.

