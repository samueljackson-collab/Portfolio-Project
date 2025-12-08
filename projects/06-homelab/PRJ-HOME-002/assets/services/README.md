# Service Inventory

Sanitized summary of services deployed in PRJ-HOME-002. Use this as a quick reference when matching screenshots, compose files, and proxy definitions.

| Service | Role | Hostname | IP (example) | Data Location | Notes |
| --- | --- | --- | --- | --- | --- |
| Nginx Proxy Manager | Reverse proxy + TLS | npm.example.com | 192.168.40.25 | `/opt/nginx-proxy-manager` | Import config from `configs/nginx-proxy-manager/proxy-hosts-example.json` |
| Wiki.js | Knowledge base | wiki.example.com | 192.168.40.20 | `/opt/wikijs` + PostgreSQL | Compose: `configs/docker-compose-wikijs.yml` |
| Home Assistant | Smart home hub | ha.example.com | 192.168.40.21 | `/opt/home-assistant` + PostgreSQL | Compose: `configs/docker-compose-homeassistant.yml` |
| Immich | Photo management | photos.example.com | 192.168.40.22 | `/opt/immich` + TrueNAS NFS | Compose: `configs/docker-compose-immich.yml` |
| PostgreSQL | Database backend | db.example.com | 192.168.40.23 | `/var/lib/postgresql` | Compose: `configs/docker-compose-postgresql.yml` |
| Monitoring Stack | Prometheus/Grafana | monitor.example.com | 192.168.40.30 | `/opt/monitoring` | Alerts referenced in `configs/monitoring/README.md` |
| Proxmox Backup Server | Backup + dedupe | pbs.example.com | 192.168.40.15 | `/mnt/datastore/homelab-backups` | Policy defined in `proxmox/backup-config.json` |

## Screenshot Map
- Proxy + TLS evidence → `screenshots/nginx-proxy-manager-hosts.png`
- Application UIs → `screenshots/wikijs-home.png`, `screenshots/home-assistant-overview.png`, `screenshots/immich-library.png`
- Infrastructure health → `screenshots/proxmox-dashboard.png`, `screenshots/proxmox-ha-groups.png`, `screenshots/truenas-dataset-layout.png`
- Backup/Monitoring → `screenshots/pbs-job-status.png`, `screenshots/grafana-backup-overview.png`, `screenshots/loki-log-search.png`

## Proxmox Definitions
- Cluster membership and HA groups captured in `../proxmox/cluster.conf` and `../proxmox/network-interfaces`.
- VM templates and cloud-init settings stored under `../proxmox/vm-templates/`.
- Backup schedule stored in `../proxmox/backup-config.json` and mirrored in `docs/backup-strategy.md`.

## TrueNAS Layouts
- Dataset hierarchy and snapshot/replication policies in `../configs/truenas/dataset-structure.md`.
- NFS/iSCSI exports align to compose mounts for Immich and PostgreSQL.
