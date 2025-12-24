# Homelab Network Troubleshooting Playbook

**Applies To:** pfSense firewall (WAN + VLAN gateways), UniFi switch (24 PoE), UniFi U6 Pro APs (3 SSIDs mapped to Trusted/IoT/Guest), Suricata IPS, OpenVPN, and the 5-VLAN design (Trusted 10, IoT 20, Guest 30, Servers 40, DMZ 50). Aligns with the security controls and firewall policies documented in `README.md` and `assets/documentation/security-policies.md`.

## How to Use This Playbook
1. **Stabilize first:** Preserve the default-deny posture—avoid temporary “allow any” rules. Prefer pulling known-good backups before major changes.
2. **Identify the blast radius:** Confirm which VLAN(s) and SSID(s) are affected to avoid unnecessary global changes.
3. **Follow the decision tree:** Each section provides a branch diagram plus stepwise diagnostics and resolution checks.
4. **Verify and log:** After remediation, run the listed verification steps and note findings in the ops journal for postmortems.

---

## 1) Connectivity Loss (WAN/LAN/VPN)

### Rapid Checks
- Confirm power and link on pfSense WAN/LAN, UniFi switch uplink, and AP trunks.
- Validate management plane reachability: `curl -k https://192.168.1.1` (pfSense) and `curl -k https://192.168.1.2:8443/status` (UniFi).

### Decision Tree
```
Can you reach pfSense UI/SSH?
├─ NO → Physical/power/cabling issue
│   ├─ Check PSU/UPS, NIC link LEDs
│   └─ Console in: verify interfaces are UP
└─ YES → pfSense reachable
    ├─ WAN down? (no IP/default route)
    │   ├─ Check modem sync, DHCP/PPPoE status
    │   └─ Renew WAN lease → test ping 8.8.8.8
    ├─ LAN down? (no ping to switch/AP)
    │   ├─ Verify LAN/VLAN interfaces UP
    │   └─ Check trunk native VLAN and allowed VLANs
    └─ VPN only? (OpenVPN)
        ├─ Check service status/logs
        └─ Validate certs and firewall rule on 1194/UDP
```

### Diagnostics
- **Interface state:** `ifconfig` → expect `status: active` on WAN + VLAN interfaces.
- **Routing:** `netstat -rn` → confirm default route via ISP gateway.
- **Ping matrix:** From pfSense shell, ping UniFi switch (192.168.1.2), AP (192.168.1.3), and a client on VLAN 10/20/30/40/50.
- **Packet filter:** `pfctl -s info` to ensure firewall enabled; `pfctl -sr` to confirm rules loaded.
- **VPN:** `sockstat -4 | grep 1194` and `clog /var/log/openvpn.log | tail` for listener and auth errors.

### Resolutions
- Reseat/replace cables or fail to backup WAN if modem offline; renew WAN lease in pfSense Status → Interfaces.
- If default route missing, reapply interface assignments (pfSense console option 1) and reload config backup.
- Restore firewall if disabled: `pfctl -e`; avoid rule flushes that break default-deny posture.
- For VPN, restart OpenVPN service; re-issue/re-import client certs if recent CA rotation occurred.

### Verification
- `ping -c 4 8.8.8.8` succeeds from pfSense and a VLAN 10 client.
- LAN interconnectivity: `ping 192.168.1.2` (switch) and `192.168.1.3/4` (APs) returns <5 ms.
- VPN client connects and routes to VLAN 10/40 while respecting policy blocks to VLAN 20/30/50.

---

## 2) DHCP / DNS Failures per VLAN

### Decision Tree
```
Clients lack IP?
├─ Scope exhausted?
│   └─ Check leases per VLAN, bump range only if within policy
├─ DHCP service down?
│   ├─ Check dhcpd status/logs per interface
│   └─ Restart dhcpd on affected VLAN
└─ VLAN tagging issue?
    ├─ Verify switch/AP port profiles
    └─ Ensure correct native VLAN on trunks

Clients have IP but no DNS?
├─ Check Unbound service health
├─ Validate firewall allows UDP/TCP 53 from VLAN
└─ Confirm DNS forwarders reachable upstream
```

