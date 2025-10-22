# Homelab & Secure Network Build

## Objective
- Reconstruct the end-to-end documentation for the wired rack, UniFi-controlled Wi-Fi, and segmented VLAN layout that underpins the homelab network.
- Capture the security, backup, and monitoring practices that keep the environment resilient and reproducible.

## Key Artifacts to Produce
- [ ] **Network Topology Diagram** – physical + logical view of switches, firewall, APs, and inter-VLAN routes ([Coming Soon](./artifacts/network-topology.md)). *(Target format: draw.io + PNG export)*
- [ ] **Rack Elevation & Cable Map** – labeled ports, patch-panel mapping, and power layout ([Coming Soon](./artifacts/rack-elevation.md)). *(Target format: PDF + CSV patch schedule)*
- [ ] **VLAN/IPAM Matrix** – subnet allocations, DHCP scopes, and reserved addresses ([Coming Soon](./artifacts/vlan-ipam.md)). *(Target format: Google Sheet export)*
- [ ] **Network Hardening Checklist** – MFA, RBAC, firmware patch cadence, and guest/IoT isolation tasks ([Coming Soon](./checklists/network-hardening.md)).
- [ ] **Operations Runbook** – backup workflow, firmware rollback steps, and change-control template ([Coming Soon](./runbooks/network-operations.md)).
- [ ] **Monitoring & Alert Notes** – UniFi/Prometheus metrics to capture and alert thresholds ([Coming Soon](./dashboards/network-observability.md)).

## Current Backfill Status
- Status: 🔵 **Planned** – topology exists but artifacts were never captured in version control.
- Owner: Sam Jackson
- Target Backfill Window: 2025-03

## Recovery Dependencies & Blockers
- [ ] Export latest UniFi Network configuration to extract VLAN names and firewall rules. *(Blocked: controller VM powered down until UPS batteries are replaced.)*
- [ ] Pull rack photos/labels from NAS archive for accurate cable mapping. *(Dependency: locate external drive with 2024-Q4 photo dump.)*
- [ ] Re-run nmap/L2 discovery to confirm current device inventory. *(Dependency: schedule maintenance window to avoid disrupting PoE cameras.)*

## Coordination Notes
- Align artifact formats with the standards set in `docs/PRJ-MASTER-PLAYBOOK` once that repository is restored.
- Share drafts with the virtualization project (PRJ-HOME-002) so service dependencies stay consistent across runbooks.
