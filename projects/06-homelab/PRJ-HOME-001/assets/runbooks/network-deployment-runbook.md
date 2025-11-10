# Homelab Network Build – End-to-End Deployment Procedure

**Runbook Version:** 1.0  
**Author:** Infrastructure Engineering  
**Last Updated:** 2024-05-30  
**Applies To:** PRJ-HOME-001 segmented UniFi homelab deployment

---

## 1. Prerequisites (Pre-Deployment)

Complete each prerequisite before touching production equipment:

- [ ] Hardware inventory validated (ISP modem, UDMP, USW-24-POE, USW-8-60W, 3× AP AC Pro, CyberPower UPS, patch panel, rack, cabling, tools).
- [ ] Cable runs planned, lengths measured, and labeled per room (Cat6a plenum).
- [ ] Wall-mounted 12U rack secured to studs, weight-tested to 75 lbs.
- [ ] UPS installed, batteries conditioned, load test completed (simulate 10-minute outage).
- [ ] ISP modem placed in bridge mode (coordinate with ISP support to disable NAT/Wi-Fi).
- [ ] Review network design package (VLAN matrix, firewall policy, IP scheme, this runbook).

> **Tip:** Photograph the existing network before changes for rollback reference.

---

## 2. Physical Installation (Day 1)

### Step 2.1 – Rack Equipment Installation
- [ ] Install patch panel at rack unit (RU) 1 using cage nuts and M6 screws.
- [ ] Mount UniFi Dream Machine Pro at RU 2; ensure exhaust clearance ≥ 2 inches.
- [ ] Mount UniFi Switch 24 PoE at RU 3; connect to UPS using IEC power cord.
- [ ] Mount horizontal cable management at RU 4 and RU 5.
- [ ] Place UniFi Switch 8 PoE on RU 6 shelf (or wall mount near remote desk).
- [ ] Connect UPS to dedicated surge-protected outlet; verify grounding.

**Validation:** Shake rack lightly—no wobble. Confirm power sequencing: UPS → switches → UDMP.

### Step 2.2 – Cable Termination
- [ ] Pull Cat6a runs from each room back to rack; label both ends (e.g., `LR-TV-01`).
- [ ] Terminate patch panel using T568B wiring scheme.
- [ ] Crimp keystone jacks for in-room wall plates using matching labels.
- [ ] Use cable tester (Klein Tools VDV Scout Pro) to validate continuity and wire map.

```bash
# Example test log entry
Test Port: LR-TV-01  Result: PASS  Speed: 1 Gbps  Length: 62 ft
```

### Step 2.3 – Access Point Installation
- [ ] Mount AP AC Pros to ceiling brackets in living room, bedroom hallway, and office.
- [ ] Route cabling discreetly (attic or conduit) to maintain aesthetics and shield interference.
- [ ] Patch AP cables into panel ports 15–17; cross-connect to USW-24 PoE ports 15–17.
- [ ] Power on USW-24; ensure PoE budget (95 W) covers three APs (~12 W each) with 59 W headroom.

**Validation:** AP LED transitions white → blue within 5 minutes (adoption pending).

---

## 3. UniFi Dream Machine Pro Initial Configuration (Day 1)

### Step 3.1 – Factory Reset & Setup Wizard
- [ ] Hold UDMP reset button 10 seconds to ensure clean state.
- [ ] Connect laptop to LAN Port 1; assign static 192.168.1.100/24 temporarily.
- [ ] Browse to `https://192.168.1.1`; complete setup wizard:
  - Country/Timezone → align with physical location.
  - Device Name → `UDMP-Homelab`.
  - Admin Credentials → use Bitwarden-generated 24-char password.
  - Enable remote access only if 2FA configured; otherwise leave disabled.

### Step 3.2 – WAN Configuration
- [ ] Connect UDMP WAN (eth9) to bridged ISP modem via Cat6a.
- [ ] Configure WAN as DHCP (adjust to static if ISP provides dedicated IP).

```bash
ssh admin@192.168.1.1
ip addr show eth9            # Confirm WAN IP issued
ping -c 4 1.1.1.1            # Validate raw connectivity
ping -c 4 google.com         # Validate DNS resolution
```

**Expected Output:** 0% packet loss, latency < 20 ms to 1.1.1.1.

### Step 3.3 – Adopt Switches & APs
- [ ] Navigate to **UniFi Network → Devices → Pending Adoption**.
- [ ] Adopt USW-24, USW-8, and APs sequentially; wait for firmware updates to finish.
- [ ] Enable Auto-Optimize off (prefer manual tuning) under system settings.

