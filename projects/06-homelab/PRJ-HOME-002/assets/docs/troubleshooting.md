# Troubleshooting Guide

Use this guide to quickly isolate and resolve common issues across the Proxmox cluster and core services.

## Proxmox & Ceph
- **VMs not migrating**: Verify shared storage availability with `pvesm status`; ensure HA group membership for affected VMs.
- **Ceph warnings**: Run `ceph health detail` to pinpoint failed OSDs or placement groups. Rebalance with `ceph osd reweight-by-utilization` after recovery.
- **API unreachable**: Check `pveproxy` service and firewall rules; confirm certificates are valid in `/etc/pve/local/pveproxy-ssl.pem`.

## Networking & DNS
- **DNS failures**: Ensure Pi-hole is reachable at `192.168.40.35` and upstream forwarders respond. Reload configs from `assets/services/pihole/pihole-config.conf`.
- **Proxy timeouts**: Confirm backend health via `curl -k https://<service-ip>` and validate mappings in `assets/configs/nginx-proxy-manager/proxy-hosts.yml`.
- **NTP drift**: Verify NTP server status with `ntpq -p` and restart the service using `assets/services/ntp/ntp.conf` as the source of truth.

## Applications
- **Wiki.js login errors**: Check PostgreSQL container in `docker-compose-postgresql.yml` and confirm `NODE_EXTRA_CA_CERTS` points to the internal CA.
- **Home Assistant automations**: Validate MQTT broker connectivity and reload configuration from `docker-compose-homeassistant.yml`.
- **Immich media uploads**: Ensure object storage paths match the TrueNAS share defined in `assets/configs/truenas/share-definitions.yml`.

## Monitoring & Logs
- **Prometheus targets down**: Compare scrape URLs with `assets/configs/monitoring/prometheus/prometheus.yml`; verify firewall rules allow node exporter ports.
- **Centralized logs missing**: Confirm Rsyslog listener on TCP/UDP 514 using `assets/services/rsyslog/rsyslog.conf`; check that Proxmox and TrueNAS forwarders are enabled.
- **Backup alerts**: Inspect PBS jobs via `journalctl -u proxmox-backup` and correlate with `assets/logs/backup-job-log.md` for recent runs.

## Escalation
- Capture diagnostics (`pveversion -v`, `ceph report`, `docker-compose ps`) and attach to the incident ticket.
- If production services are impacted, trigger DR steps from `assets/docs/disaster-recovery.md` after obtaining approvals.
