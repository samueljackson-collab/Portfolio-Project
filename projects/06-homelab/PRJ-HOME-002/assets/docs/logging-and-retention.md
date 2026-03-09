# Logging and Retention

Centralized logging and retention guidelines for Proxmox, TrueNAS, and core services.

## Log Ingestion
- **Rsyslog** receives logs on TCP/UDP 514 following `assets/services/rsyslog/rsyslog.conf` inputs.
- **Promtail** forwards application logs to Loki using the labels defined in `assets/configs/monitoring/promtail/config.yml`.
- **Ceph & Proxmox** forward system logs to the Rsyslog collector; PBS jobs emit to `journalctl -u proxmox-backup`.

## Retention Policy
- **Rsyslog on PBS:** 30 days hot storage on Ceph-backed filesystem; compressed archives retained for 90 days on TrueNAS.
- **Loki:** 14 days indexed logs for quick search; object storage tier on TrueNAS retains chunks for 60 days.
- **Proxmox Tasks:** Task logs retained 30 days; rotation defined in `/etc/pve/datacenter.cfg` and mirrored in `assets/proxmox/cluster.conf` notes.

## Access & Reporting
- Grafana dashboards surface log volume and error rates; links referenced from `assets/screenshots/service-screenshots.md`.
- Incident responders must export relevant logs to case folders within the TrueNAS `audit/` dataset described in `assets/configs/truenas/dataset-layout.md`.
- Quarterly compliance reviews verify retention settings against this document and update configs as needed.
