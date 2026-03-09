# UniFi Switch 24 PoE – Port Map

## Hardware Summary
- **Model:** UniFi Switch 24 PoE (US24P250)
- **Management IP:** `192.168.1.2`
- **PoE Budget:** 250W total, 16x PoE+ capable ports
- **Firmware Mode:** VLAN-aware switching with RSTP and LLDP enabled

## Port Profiles

| Profile | Mode | Native VLAN | Tagged VLANs | PoE | Security Notes |
|---------|------|-------------|--------------|-----|----------------|
| **Uplink** | Trunk | 10 (Trusted) | 10, 20, 30, 40, 50 | Off | Open trunk for firewall uplink |
| **Access Point PoE** | Trunk (AP) | 10 (Trusted) | 20 (IoT), 30 (Guest) | Auto (802.3at) | Port security enabled; forwards only allowed VLANs |
| **Trusted Device** | Access | 10 (Trusted) | — | Off | Full access for wired clients |
| **Server** | Access | 40 (Servers) | — | Off | Port security + LLDP-MED enabled |

## Port Map

| Port | VLAN Mode | Profile | Native / Tagged VLANs | Speed | PoE | Device / Location | Notes |
|------|-----------|---------|-----------------------|-------|-----|-------------------|-------|
| 1 | Trunk | Uplink | Native 10; Tagged 10/20/30/40/50 | 1 Gbps | Off | pfSense firewall uplink | Carries all VLANs |
| 2 | Trunk (AP) | Access Point PoE | Native 10; Tagged 20/30 | 1 Gbps | Auto | U6 Pro – Living Room | WPA3/Guest SSIDs |
| 3 | Trunk (AP) | Access Point PoE | Native 10; Tagged 20/30 | 1 Gbps | Auto | U6 Pro – Office | WPA3/Guest SSIDs |
| 4 | Access | Server | Native 40 | 1 Gbps | Off | Proxmox-01 | Hypervisor node |
| 5 | Access | Server | Native 40 | 1 Gbps | Off | Proxmox-02 | Hypervisor node |
| 6 | Access | Server | Native 40 | 1 Gbps | Off | Proxmox-03 | Hypervisor node |
| 7 | Access | Server | Native 40 | 1 Gbps | Off | TrueNAS | Storage |
| 8 | Access | Trusted Device | Native 10 | 1 Gbps | Off | Workstation-01 | Primary desktop |
| 9–24 | — | — | — | — | Off | Available | Labeled and tested, ready for use |

## PoE Budget Summary
- **Total Budget:** 250W
- **Active PoE Loads:** 2x U6 Pro APs @ ~13W each (≈26W)
- **Remaining Headroom:** ≈224W available for future PoE devices
- **Policy:** PoE disabled on non-AP ports; enable per-port as needed to conserve budget and reduce fault domain.

## Cable Run Details
- **Patch Panel Labels:** Port 1 “pfSense Uplink”, Port 2 “Living Room AP”, Port 3 “Office AP”, Ports 4-7 “Servers (Proxmox/TrueNAS)”, Port 8 “Workstation”.
- **Cable Types:** Cat6a for all runs; factory-terminated patch leads in rack.
- **Lengths:** Rack interconnects 1–3 ft; Living Room AP 25 ft; Office AP 75 ft; server/workstation drops 3–6 ft to rack.
- **Notes:** All drops tested with cable tester (pass), keystones terminated T568B, PoE verified at AP drops during provisioning.

## Maintenance Log

| Date | Activity | Details |
|------|----------|---------|
| 2025-11-05 | Baseline provisioning | Adopted switch and applied port profiles; validated VLAN tagging on Ports 1–3; verified PoE draw per AP (~13W). |
| 2025-11-12 | Firmware/port audit | Confirmed RSTP/LLDP enabled; re-tested trunk to pfSense after rules update; checked PoE headroom (available > 220W). |
| 2025-12-01 | Cable verification | Retested Living Room and Office AP drops (25ft/75ft); replaced rack patch leads with Cat6a 1ft to reduce bend radius. |
| 2026-01-10 | Quarterly review | Confirmed MAC lock on AP ports still aligned; spot-checked server VLAN 40 access and workstation native VLAN 10 connectivity. |

