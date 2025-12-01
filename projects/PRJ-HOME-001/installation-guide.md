# Installation Guide

This guide covers stand-up of the homelab network stack from bare metal through controller adoption.

## Prerequisites
- Hardware: pfSense-capable firewall with at least 6 NICs, UniFi PoE switch, two UniFi APs, Proxmox/TrueNAS hosts.
- Software: pfSense 2.6+ ISO, UniFi Network Application 7.5+ (self-hosted or CloudKey), SSH access to devices, TFTP/DHCP server for imaging if needed.
- Cabling: Labeled Cat6 for uplinks and AP drops; rack power with surge protection/UPS.

## Steps
1. **Rack and power**
   - Mount firewall, switch, and servers. Connect UPS-backed power.
   - Label ports and patch cables to match the physical diagram.
2. **Install pfSense**
   - Write the pfSense ISO to USB, boot firewall, and install to SSD.
   - Assign WAN/LAN temporarily; enable SSH and web GUI with a strong admin credential.
3. **Baseline pfSense setup**
   - Update to latest release; install Suricata package (do not enable yet).
   - Create VLAN interfaces for Trusted, IoT, Guest, Servers, and DMZ.
4. **Install UniFi Network Application**
   - Deploy controller on a management host or container; set hostname `unifi.lab.local`.
   - Generate a local admin account; disable remote cloud access until verification.
5. **Adopt switch and APs**
   - Factory-reset devices, place them on the Trusted VLAN (untagged) for adoption.
   - Using SSH or discovery, set `set-inform http://unifi.lab.local:8080/inform`.
6. **Time/DNS/NTP alignment**
   - Point all devices to pfSense for DNS (with DNSSEC) and NTP; confirm clocks align.
7. **Backup safety**
   - Export initial pfSense config and UniFi backup; store securely before major changes.

## Notes
- Keep WAN disconnected until firewall rules are in place; use offline package repos if required.
- For Protectli/low-noise builds, validate thermals before loading Suricata or VPN.

