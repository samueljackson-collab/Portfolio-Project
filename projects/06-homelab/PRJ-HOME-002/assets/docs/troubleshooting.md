# Troubleshooting Guide

This guide captures common issues observed in PRJ-HOME-002 and the steps to remediate them. All examples are sanitized.

## Proxmox & Virtualization
### Symptom: VM fails to start after migration
- **Check:** `journalctl -xeu pvedaemon` on target node.
- **Fix:** Ensure storage is shared (Ceph or NFS). Update VM disk location with `qm rescan --vmid <id>` if stale.
- **Prevent:** Keep storage definitions in sync with `proxmox/storage.cfg` and run `pvecm updatecerts` monthly.

### Symptom: Ceph showing `HEALTH_WARN`
- **Check:** `ceph -s` and Grafana Ceph dashboard.
- **Fix:** Confirm all OSDs are in/out; repair flapping OSDs, rebalance with `ceph osd reweight`.
- **Prevent:** Avoid maintenance during rebalance; enforce replication=3 from `configs/truenas/dataset-structure.md` guidance.

## Network & Proxy
### Symptom: Service unreachable via external domain
- **Check:** DNS records at Cloudflare are proxied and pointing to WAN IP; validate `curl -I https://service.example.com`.
- **Fix:** Re-import sanitized Nginx Proxy Manager config; confirm certificate present; open port forward 80/443 on firewall.
- **Prevent:** Use `assets/configs/nginx-proxy-manager/proxy-hosts-example.json` as golden config and test renewals monthly.

### Symptom: HA VLAN devices lose DHCP
- **Check:** Bridge tagging on Proxmox `vmbr0.40`; verify UDM VLAN scope.
- **Fix:** Restart `systemctl restart networking` on host; re-apply `proxmox/network-interfaces` baseline.
- **Prevent:** Document changes in `docs/lessons-learned.md` and keep versioned network configs in Git.

## Services
### Symptom: Home Assistant UI sluggish
- **Check:** CPU usage inside VM; database bloat in PostgreSQL.
- **Fix:** Vacuum database weekly, archive recorder data older than 30 days; allocate extra vCPU/memory if sustained.
- **Prevent:** Move long-term metrics to external TSDB; confirm docker compose limits in `configs/docker-compose-homeassistant.yml`.

### Symptom: Immich upload failures
- **Check:** Reverse proxy upload limits; `docker logs immich-server`.
- **Fix:** Ensure `client_max_body_size` set in Nginx (see compose file) and NFS mount from TrueNAS is healthy.
- **Prevent:** Run `zpool status` on TrueNAS monthly; alert when pool usage > 80%.

### Symptom: Wiki.js cannot send email
- **Check:** SMTP credentials in `.env`; outbound firewall rules.
- **Fix:** Update sanitized `.env` from `configs/example.env`; allow SMTP outbound on firewall for VM.
- **Prevent:** Use per-app API tokens; rotate quarterly.

## Backups & DR
### Symptom: PBS job failed
- **Check:** `assets/logs/backup-rotation.log` and PBS UI.
- **Fix:** Confirm datastore reachable (TrueNAS NFS path), clear old snapshots if quota reached.
- **Prevent:** Enforce retention noted in `docs/backup-strategy.md`; run `backup-verify.sh` nightly.

### Symptom: Restore slow or stuck
- **Check:** Target storage throughput; network between PBS and PVE.
- **Fix:** Restore to local LVM then migrate to Ceph; avoid dedupe rehydration on busy hours.
- **Prevent:** Schedule large restores off-peak; maintain 20% free space on datastores.

## Observability
### Symptom: Metrics missing in Grafana
- **Check:** Prometheus scrape config (`configs/monitoring/README.md`) and `node_exporter` status.
- **Fix:** Restart Prometheus container; verify firewall rules allow `:9100`.
- **Prevent:** Add scrape job tests in CI; alert when target down for >5m.

### Symptom: Loki ingestion errors
- **Check:** Promtail logs on VMs; Loki retention settings.
- **Fix:** Adjust rate limits; re-apply `configs/monitoring/README.md` guidance; ensure disk not full.
- **Prevent:** Enforce log rotation and size caps per `docs/backup-strategy.md`.