### Diagnostics
- **Leases:** pfSense Status → DHCP Leases; confirm usage <80% and MACs match inventory.
- **Service status:** `ps aux | grep dhcpd` and `clog /var/log/dhcpd.log | tail` for per-interface failures.
- **Scope validation:** Ensure ranges align with design (e.g., VLAN 10: 192.168.1.50-200; VLAN 20: 192.168.20.50-200; etc.).
- **DNS health:** `dig @192.168.1.1 google.com` from each VLAN; `unbound-control status` for resolver state.
- **Firewall rules:** Confirm VLAN rules still permit DNS/HTTP/HTTPS as defined in security policies; check logs for blocks.

### Resolutions
- Increase scope only within documented VLAN subnets; avoid overlapping static reservations.
- Restart services: `pfSsh.php playback svc restart dhcpd` and `pfSsh.php playback svc restart unbound`.
- Clear rogue/unknown leases; add static mappings for trusted devices per policy.
- If DNSSEC failures observed, temporarily disable DNSSEC validation only after confirming upstream outage; re-enable post-restoration.
- For VLAN tagging faults, re-apply correct port profile (Trunk with VLAN 10 native + allowed 20/30/40/50) on UniFi switch/AP uplinks.

### Verification
- New clients obtain leases within 5 seconds on affected VLAN.
- `dig @192.168.1.1 homelab.local` and external lookups succeed from VLAN 10/20/30/40/50.
- DHCP logs show successful ACK per VLAN without `no free leases` or `bad packet` errors.

---

## 3) WiFi Performance Degradation (SSID: Trusted/IoT/Guest)

### Decision Tree
```
Is issue VLAN-specific or SSID-wide?
├─ Single SSID → Check SSID-to-VLAN mapping & PSK/RADIUS
├─ All SSIDs on one AP → Check RF health/PoE budget
└─ All APs → Check controller, backhaul, interference
```

### Diagnostics
- **Channel utilization:** UniFi → Insights → RF Environment; ensure 2.4 GHz <60% and 5 GHz <70%.
- **Client distribution:** Check band steering; avoid >40 clients per radio on U6 Pro.
- **PHY rates:** Look for excessive legacy (802.11b/g) associations; enforce minimum RSSI in controller if needed.
- **Interference sweep:** Confirm channels match plan (2.4 GHz: 1/6; 5 GHz: 36/149 @80 MHz). Avoid DFS if radar hits logged.
- **Backhaul:** `iperf3` between VLAN 10 client and server on VLAN 40 to validate wired path; check switch for errors (`show interfaces` via UniFi). 
- **QoS/contention:** Verify Smart Queues/traffic shaping on pfSense aren’t saturating uplink; inspect Suricata for drops.

### Resolutions
- Rebalance channels to non-overlapping set; reduce 5 GHz width to 40 MHz if DFS congestion persists.
- Enable minimum RSSI (e.g., -75 dBm) and band steering to shift capable clients to 5 GHz.
- Limit low-security devices to IoT SSID; enforce WPA3/802.1X on Trusted per policy.
- If single AP overloaded, add secondary AP or lower transmit power to improve roaming.
- Clear PoE alarms; ensure AP ports use PoE+ and have sufficient budget (see Section 5).

### Verification
- `ping -c 20 192.168.1.1` from wireless Trusted client shows <2% loss and <20 ms avg.
- Throughput test (`iperf3 -R`) meets expected LAN speeds (>300 Mbps on 5 GHz, >80 Mbps on 2.4 GHz) when interference low.
- Roaming between APs maintains session without drop for voice/Zoom.

---

## 4) VLAN Isolation / Routing Anomalies

