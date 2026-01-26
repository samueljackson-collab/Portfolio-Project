# PRJ-HOME-001 Verification Checklist

## Core
- [ ] UDM-Pro firmware up to date; WAN online with expected public IP.
- [ ] Controller backups enabled and last backup timestamp `<24h`.

## Switching
- [ ] LACP on 10G uplinks shows `active` on both ends.
- [ ] Port profiles applied: uplinks (Core), user desks (Trusted), APs (IoT AP), cameras (IoT).

## VLAN/DHCP
- [ ] DHCP leases issued in VLANs 10/20/30/40 with correct gateway/DNS options.
- [ ] Static reservations for NVR and management laptop applied.

## Firewall/Policy
- [ ] IoT → Trusted/Guest traffic blocked; confirm via test pings and rule logs.
- [ ] DNS egress allowed only to 1.1.1.1 and 9.9.9.9.
- [ ] Guest VLAN cannot reach RFC1918 networks.

## Wireless
- [ ] SSIDs mapped to correct VLANs; captive portal active on Guest.
- [ ] Minimum RSSI and band steering enforced on Trusted/IoT.
- [ ] Roaming test passes between APs without disconnects.

## Monitoring
- [ ] Syslog stream received at 192.168.10.50.
- [ ] Alerts configured for AP disconnect, WAN down, and PoE budget exceeded.

## Final Sign-off
- [ ] Speed test from Guest shows rate limiting (≈10/2 Mbps).
- [ ] Latency <10 ms between Trusted client and gateway during normal load.
- [ ] All diagrams and configs stored under `assets/` and linked in README.
