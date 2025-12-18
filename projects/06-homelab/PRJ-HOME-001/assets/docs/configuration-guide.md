# Homelab Network Configuration Guide

## Overview
How to configure UniFi controller, VLANs, DHCP scopes, firewall rules, and Wi-Fi SSIDs using the sanitized export as a baseline.

## Import Baseline
1. Download `network-exports/unifi-controller-export-sanitized.json`.
2. In UniFi Network Application > Settings > System > Backup, select **Restore from file**.
3. After restore, verify device adoption status and firmware versions.

## VLANs and Switching
- Apply profile `Trunk-All` to uplink ports (ports 23-24 on USW-24-PoE, port 8 on lab-switch).
- Assign access ports:
  - Ports 1-3 (USW-24-PoE): AP uplinks, native VLAN 1, tagged 10/50/99/100.
  - Ports 4-10: Trusted access (VLAN 10 untagged).
  - Ports 11-16: Lab access (VLAN 100 untagged).
  - Ports 17-18: IoT wired (VLAN 50 untagged).
  - Ports 19-20: Guest wired (VLAN 99 untagged) for conference rooms.

## DHCP & DNS
- DHCP options already set per `configs/vlan-firewall-dhcp.md`.
- Verify DNS override on Trusted VLAN points to Pi-hole (192.168.10.2).
- Enable DHCP guard on guest and IoT networks to block rogue DHCP.

## Wi-Fi
- SSIDs: Trusted-WiFi (VLAN10), IoT-WiFi (VLAN50), Guest-WiFi (VLAN99).
- Enable band steering and minimum RSSI of -75 dBm to reduce sticky clients.
- Fast roaming enabled on Trusted-WiFi; disabled on Guest/Iot to reduce roaming churn.
- Guest portal uses voucher auth with 8-hour expiry; set rate limit 10/2 Mbps.

## Firewall
- Validate LAN_IN rules align with `configs/vlan-firewall-dhcp.md` table.
- Create IPv6 drop rule set (IPv6 disabled in export) to prevent unsolicited inbound.
- Apply IDS/IPS balanced profile on WAN_IN with GeoIP blocklist for RU/CN/KP/IR/SY.

## Monitoring and Alerts
- Enable email alerts for device disconnect, high latency, and WAN failover events.
- Create log forwarding to syslog server `192.168.10.5` for archival.
- Add health dashboard widget for per-SSID client count and channel utilization.

## Backup & Recovery
- Schedule daily encrypted backup at 03:00 UTC with 7-day retention.
- Store backups to `s3://homelab-unifi-backup` via rclone (access key stored on controller, not in repo).
- Test restore quarterly using lab-switch + AP to validate process.