---

## 4. VLAN Configuration (Day 2)

Navigate to **Settings → Networks** and create/verify the following networks:

| Network | VLAN ID | Subnet | DHCP Scope | DNS | Notes |
|---------|---------|--------|------------|-----|-------|
| Management | 1 | 192.168.1.0/24 | Disabled | — | Static mgmt IPs only. |
| Trusted | 10 | 192.168.10.0/24 | 192.168.10.100-200 | 192.168.10.2 | Primary user/workload subnet. |
| IoT | 50 | 192.168.50.0/24 | 192.168.50.100-200 | 1.1.1.1 | mDNS reflector enabled. |
| Guest | 99 | 192.168.99.0/24 | 192.168.99.100-200 | 1.1.1.1 / 9.9.9.9 | Guest isolation enabled. |
| Lab | 100 | 192.168.100.0/24 | 192.168.100.100-200 | 192.168.10.2 | Short (1 hr) leases. |

**Validation:** `Settings → Networks` displays five networks with correct subnets and VLAN IDs.

---

## 5. Wi-Fi SSID Configuration (Day 2)

### Step 5.1 – Homelab-Trusted
- SSID: `Homelab-Trusted` → Network: Trusted (VLAN 10).
- Security: WPA3 Personal (allow WPA2 fallback).
- Band steering enabled; fast roaming (802.11r) on; minimum RSSI -70 dBm.

### Step 5.2 – Homelab-IoT
- SSID: `Homelab-IoT` → Network: IoT (VLAN 50).
- Security: WPA2 Personal; 2.4 GHz only; multicast enhancement for mDNS.

### Step 5.3 – Homelab-Guest
- SSID: `Homelab-Guest` → Network: Guest (VLAN 99).
- Security: WPA2 Personal + captive portal (voucher mode, 24-hour validity).
- Rate limiting: 10 Mbps down / 5 Mbps up per device.

### Step 5.4 – Homelab-Lab
- SSID: `Homelab-Lab` → Network: Lab (VLAN 100).
- Security: WPA2 Personal; 5 GHz only; SSID hidden for obscurity.

**Validation:** Join each SSID with test devices; confirm DHCP allocation from correct pool via `ipconfig`/`ifconfig`.

---

## 6. Firewall Rule Configuration (Day 3)

Navigate to **Settings → Firewall → LAN IN** and implement rules per [firewall-rules.md](../configs/firewall-rules.md). Key steps:

1. Place **Admin Workstations to Management** rule at top to avoid accidental lockout.
2. Insert IoT/Guest deny rules above allow-any rules to enforce segmentation.
3. Enable logging on all deny rules and critical allows.
4. Apply traffic shaping policies: Guest (10 Mbps), Lab (50 Mbps) under **Traffic & Device Management**.

**Validation Tests:**

```bash
# From IoT device (e.g., smart TV developer shell)
ping 8.8.8.8                # Expect success
ping 192.168.10.10          # Expect timeout (blocked by Rule 8)

# From trusted workstation
ssh admin@192.168.1.1       # Expect login prompt (Rule 1 allows)
```

Document rule order screenshots in `assets/screenshots/`.

---

## 7. Static IPs & DHCP Reservations (Day 3)

1. Configure static IPs directly on critical hosts:
   - Proxmox VE (`/etc/network/interfaces`) → 192.168.10.10/24, gateway 192.168.10.1.
   - TrueNAS (`Network → Interfaces`) → 192.168.10.5/24.
   - Pi-hole → 192.168.10.2/24 (secondary interface 192.168.1.21 optional).
2. Define DHCP reservations in UniFi for workstations, printers, smart TV, thermostat, Hue bridge, and cameras.
3. Export updated IP plan to [ip-addressing-scheme.md](../configs/ip-addressing-scheme.md).

---

## 8. DNS Configuration with Pi-hole (Day 4)

### Step 8.1 – Install Pi-hole
```bash
ssh pi@192.168.10.2
curl -sSL https://install.pi-hole.net | bash
# Configure upstream DNS → Cloudflare (1.1.1.1, 1.0.0.1)
# Enable web admin with lighttpd
```

### Step 8.2 – Integrate with UniFi
- Trusted VLAN DHCP DNS → 192.168.10.2 (primary), 1.1.1.1 (secondary).
- Lab VLAN DHCP DNS → 192.168.10.2 (supports custom records for lab hosts).
- IoT/GUEST VLANs remain pointed at public DNS for resilience.

