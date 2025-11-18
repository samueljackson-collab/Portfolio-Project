# Troubleshooting & Maintenance Guide

## How to Use This Guide
- Start with the symptom, follow the diagnostic steps sequentially, apply resolution, and validate with post-checks.
- Capture logs/metrics before and after changes; document in Git with timestamp and outcome.

## Common Symptoms and Resolutions

### 1) No Internet for All Devices
**Diagnosis**
1. Check UDMP WAN status in controller (should show public IP, uptime). If down, verify modem LEDs and coax.
2. Run `ping 8.8.8.8` from UDMP tools; if fails, ISP outage likely.
3. Confirm WAN interface DHCP lease; renew if expired.
4. Check IDS/IPS events for blocks or DDoS mitigation triggering.
5. Validate threat management not blocking due to geo-filter.
**Resolution**
- Power-cycle modem (wait 30s) then UDMP; ensure modem in bridge mode.
- If DHCP lease stuck, release/renew via controller.
- Temporarily disable Geo-IP block if legitimate region required.
**Post-Check**
- `ping 1.1.1.1` succeeds; `ping google.com` resolves; controller WAN latency <20ms typical.

### 2) Single Device Cannot Access Network
**Diagnosis**
1. Verify switch port status (PoE, speed) and VLAN profile from controller.
2. Check device NIC settings (DHCP vs static); confirm IP in correct subnet.
3. Review DHCP leases on UDMP; ensure address issued.
4. Check for MAC address blocking or port security violations.
**Resolution**
- Re-provision port to correct profile; bounce port.
- Renew DHCP on device or set static within reserved range.
- Remove MAC block; verify no duplicate IP.
**Post-Check**
- Device receives correct IP/gateway/DNS; `ping gateway` <2ms; reaches internet.

### 3) WiFi Coverage Weak or Dropping
**Diagnosis**
1. Check RSSI in UniFi client list; values worse than -70 dBm indicate coverage issue.
2. Inspect AP channel utilization; ensure non-overlapping 1/6/11 and 36/149 reuse plan.
3. Verify AP transmit power and PoE state; check switch PoE budget.
4. Check for DFS events causing channel change.
**Resolution**
- Increase transmit power one step on affected AP; or reposition AP for line-of-sight.
- Add additional AP on port 16 if persistent weak area; adopt and apply AP-Trunk profile.
- Reduce channel width to 40MHz if high interference.
**Post-Check**
- RSSI improved >-65 dBm; retry rate <5%; roaming events successful without drops.

### 4) Camera Offline
**Diagnosis**
1. Verify PoE draw on switch port (should be 3-6W). If 0W, check cable/port disable.
2. Confirm link speed (100M expected) and VLAN 50 assignment.
3. Ping camera IP (192.168.50.110-113) from UDMP; if unreachable, check DHCP reservation.
4. Review Protect/NVR logs for disconnections.
**Resolution**
- Reseat cable; replace with tested outdoor Cat5e if damaged.
- Power-cycle port; ensure Camera-Access profile applied.
- If IP conflict, reserve correct IP via DHCP mapping; reboot camera.
**Post-Check**
- Camera streams in Protect; RTSP test to NVR succeeds; switch port shows active PoE and link.

### 5) IoT Device Not Discoverable
**Diagnosis**
1. Ensure IoT SSID connectivity and correct VLAN 20 IP.
2. Verify mDNS rule from Trusted to IoT (port 5353) present and not shadowed.
3. Confirm controller shows IoT device online; check DHCP lease.
4. Inspect firewall logs for RFC1918 blocks from IoT to other VLANs.
**Resolution**
- Restart IoT device; clear cached WiFi profile.
- Toggle mDNS service on Home Assistant; ensure Zigbee hub reachable on port 8099.
- If multicast suppressed, disable Proxy ARP temporarily for testing.
**Post-Check**
- Discovery works from Trusted device; control via Home Assistant succeeds; no firewall denies seen.

### 6) Guest Network Complaints (Slow/Blocked)
**Diagnosis**
1. Check bandwidth limit (25/10 Mbps) and current utilization per client.
2. Review DPI/content filter blocks; ensure not over-blocking.
3. Verify client isolation enabled (prevents LAN access by design).
4. Ensure WAN not saturated by other VLANs (controller traffic stats).
**Resolution**
- Temporarily raise guest limit to 50/20 for testing.
- Adjust DPI to allow necessary categories; keep P2P/Adult blocked.
- If WAN saturated, enforce per-VLAN QoS or schedule heavy downloads.
**Post-Check**
- Guest clients sustain expected throughput; still isolated from LAN; content filtering adequate.

### 7) DHCP Issues (No or Wrong IP)
**Diagnosis**
1. Check UDMP DHCP status for target VLAN; scope exhaustion? (Trusted uses .100-.249 etc.).
2. Validate switch port VLAN and native tagging.
3. Inspect logs for DHCP guard or rogue DHCP detection.
4. Confirm device MAC not in blocklist; verify lease time 86400s.
**Resolution**
- Expand scope if >80% utilized; add reservations for critical devices.
- Correct port profile; bounce port.
- Clear stale DHCP entries; reboot device.
**Post-Check**
- Device receives correct IP/gateway/DNS; lease recorded on UDMP; internet accessible.

### 8) High Latency or Packet Loss
**Diagnosis**
1. Run continuous ping from UDMP to ISP gateway and to internal gateway IPs; compare loss/latency.
2. Check switch errors (CRC, drops) on affected ports; inspect cabling for damage.
3. Validate WiFi utilization; high channel utilization >70% may cause latency.
4. Review IDS/IPS for potential packet drops or rate limiting.
**Resolution**
- Replace damaged cables; ensure Cat6 for gigabit runs.
- Move devices to wired where possible; reduce 80MHz to 40MHz during congestion.
- If IDS causing drops, switch LAN IDS to alert-only (already default) and retest.
**Post-Check**
- Latency <5ms LAN, <25ms WAN; 0% packet loss over 5-minute test; switch counters clean.

## Preventive Maintenance
- **Backups**: Verify nightly UDMP config backup to TrueNAS; test restore quarterly.
- **Firmware**: Monthly check for UDMP/USW/AP updates; schedule maintenance window; document versions.
- **Log Review**: Weekly review of firewall/IDS logs; monthly DPI/category tuning.
- **PoE Budget**: Review after adding devices; keep utilization <80%.
- **Port Audit**: Quarterly port profile validation vs documentation.

## Disaster Recovery Quick Steps
1. **Gateway Failure**: Deploy spare UDMP/UXG, restore latest backup, verify WAN/DHCP/firewall.
2. **Switch Failure**: Connect critical devices to spare PoE switch; trunk to UDMP; reapply port profiles.
3. **AP Failure**: Replace with spare AP, adopt in controller, assign SSID set.
4. **WAN Outage**: Use LTE/5G modem on UDMP WAN2/SFP+; update DNS if public services used.

## Validation Checklists
- **Post-Change**: Verify connectivity per VLAN (gateway ping, DNS, internet), inter-VLAN rules (allowed services), and monitoring alerts.
- **Security**: Confirm IDS/IPS running, WAN inbound deny in effect, RFC1918 blocks for Guest/IoT active.
- **Wireless**: Confirm all SSIDs broadcasting, channel plan intact (1/6/11 + 36/149), client counts normal.
