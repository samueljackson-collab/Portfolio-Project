# Homelab Network Installation Guide

## Purpose
Reference steps to deploy the physical network stack (rack, switching, access points, and controller) from scratch.

## Prerequisites
- Printed copies of physical-topology.mermaid and cable map
- Labeled patch cables by VLAN color (Mgmt: blue, Trusted: green, IoT: purple, Guest: yellow, Lab: orange)
- UniFi Dream Machine Pro with latest firmware downloaded
- PoE budget calculation for APs and cameras

## Steps
1. **Rack and Power**
   - Mount patch panel (top), UDM Pro (middle), USW-24-PoE (below), and UPS (bottom).
   - Connect UPS to dedicated 20A circuit; plug gateway and switch into UPS battery outlets.
2. **Controller Bring-up**
   - Factory reset UDM Pro; adopt via `https://setup.ui.com` using local account only.
   - Import sanitized baseline: `assets/network-exports/unifi-controller-export-sanitized.json`.
   - Confirm site name is `homelab` and disable remote cloud access.
3. **Switching and VLAN Trunks**
   - Connect UDM Pro LAN port to USW-24-PoE port 24 (trunk all VLANs tagged, management untagged).
   - Patch lab-switch uplink to USW-24-PoE port 23 (trunk all VLANs tagged, management untagged).
4. **Access Points**
   - Mount APs at pre-marked locations; connect to USW-24-PoE ports 1-3 (PoE on, VLAN management untagged).
   - Validate LED state (adopted + broadcast) and run RF scan to confirm channel plan.
5. **WAN Connectivity**
   - Connect primary ISP to WAN1; optional LTE/backup to WAN2.
   - Verify IP assignment via controller and run throughput test.
6. **Labeling and Documentation**
   - Apply printed labels to rack units and patch cords.
   - Capture photos for `assets/photos` and update port map in configuration guide.

## Post-Install Validation
- Ping between VLAN gateways from trusted workstation.
- Confirm DHCP leases from each scope (10, 50, 99, 100).
- Connect guest device and verify internet-only access.
- Run speed test from IoT SSID to validate rate limits.