**Validation:**
```bash
nslookup doubleclick.net 192.168.10.2   # Expect 0.0.0.0 (blocked)
nslookup google.com 192.168.10.2        # Expect valid A records
```

---

## 9. WireGuard VPN Configuration (Day 4)

1. Enable **Settings → VPN → WireGuard** on UDMP.
2. Create user profile `remote-admin`; generate client configuration file.
3. Expose UDP port 51820 via port forward; restrict source countries via Geo-IP filter.
4. Distribute `.conf` to client devices via password manager.

**Validation:** Connect from LTE network; confirm access to trusted resources (e.g., `ssh proxmox.trusted`).

---

## 10. Verification & Testing (Day 5)

| Test | Command/Action | Expected Result |
|------|----------------|-----------------|
| Internet reachability (all VLANs) | `ping 1.1.1.1` from representative device | <20 ms latency, 0% loss |
| Inter-VLAN isolation | Attempt `ping 192.168.10.10` from IoT device | Timeout (firewall Rule 8) |
| Trusted admin access | `ssh admin@192.168.1.1` from workstation | Prompt for password/SSH key |
| Guest captive portal | Connect mobile to `Homelab-Guest` | Portal page, voucher required |
| VPN routing | Connect WireGuard client | Receive IP 10.6.0.x, access trusted resources |
| Throughput test | `iperf3 -c 192.168.10.10` (wired) | ≥ 900 Mbps |
| Wi-Fi coverage | Walk test with UniFi WiFiman app | RSSI better than -65 dBm in coverage zones |

Log results in deployment notes for auditability.

---

## 11. Backup & Restore Planning (Day 5)

- Enable UniFi automatic backups (daily, retain 7 days) under **System → Backup**.
- Download initial backup and store in encrypted vault (1Password/Bitwarden Secure Note).
- Document configuration export steps for Pi-hole, TrueNAS, and Proxmox.

---

## 12. Documentation & Labeling (Day 5)

- Label patch panel and switch ports with Brother P-touch (e.g., `AP-LR-15`).
- Update architectural diagrams (`assets/diagrams/*.mermaid`) with any changes.
- Capture controller screenshots: device overview, topology map, firewall rules.
- Store runbook, diagrams, and screenshots in Git repository for version control.

---

## 13. Ongoing Maintenance

| Cadence | Task |
|---------|------|
| Weekly | Review UniFi alerts, inspect Pi-hole query logs, verify UPS self-test status. |
| Monthly | Apply firmware updates (UDMP, switches, APs); review firewall logs for anomalies. |
| Quarterly | Audit DHCP reservations, validate VPN access list, perform restore drill using UniFi backup. |
| Annually | Inspect cabling for wear, dust equipment, evaluate power capacity, revisit VLAN design. |

---

## 14. Rollback Procedure

1. **Stop** at the failure point; document the issue (timestamp, device, observed error).
2. Restore previous UniFi backup via **System → Backup → Restore**; reboot UDMP if prompted.
3. Factory reset affected hardware (switch/AP) if configuration drift persists.
4. Reconnect ISP modem/router to legacy configuration if internet outage exceeds 30 minutes.
5. Escalate to network lead if rollback fails; engage vendor support as needed.

---

## 15. Sign-Off Checklist

Deployment is considered complete when all items are verified:

- [ ] VLANs and DHCP scopes match documented ranges.
- [ ] All SSIDs broadcasting with correct security and VLAN tagging.
- [ ] Firewall rules enforce intended allow/deny policies.
- [ ] Internet access and VPN connectivity validated from each zone.
- [ ] UniFi backup scheduled and initial backup archived.
- [ ] Documentation (runbook, diagrams, configs) updated with as-built state.

Store signed checklist in `assets/docs/deployment-approvals/`.

---

## Appendix A – Useful Commands

```bash
# Display VLAN tagging on UDMP
show interfaces switchport

# Verify traffic shaping policies
show qos status

# List active DHCP leases on UDMP
show dhcp leases

# AP adoption troubleshooting
ssh ubnt@192.168.1.10 "info"

# Restart network stack on UDMP (maintenance window only)
restart switch
```

## Appendix B – Support Contacts

| Provider | Contact | Notes |
|----------|---------|-------|
| ISP Tier-2 Support | 1-800-XXX-XXXX | Request bridged modem assistance; reference account ###. |
| Ubiquiti Enterprise Support | https://help.ui.com | Use support ticket with device serials from UniFi. |
| Internal Network Lead | on-call alias | Escalate major outages or security incidents. |

Maintain this runbook under version control; increment version upon each process refinement.
