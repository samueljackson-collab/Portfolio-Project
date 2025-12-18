# Homelab Network Troubleshooting Guide

## Quick Triage
1. Check controller alerts (device offline, DHCP failures, high latency).
2. Validate physical layer: link LEDs, PoE status, cable seating.
3. Confirm client VLAN/SSID assignment in UniFi client view.
4. Run `ping` to gateway and DNS; follow with `traceroute` if needed.

## Common Issues

### Cannot Adopt Device
- Ensure device is factory-reset and on management VLAN (untagged 1).
- Check DHCP on management network is **disabled**; set static IP in 192.168.1.0/24.
- SSH into device and run `set-inform http://192.168.1.1:8080/inform`.

### No Internet on Guest/IoT
- Verify VLAN tagging on switch port; guest should be untagged 99, IoT untagged 50.
- Check firewall rules for Guest Isolation/IoT Isolation (see `configs/vlan-firewall-dhcp.md`).
- Confirm WAN link state and failover status on gateway dashboard.

### DHCP Failures
- Inspect DHCP leases under each network; check pool exhaustion.
- Confirm DHCP guard is not blocking trusted DHCP server (should only run on guest/IoT).
- Review reservations in `network-exports/unifi-controller-export-sanitized.json` for typos.

### Slow Wi-Fi / Sticky Clients
- Review `diagrams/wifi-topology.mermaid` for channel layout; run RF scan to avoid DFS overlap.
- Increase minimum RSSI to -70 dBm for affected SSID.
- Rebalance AP power (set to medium) and verify band steering is on.

### WireGuard VPN Down
- Confirm UDP/51820 rule still present in WAN_IN.
- Check peer key/endpoint on client; rotate keys if compromised.
- Run `wg show` on gateway and verify handshake within last 120 seconds.

## Escalation and Logging
- Enable debug logs on gateway: **Settings > System > Advanced > Debug Terminal**.
- Export tech support file after reproducing issue; store in `/tmp/unifi-tsf.zip`.
- If issue persists, restore last known-good backup and reapply delta changes from configuration guide.
