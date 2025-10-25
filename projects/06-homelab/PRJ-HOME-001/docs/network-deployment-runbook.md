# Network Deployment Runbook
**Project:** PRJ-HOME-001 – UniFi Home Network Refresh  \
**Environment:** Residential (two-story + outdoor coverage)  \
**Version:** 1.0 (2024-06-09)

---

## 1. Pre-Deployment Checklist
| Item | Owner | Status |
| --- | --- | --- |
| Site survey photos and RF heatmap captured | Network Eng | ☐ |
| Rack location cleared, dedicated circuit confirmed | Homeowner | ☐ |
| Cable pathways inspected (attic, crawlspace, exterior conduit) | Facilities | ☐ |
| Equipment firmware downloaded to local laptop | Network Eng | ☐ |
| IP plan validated against inventory | Network Eng | ☐ |
| Change approval (homeowner sign-off) | Stakeholder | ☐ |

---

## 2. Staging Procedures
1. **Bench configuration** (lab bench):
   - Power UDM-Pro, Switch Pro 24 PoE, and Cloud Key using UPS.
   - Assign management IPs from VLAN 10 scope.
   - Upgrade firmware to approved versions; disable auto-updates.
2. **Adopt APs and cameras** in UniFi Network/Protect using temporary VLAN 99 staging network.
3. **Backup baseline configs** to laptop + NAS (Services VLAN) before field deployment.

---

## 3. Installation Steps
### 3.1 Rack & Power
1. Mount UPS at rack base, followed by patch panel, switch, UDM-Pro, Cloud Key.
2. Verify cable management (horizontal + vertical) and label patch panel ports.
3. Energize UPS, confirm load ≤ 60% capacity.

### 3.2 Cabling & Termination
1. Pull CAT6A runs to each AP/camera/flood light location; terminate to T568B.
2. Test each cable with Fluke DSX-5000 (document results in acceptance folder).
3. Patch outdoor pods to shielded keystones; weatherproof external junction boxes.

### 3.3 Network Configuration
1. Import bench configurations on-site via UniFi backup restore.
2. Update WAN settings per ISP credentials; verify internet access.
3. Assign VLAN profiles to switch ports:
   - Trunk (10/20/30/40/50) for APs
   - Access VLAN 30 for cameras/flood lights
   - Access VLAN 20 for wired workstation ports
4. Enable DHCP guards, storm control, and LLDP-MED.

### 3.4 Wireless & Protect Validation
1. Map SSIDs to AP groups (Downstairs, Upstairs, Outdoor).
2. Run RF scan; adjust transmit power (medium indoor, low outdoor) and channel assignments.
3. Add cameras/flood lights to UniFi Protect; configure recording schedules and motion zones.
4. Verify doorbell cameras associate to Outdoor APs with RSSI ≥ -65 dBm.

---

## 4. Validation Tests
| Test | Procedure | Pass Criteria |
| --- | --- | --- |
| VLAN segmentation | Laptop on VLAN 20 attempts to ping VLAN 30 host | ICMP blocked, DNS allowed |
| Guest isolation | Guest client attempts LAN discovery | mDNS/SMB blocked |
| Throughput | iPerf3 between wired host and Wi-Fi client (5 GHz) | ≥ 600 Mbps peak |
| Camera stream | Review Protect timeline per camera | 24/7 recording, no gaps |
| UPS runtime | Simulate power loss | ≥ 20 minutes runtime, graceful shutdown events logged |

Record results in commissioning sheet stored at `docs/commissioning/2024-06-udmpro.xlsx`.

---

## 5. Post-Deployment Tasks
- Capture final rack/cabling photos; update asset inventory.
- Schedule firmware maintenance window cadence (quarterly).
- Deliver documentation bundle (this runbook + IP plan + topology) to homeowner.
- Set calendar reminders for monthly monitoring review and quarterly failover drill.

---

## 6. Rollback Plan
1. Restore pre-change configuration backups on UDM-Pro and switch.
2. Disconnect new cabling from patch panel; reconnect legacy network if applicable.
3. Revert DNS/DHCP scopes to prior settings.
4. Document incident and corrective actions in change log.

