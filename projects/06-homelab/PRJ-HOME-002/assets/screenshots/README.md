# Service Screenshots

Sanitized screenshots demonstrating key services. Filenames and URLs use placeholders (example.com).

## Proxmox & Infrastructure
- `proxmox-dashboard.png` — Cluster overview showing three nodes, Ceph health (HEALTH_OK), and PBS datastore usage.
- `proxmox-ha-groups.png` — HA group assignments for P0/P1 services.
- `truenas-dataset-layout.png` — Dataset and snapshot schedule view matching `configs/truenas/dataset-structure.md`.

## Core Services
- `nginx-proxy-manager-hosts.png` — Proxy host list with forced SSL and HSTS enabled.
- `wikijs-home.png` — Wiki.js landing page with SSO banner (domain sanitized).
- `home-assistant-overview.png` — Dashboard cards for sensors and automations.
- `immich-library.png` — Immich album view; upload status ribbon visible.

## Monitoring & Backups
- `grafana-backup-overview.png` — Grafana panel showing PBS job durations, dedupe ratio, and success rate.
- `loki-log-search.png` — Loki query for `vm=immich-prod` with structured fields.
- `pbs-job-status.png` — Proxmox Backup Server UI showing completed jobs and retention policy badges.

## Usage Notes
- Screenshots are sanitized and intended for evidence tracking; remove or blur any sensitive metadata before publishing.
- For new captures, place files in this directory using the naming convention above and update this README accordingly.
