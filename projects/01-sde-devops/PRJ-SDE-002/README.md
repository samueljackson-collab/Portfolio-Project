# Observability & Backup Reliability Stack

## Objective
- Rebuild the documentation and automation for the Prometheus, Grafana, Loki, Alertmanager, and Proxmox Backup Server (PBS) deployment supporting the homelab services.
- Provide clear runbooks and dashboards so on-call responders can detect, triage, and recover from failures quickly.

## Key Artifacts to Produce
- [ ] **Architecture Diagram** – data flow from exporters/log shippers to Prometheus/Loki, alert routing, and PBS integration ([Coming Soon](./artifacts/observability-architecture.md)). *(Target format: draw.io + PNG export)*
- [ ] **Dashboard Inventory** – Grafana board list with golden-signal metrics, owners, and alert thresholds ([Coming Soon](./dashboards/dashboard-inventory.md)).
- [ ] **Alert Catalog** – Alertmanager rules, notification targets, and test procedures ([Coming Soon](./runbooks/alert-catalog.md)).
- [ ] **Backup Validation Runbook** – PBS job verification, restore drills, and integrity checks ([Coming Soon](./runbooks/backup-validation.md)).
- [ ] **Infrastructure-as-Code Checklist** – Git repo structure, secrets handling, and CI validation steps ([Coming Soon](./checklists/iac-readiness.md)).
- [ ] **SLO/Error Budget Policy** – definitions for uptime, restore time, and backup success SLOs ([Coming Soon](./policies/slo-error-budget.md)).

## Current Backfill Status
- Status: 🟠 **In Progress** – legacy Grafana exports are available but need to be normalized; alert catalog missing.
- Owner: Sam Jackson
- Target Backfill Window: 2025-04

## Recovery Dependencies & Blockers
- [ ] Import legacy Grafana JSON exports from the NAS `backups/grafana/` folder. *(Dependency: decrypt vault archive once key escrow is retrieved.)*
- [ ] Rebuild Alertmanager webhook integration with Matrix. *(Blocked pending Matrix homeserver credentials from password manager.)*
- [ ] Validate PBS datastore health after NAS resilver completes. *(Shared blocker with PRJ-HOME-002; track on combined ops board.)*

## Coordination Notes
- Reuse exporter configurations captured in PRJ-HOME-002 once services are back online to avoid drift.
- Align SLO definitions with production-style documentation in `docs/PRJ-MASTER-HANDBOOK` when that repo is available.
