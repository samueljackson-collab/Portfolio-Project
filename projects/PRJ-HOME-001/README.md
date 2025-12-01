# PRJ-HOME-001: Homelab & Secure Network Build

A secure, VLAN-segmented homelab network built with pfSense and UniFi. This snapshot includes sanitized controller exports, VLAN/firewall/DHCP definitions, visual documentation, and operational runbooks so the build can be reproduced without exposing private data.

## Contents
- `assets/configs/`
  - `unifi-controller-export.json` — Sanitized UniFi Network export with SSIDs, VLAN assignments, RADIUS/WPA3 posture, and device adoption mappings removed of identifiers.
  - `vlan-firewall-dhcp-config.md` — Human-readable VLAN table, firewall policy map, and DHCP scopes with placeholder host IDs and MACs.
- `assets/diagrams/`
  - `physical-topology.mmd` — Rack-level layout showing pfSense, UniFi switch, APs, and server uplinks.
  - `logical-network.mmd` — Security-zone diagram connecting VLANs to services and enforcement points.
  - `wifi-layout.md` — Wi‑Fi coverage/SSID layout with 2.4/5 GHz channel plans.
- `assets/photos/`
  - Sanitized photo notes and filenames for rack/cable/AP placement.
- Guides at the project root: installation, configuration, troubleshooting, lessons learned, and a verification checklist.

## How to Use
1. Review the diagrams to understand the intended physical and logical flow.
2. Import the sanitized UniFi export into a lab controller (avoid production) and map placeholder MACs/IPs to your hardware.
3. Apply VLAN, firewall, and DHCP definitions from `vlan-firewall-dhcp-config.md` to pfSense (or your firewall of choice), adjusting interface names and upstream details.
4. Follow `installation-guide.md` then `configuration-guide.md` to rebuild the environment end-to-end.
5. Validate with `verification-checklist.md` and keep `troubleshooting-guide.md` handy for common failure modes.

## Related Projects
- Original homelab planning and prior evidence live under [`projects/06-homelab/PRJ-HOME-001`](../06-homelab/PRJ-HOME-001/).

