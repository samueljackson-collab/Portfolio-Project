# VLAN, Firewall, and DHCP Configurations (Sanitized)

## VLAN Plan
- **VLAN 10 - Management**: 192.168.10.0/24, gateway 192.168.10.1, DHCP 192.168.10.100-199, tagged on uplinks only.
- **VLAN 20 - Trusted LAN**: 192.168.20.0/24, gateway 192.168.20.1, DHCP 192.168.20.50-199, untagged on user switch ports.
- **VLAN 30 - IoT**: 192.168.30.0/24, gateway 192.168.30.1, DHCP 192.168.30.50-199, tagged on AP ports for SSID `Home-IoT`.
- **VLAN 40 - Guest**: 192.168.40.0/24, gateway 192.168.40.1, DHCP 192.168.40.50-199, captive portal + rate limit.

## Firewall Rules
1. **Block IoT lateral movement**
   - Action: Drop
   - Source: VLAN 30 (IoT)
   - Destination: VLAN 20 (Trusted) and VLAN 40 (Guest)
   - Justification: Prevent untrusted devices from reaching trusted/guest zones.
2. **Allow Trusted to local LAN**
   - Action: Accept
   - Source: VLAN 20 (Trusted)
   - Destination: RFC1918 networks
   - Justification: Normal user access to services.
3. **DNS egress control**
   - Action: Accept
   - Source: Internal Networks (VLANs 10, 20, 30, 40)
   - Destination: DNS allow-list group (1.1.1.1, 9.9.9.9)
   - Protocol: UDP/53
   - Justification: Prevent rogue DNS tunneling.
4. **Guest isolation**
   - Action: Drop
   - Source: VLAN 40 (Guest)
   - Destination: RFC1918 networks except gateway
   - Justification: Guest clients must stay internet-only.

## DHCP Options
- **Option 6 (DNS)**: 1.1.1.1, 9.9.9.9 for all VLANs; fallback to gateway resolver.
- **Option 42 (NTP)**: 192.168.10.1 for management and trusted VLANs.
- **Reservation examples (hashed identifiers)**:
  - Trusted user laptop: MAC `AA:BB:CC:DD:EE:FF` → 192.168.20.60
  - Camera NVR: MAC `11:22:33:44:55:66` → 192.168.30.60

## Switch Port Profiles
- **Core Uplink**: Tagged VLANs 10/20/30/40; native VLAN 10; LACP enabled.
- **Access - Trusted**: Native VLAN 20, no tagging.
- **Access - IoT AP**: Tagged 20/30/40; native VLAN 10 for AP management.

> All identifiers are sanitized; adjust gateways and ranges before production rollout.
