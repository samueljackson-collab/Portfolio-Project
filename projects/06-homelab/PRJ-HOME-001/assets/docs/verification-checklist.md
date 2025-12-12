# Homelab Network Verification Checklist

## Physical
- [ ] All rack devices powered via UPS and labeled (RU + hostname).
- [ ] Patch panel to switch mappings match physical-topology.mermaid.
- [ ] APs secured with PoE power and correct port assignments (1-3 on USW-24-PoE).

## Configuration
- [ ] `unifi-controller-export-sanitized.json` imported and devices adopted.
- [ ] VLANs 1/10/50/99/100 present with correct gateways and DHCP scopes.
- [ ] DHCP guard enabled on guest and IoT networks.
- [ ] IDS/IPS balanced profile enabled on WAN with GeoIP blocks.
- [ ] Backup schedule set to daily 03:00 UTC with offsite target configured.

## Wi-Fi
- [ ] SSIDs Trusted-WiFi, IoT-WiFi, Guest-WiFi broadcasting on all APs.
- [ ] Minimum RSSI -75 dBm and band steering enabled on Trusted-WiFi.
- [ ] Guest portal active with voucher auth and 10/2 Mbps rate limit.

## Security
- [ ] Firewall LAN_IN rules match `configs/vlan-firewall-dhcp.md` ordering.
- [ ] WAN_IN allows only UDP/51820 for WireGuard; all else dropped/logged.
- [ ] Management VLAN has DHCP disabled and strong local admin password set.
- [ ] Syslog export configured to 192.168.10.5.

## Validation Tests
- [ ] Ping gateway and DNS from each VLAN.
- [ ] Obtain DHCP lease from each scope; verify DNS option matches plan.
- [ ] Guest client blocked from RFC1918 networks; IoT client blocked from mgmt.
- [ ] WireGuard client connects and reaches Trusted VLAN only.
- [ ] Throughput test meets ISP contract on WAN1; failover triggers on WAN1 unplug.

## Documentation
- [ ] Photos uploaded/sanitized per `assets/photos/README.md`.
- [ ] Diagrams updated (physical, logical, Wi-Fi) and referenced in project README.
- [ ] Runbooks and troubleshooting guide refreshed with any changes.