### Decision Tree
```
Unexpected access across VLANs?
├─ Firewall rule drift?
│   ├─ Check pfSense rules vs security matrix
│   └─ Review recent changes/aliases
├─ Switch trunk misconfig?
│   ├─ Verify allowed VLANs on uplinks
│   └─ Check native VLAN matches design (10)
└─ Device on wrong port profile?
    └─ Ensure edge ports are access-mode with correct VLAN
```

### Diagnostics
- **Rule audit:** pfSense Firewall → Rules per interface; compare with policy: IoT/Guest to RFC1918 must be blocked, DMZ inbound only 80/443.
- **Logs:** Filter firewall logs for unexpected passes between RFC1918 nets.
- **Packet capture:** Use pfSense Packet Capture on VLAN interfaces to validate tagging and source VLAN.
- **Switch profiles:** In UniFi, confirm uplinks are Trunk (native 10) with allowed 20/30/40/50; edge ports set to Access with the intended VLAN.
- **Routing table:** `netstat -rn` to ensure per-VLAN gateways present; check for stray static routes.

### Resolutions
- Reapply saved firewall rule set from backup if drift detected; avoid temporary “allow any” exceptions that violate least privilege.
- Correct trunk/native VLAN on uplinks; remove unnecessary allowed VLANs to reduce bleed-over.
- Enforce DHCP snooping/port isolation on IoT/Guest ports where available; disable inter-VLAN L3 on switch (routing centralized on pfSense).
- For DMZ exposure, verify NAT/port forwards limited to 80/443 and IPS rules enabled on WAN/DMZ per policy.

### Verification
- From VLAN 20/30 clients, `ping 192.168.1.1` should fail (blocked) while internet works; VLAN 10 can reach VLAN 40 but is blocked to 20/30/50 per matrix.
- Packet captures show correct 802.1Q tags without untagged bleed on trunks.
- Suricata alerts quiet after isolating offending flow; firewall logs show expected blocks.

---

## 5) PoE Device Failures (APs, Cameras)

### Decision Tree
```
PoE device offline?
├─ Switch port down?
│   └─ Check link state & errors
├─ PoE budget exceeded? (US24P250 = 250W)
│   └─ Review total draw, per-port class
└─ Bad cable/injector?
    └─ Swap cable/port or move to injector
```

### Diagnostics
- **Port state:** UniFi → Devices → Switch → Ports; confirm link up, no excessive CRCs.
- **PoE budget:** Check UniFi “Power” tab; ensure remaining watts > device class (U6 Pro ≈ 13W typical).
- **LLDP/CDP:** Validate device identifies correctly; absence may indicate cabling or negotiation issues.
- **Environmental:** Check rack UPS output; confirm no brownout alarms.

### Resolutions
- Reduce load: disable PoE on unused ports; stagger camera power-up to avoid inrush trips.
- If budget tight, move high-draw device to injector or secondary switch.
- Replace suspect cable with Cat6; ensure AP ports configured for PoE+.
- Re-provision device in UniFi after restoring power to clear “Adopting” loops.

### Verification
- Port shows PoE (af/at) active with stable wattage; device heartbeat green in UniFi.
- Continuous ping to device IP returns <5 ms, no drops for 5 minutes.
- Controller no longer reports power or adoption alarms.

---

## Preventive Maintenance Routines
- **Weekly:** Review firewall/IPS logs for unexpected inter-VLAN passes; confirm DHCP scope utilization <80% per VLAN; verify Suricata signatures are current.
- **Bi-Weekly:** Run `dig @192.168.1.1` from each VLAN and `iperf3` Trusted↔Servers to baseline latency/throughput; document deltas.
- **Monthly:** Validate UniFi firmware and pfSense updates in maintenance window; backup configs before upgrades; re-verify VLAN rule matrix afterward.
- **Quarterly:** Re-run RF site survey, adjust channels/power; audit PoE budget against inventory growth; rotate VPN certs if nearing expiry.
- **After any change:** Re-run verification steps for affected section and log results in the ops journal to maintain change traceability.
