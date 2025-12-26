# PRJ-HOME-001 Troubleshooting Guide

## WAN/Connectivity
- Verify ONT → UDM-Pro link status (10G) and PPPoE/DHCP lease in controller.
- Run `ping 1.1.1.1` from controller diagnostics; if failed, check ISP modem bridge mode.
- If dual LACP uplink flaps, disable one link to isolate cabling issues.

## Adoption and Provisioning
- AP stuck in adopting: factory-reset (press 10 seconds), ensure DHCP on VLAN 10 provides IP, then re-adopt.
- Switch not adopting: confirm controller discovery is allowed on management VLAN and SSH is enabled during onboarding.
- Firmware failures: switch controller to manual upgrade and upload stable firmware from UniFi downloads.

## DHCP/Addressing
- Clients pulling APIPA: confirm DHCP range not exhausted; validate helper is enabled on VLAN 30/40.
- Wrong subnet: check port profile tagging; ensure native VLAN matches design (e.g., 20 for trusted access).

## Wireless Issues
- Poor roaming: raise minimum RSSI to -70 dBm and ensure 2.4 GHz channels are non-overlapping (1/6/11).
- IoT devices failing to connect: temporarily disable band steering; ensure multicast enhancement is enabled.
- Guest portal errors: restart UniFi portal service and verify captive portal VLAN 40 is mapped to SSID.

## Firewall/Policy
- Cannot reach LAN from Trusted: ensure rule order keeps allow above default drop; check logging for rule hits.
- IoT unexpectedly reaching LAN: confirm group `LAN_IOT` is bound to drop rules and no manual overrides exist.

## Performance
- High CPU on gateway: disable IDS temporarily to confirm; if resolved, tune signatures or upgrade hardware.
- Latency during backups: move UniFi backups to off-peak hours; verify PoE budget is not maxed causing throttling.

## Data Recovery and Exports
- Use local controller backup from previous day; restore on staging instance before production.
- Export sanitized config via Settings → System → Export Site; scrub WAN credentials before sharing.
