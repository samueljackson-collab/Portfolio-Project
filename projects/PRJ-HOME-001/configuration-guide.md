# PRJ-HOME-001 Configuration Guide

## Controller Settings
- **Backups**: Daily encrypted backups retained for 30 days; offload to NAS weekly.
- **Management Access**: Restrict UI to VLAN 10 source IPs; enforce MFA on controller accounts.
- **IDS/IPS**: Enable with balanced profile; exclude trusted home-lab ranges if noisy.

## Network Definitions
- Create VLAN networks 10/20/30/40 matching subnets in `assets/vlan-firewall-dhcp-config.md`.
- Set DHCP scopes with lease time 12 hours; reserve static leases for critical devices.
- DNS: Forward to 1.1.1.1 and 9.9.9.9; enable threat intelligence filtering if licensed.

## Wireless Networks
- **Home-Trusted** → VLAN 20, WPA2-PSK, minimum RSSI -70 dBm, band steering on.
- **Home-IoT** → VLAN 30, WPA2-PSK, client isolation enabled, multicast enhancement on.
- **Home-Guest** → VLAN 40, WPA2-PSK + captive portal, rate limit 10/2 Mbps.
- Disable legacy data rates below 12 Mbps to reduce airtime hogging.

## Firewall Policies
1. Deny IoT to Trusted and Guest (see rule set in `assets/unifi-controller-export-sanitized.json`).
2. Allow Trusted to RFC1918 networks; log accepts to SIEM/webhook.
3. Allow DNS to allow-listed resolvers only; drop all other outbound UDP/53.
4. Create LAN-in allow rules for management to gateway/APs.

## Switch and Port Profiles
- **Core Uplink**: Tagged 10/20/30/40, native 10; LACP active/active.
- **Access - Trusted**: Native 20; storm control enabled.
- **Access - IoT AP**: Tagged 20/30/40 with native 10; LLDP/LLDP-MED on.
- **Camera NVR**: Native 30; PoE+ budget reserved; restrict to TCP/8554 RTSP inbound.

## Monitoring and Logging
- Enable syslog export to 192.168.10.50 (home-lab rsyslog) for firewall, WLAN, and IDS.
- Configure alerts for AP disconnect, WAN down, PoE budget exceeded.
- Use WiFiman or similar app for roaming tests and RF scans after channel changes.
