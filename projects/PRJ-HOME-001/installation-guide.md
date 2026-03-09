# PRJ-HOME-001 Installation Guide

## Prerequisites
- UniFi Network Application 7.x or later (controller or UDM-Pro integrated).
- L2 switch with 802.1Q and LACP support.
- Two UniFi access points (U6-LR + U6-Lite) or equivalent coverage.
- ISP modem/ONT in bridge mode with provided WAN credentials.

## Hardware Setup
1. Rack and power the UDM-Pro, core PoE switch, and NVR/home-lab gear.
2. Connect ONT → UDM-Pro WAN; UDM-Pro LAN10G → PoE switch using two cables for LACP.
3. Patch APs and downstream devices into PoE switch; label ports by room.
4. Connect a laptop to a trusted access port (VLAN 20 untagged) for initial adoption.

## Controller Initialization
1. Run UniFi setup wizard; select **New Setup** and choose a local-only account for exportability.
2. Set **Site Name** to `HomeLab` (match the sanitized export).
3. Disable remote management/UPnP; enable automatic backups to local storage.
4. Import baseline configuration using `assets/unifi-controller-export-sanitized.json`.

## Switching Baseline
1. Create port profiles noted in `assets/vlan-firewall-dhcp-config.md`.
2. Apply **Core Uplink** profile on both UDM-Pro 10G ports; enable LACP on switch side.
3. Apply **Access - Trusted** on user ports; **Access - IoT AP** on AP ports.

## Access Point Adoption
1. From the controller, adopt APs; wait for firmware auto-upgrades to complete.
2. Map SSIDs to VLANs per the Wi‑Fi diagram; confirm band steering and minimum RSSI enforcement.
3. Perform site RF scan; adjust channel width to 20 MHz on 2.4 GHz and 80 MHz on 5 GHz.

## Validation
- Confirm controller shows all devices online with green health.
- Verify DHCP leases in each VLAN and confirm DNS resolution via allow-listed resolvers.
- Run a speed test from Guest SSID to ensure rate-limit policy is applied.
