# Installation Guide (PRJ-HOME-001)

## Scope
This guide covers initial hardware installation, cabling, and base software setup for the homelab network stack.

## Prerequisites
- ISP modem in bridge mode
- Rack-mounted UPS with dedicated 15A circuit
- pfSense appliance or firewall hardware
- UniFi switch + access points
- Laptop with Ethernet port and console access

## Hardware Install
1. **Mount the rack gear**
   - Install UPS at bottom of rack for stability.
   - Mount firewall, switch, and servers in that order.
2. **Cable power**
   - Connect all rack gear to UPS.
   - Label power cords (UPS-1, UPS-2, etc.).
3. **Patch panel + cabling**
   - Terminate Cat6a runs into patch panel.
   - Patch panel → switch ports using 0.5m Cat6a.
4. **WAN connection**
   - Modem → firewall WAN port (Cat6a).
5. **LAN trunk**
   - Firewall LAN → switch trunk (Cat6a).
6. **PoE devices**
   - Connect APs to PoE switch ports.

## Base Software Setup
1. Install pfSense (2.6+)
2. Set LAN IP to 192.168.10.1/24 temporarily
3. Enable DHCP scope for trusted VLAN (temporary)
4. Install UniFi Network Application (7.5+)
5. Adopt switches/APs and update firmware

## Validation Checklist
- [ ] Internet reachable from trusted VLAN
- [ ] Switch and APs adopted
- [ ] PoE power stable to APs
- [ ] UPS monitoring enabled

## References
- See `assets/diagrams/physical-topology-rack-layout.mermaid` for physical cabling.
- See `assets/runbooks/network-configuration-runbook.md` for VLAN, DHCP, and firewall configuration steps.
