# Configuration Guide

Use this guide to apply VLANs, firewall policy, DHCP scopes, and wireless profiles after installation.

## pfSense
1. **Interfaces & VLANs**
   - Create VLANs on the LAN parent: VLAN 10 (Trusted), 20 (IoT), 30 (Guest), 40 (Servers), 50 (DMZ).
   - Assign interfaces as `TRUST`, `IOT`, `GUEST`, `SERVERS`, `DMZ` with /24 networks from the config file.
2. **DHCP**
   - Enable DHCP per interface using `assets/configs/vlan-firewall-dhcp-config.md` ranges.
   - Reserve static mappings for infrastructure MACs using placeholder entries as a template.
3. **DNS & NTP**
   - Enable Unbound in resolver mode with DNSSEC and ACLs allowing each VLAN.
   - Point NTP to upstream pool and advertise via DHCP.
4. **Firewall policy**
   - Apply inter-VLAN rules from the policy table; default deny across VLANs.
   - Enable anti-lockout rule on TRUST only; add bogon/anti-spoof on all VLANs.
5. **IPS/VPN**
   - Configure Suricata inline on WAN and DMZ with ET ruleset, blocking mode, and syslog forwarding.
   - Configure OpenVPN for remote admin to TRUST + SERVERS with certificate auth and MFA.

## UniFi Network
1. **Import backup**
   - Restore `assets/configs/unifi-controller-export.json` to a lab controller; update org/site names.
2. **Networks**
   - Confirm VLAN IDs and subnets match pfSense; set DHCP mode to none (firewall-owned) except management.
3. **Wireless**
   - Three SSIDs: `Homelab-Secure` (WPA3-Enterprise, VLAN 10), `Homelab-IoT` (WPA2-PSK, VLAN 20, client isolation), `Homelab-Guest` (open + captive portal, VLAN 30).
   - Apply band steering, 20 MHz on 2.4 GHz and 80 MHz on 5 GHz; manual channels per `wifi-layout.md`.
4. **Switching**
   - Create port profiles: `TRUSTED-TRUNK` (all VLANs tagged), `AP-TRUNK` (VLAN 10 native + 20/30 tagged), `SERVER-TRUNK` (VLAN 40 native + 10/20/30/50 tagged), `WAN` (untagged to ISP).
   - Tag uplinks to pfSense with TRUST native and VLANs 20/30/40/50 tagged.
5. **RADIUS/802.1X**
   - Point to pfSense FreeRADIUS or external server; update shared secrets and user groups.
6. **Management hardening**
   - Disable cloud access, require MFA, restrict controller UI to TRUST and VPN subnets.

## Validation
- Ping gateways per VLAN, validate DHCP leases, and run captive portal auth for Guest.
- Confirm APs show expected channel assignments and transmit powers per `wifi-layout.md`.

