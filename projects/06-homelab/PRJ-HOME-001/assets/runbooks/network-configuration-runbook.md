# Network Configuration Runbook (PRJ-HOME-001)

## Goal
Configure VLANs, DHCP, firewall rules, and UniFi WLAN mappings to match the secure homelab design.

## VLAN + Subnet Setup (pfSense)
1. Create VLANs on the LAN interface:
   - VLAN 10 (Trusted) → 192.168.10.0/24
   - VLAN 20 (IoT) → 192.168.20.0/24
   - VLAN 30 (Guest) → 192.168.30.0/24
   - VLAN 40 (Servers) → 192.168.40.0/24
   - VLAN 50 (DMZ) → 192.168.50.0/24
2. Assign interfaces and enable DHCP scopes per VLAN.
3. Set DNS resolver with DNSSEC and conditional forwarding as needed.

## Firewall Policy
1. Apply **default deny** on all VLAN interfaces.
2. Add allow rules per VLAN based on the table:
   - Refer to `assets/configs/firewall-rules-table.md`.
3. Add NAT rules for public DMZ services.
4. Verify logging enabled for deny rules.

## UniFi Switch Profiles
1. Create port profiles:
   - Trunk (all VLANs tagged, native VLAN 10)
   - Access profiles for VLAN 20, 30, 40, 50
2. Apply trunk to uplinks and AP ports.
3. Apply access profiles to wired endpoints.

## UniFi WLAN Mapping
1. Create SSIDs:
   - Homelab-Secure → VLAN 10
   - Homelab-IoT → VLAN 20
   - Homelab-Guest → VLAN 30
2. Enable client isolation on IoT + Guest SSIDs.
3. Enable WPA3 Enterprise for trusted SSID.

## Validation Steps
- [ ] VLAN gateways reachable from trusted client
- [ ] IoT cannot access RFC1918 networks
- [ ] Guest has internet only
- [ ] Servers reachable from trusted VLAN
- [ ] DMZ reachable from WAN on HTTPS only

## References
- `assets/diagrams/logical-network-vlans-firewall.mermaid`
- `assets/unifi/unifi-controller-export-redacted.json`
