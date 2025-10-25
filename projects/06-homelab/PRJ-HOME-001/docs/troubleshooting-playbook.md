# Troubleshooting Playbook – "Is It the Network?"
**Applies To:** UniFi Home Network (PRJ-HOME-001)  \
**Audience:** Network Engineer II / on-call support

---

## 1. Intake & Scope
1. **Gather facts**: user, device type (wired/wireless), VLAN/SSID, timestamp, symptoms.
2. **Check monitoring dashboard** for concurrent alerts (AP offline, PoE overload, WAN loss).
3. **Classify impact**: single device, segment, or site-wide.

---

## 2. Layer 1 – Physical Validation
| Action | Command / Tool | Expected Result |
| --- | --- | --- |
| Verify link state | `show interfaces` (UniFi SSH) | Up/Down status without errors |
| Check cable health | UniFi Network → Tools → Cable Test | Pass (≤ 1m skew) |
| Validate PoE budget | UniFi Network → Insights → PoE | Total draw < 80% |
| Inspect hardware | Physical LED indicators, camera feed | Link lights active, no water ingress |

If failure is localized to outdoor pod, swap patch port to known-good PoE port and retest.

---

## 3. Layer 2 – Switching & VLANs
1. Confirm switch port profile assignments match documentation (APs = trunk, cameras/flood lights = VLAN 30).
2. Use `tcpdump -i brX vlan 30` on UDM-Pro to verify tag presence for suspected device.
3. Inspect UniFi client list for duplicate MAC entries or blocked clients.
4. For wireless issues, review RF environment (channel utilization > 70% triggers re-channeling).

---

## 4. Layer 3 – Routing & Services
| Scenario | Diagnostic | Resolution |
| --- | --- | --- |
| Device cannot obtain IP | Check DHCP leases (Clients → Filter by VLAN) | Restart DHCP service, verify scope exhaustion |
| IoT device unreachable from trusted VLAN | Review firewall rules (Settings → Firewall) | Confirm IoT-to-Trusted rule is deny (expected); create temporary allow for troubleshooting |
| WAN unreachable | `ping 8.8.8.8` from UDM-Pro; `ping` ISP gateway | Open case with ISP if gateway unreachable; otherwise check firewall rules |
| Management access lost | Console into switch via out-of-band serial | Reapply management VLAN IP/static config |

---

## 5. Performance & Application Layer
1. Run `iperf3` tests between wired host and AP-connected client to isolate RF vs. WAN bottlenecks.
2. Check UniFi Protect camera bitrates and recording status; high CPU on Protect indicates storage contention.
3. For voice/video complaints, verify QoS Smart Queues on UDM-Pro and review latency/jitter graphs in monitoring dashboard.

---

## 6. Evidence Capture
- Export relevant syslog entries via `logread | tail -n 200` on UDM-Pro.
- Download packet captures (UniFi Network → Tools → Packet Capture) for impacted VLAN.
- Take timestamped photos/screenshots of physical conditions or error messages.

Store evidence in `projects/06-homelab/PRJ-HOME-001/artifacts/incidents/<YYYYMMDD>-<shortdesc>/`.

---

## 7. Escalation Criteria
| Trigger | Escalate To | SLA |
| --- | --- | --- |
| WAN outage > 30 minutes | ISP NOC | 1 hour | 
| UniFi Protect NVR storage failure | Systems Engineer | 2 hours |
| Security breach or rogue device | Security Operations | Immediate |
| Repeated AP reboot loop | UniFi Support (vendor) | 24 hours |

---

## 8. Post-Mortem Checklist
1. Document root cause, remediation, and lessons learned.
2. Update runbooks, IP plan, or firewall rules as applicable.
3. Schedule follow-up to validate fix (e.g., verify RSSI after AP relocation).
4. Communicate summary to stakeholders/homeowner within 24 hours.

