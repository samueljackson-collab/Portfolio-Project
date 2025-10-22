# Virtualization & Core Services Stack

## Objective
- Document the Proxmox + TrueNAS environment that hosts core services (Wiki.js, Home Assistant, Immich) behind a reverse proxy with TLS.
- Capture lifecycle procedures for provisioning, patching, backup/restore, and certificate rotation across the virtualized stack.

## Key Artifacts to Produce
- [ ] **Service Dependency Diagram** – Proxmox clusters, storage, reverse proxy, and service interconnects ([Coming Soon](./artifacts/service-map.md)). *(Target format: draw.io + SVG export)*
- [ ] **VM Inventory Sheet** – resource sizing, purpose, and backup retention policy ([Coming Soon](./artifacts/vm-inventory.md)). *(Target format: spreadsheet export)*
- [ ] **Reverse Proxy & TLS Runbook** – certificate renewal automation, DNS validation, and failover steps ([Coming Soon](./runbooks/reverse-proxy-tls.md)).
- [ ] **Backup & Restore Guide** – Proxmox Backup Server (PBS) schedules, TrueNAS replication notes, and recovery drills ([Coming Soon](./runbooks/backup-restore.md)).
- [ ] **Service Health Dashboard Checklist** – Grafana dashboards + alert rules needed for each workload ([Coming Soon](./dashboards/service-health.md)).
- [ ] **Patch & Change Calendar** – monthly cadence for hypervisor, guest OS, and application updates ([Coming Soon](./calendars/patch-schedule.md)).

## Current Backfill Status
- Status: 🟠 **In Progress** – PBS job notes exist offline, diagrams missing, runbooks incomplete.
- Owner: Sam Jackson
- Target Backfill Window: 2025-04

## Recovery Dependencies & Blockers
- [ ] Confirm last-known-good PBS snapshots for Wiki.js and Immich. *(Dependency: mount PBS datastore that is currently stored off-site.)*
- [ ] Retrieve reverse proxy config backup from NAS ZFS snapshots. *(Blocked until NAS resilver completes; ETA 2025-02-15.)*
- [ ] Export Home Assistant automations for inclusion in service inventory. *(Waiting on Zigbee dongle replacement to bring HA online.)*

## Coordination Notes
- Align monitoring artifacts with observability project PRJ-SDE-002 to avoid duplicate dashboard definitions.
- Share inventory sheet with PRJ-HOME-001 to ensure network VLAN assignments match service placement.
