# Lessons Learned

Documenting operational insights from PRJ-HOME-002 deployments, DR tests, and day-2 operations.

## Architecture
- Ceph replication factor of 3 provided headroom during node maintenance; live migrations stayed under 90 seconds.
- VLAN isolation (40 for core services, 50 for management) simplified firewall policy but required explicit trunking on vmbr0.
- Running Nginx Proxy Manager as a dedicated VM avoided container host dependency on app VMs.

## Deployment
- Cloud-init templates drastically reduced provisioning time (4 minutes vs. 30+ manually). Ensure templates are rebuilt quarterly to capture kernel/security updates.
- Docker Compose `.env` separation prevented secrets from entering Git; sanitize example env files to keep onboarding smooth.
- Using `docker-compose-full-stack.yml` is convenient for labs but production prefers per-service compose files for fault isolation.

## Storage & Backups
- TrueNAS snapshots plus PBS backups provided quick restore options; replicating critical datasets offsite once weekly covers RPO=24h.
- Immich benefited from NFS cache tuning; enabling `actimeo=2` reduced UI latency during photo browsing.
- Ceph health warnings during backup windows correlated with PBS bandwidth spikes; rate-limit PBS tasks if replication backlog grows.

## Monitoring & Troubleshooting
- Grafana alerting on `node_exporter` loss helped catch a VLAN tag change before it impacted users.
- Promtail needed explicit Docker journald mounts on systemd hosts; missing mount caused silent log drops.
- Home Assistant slowdowns were usually PostgreSQL bloat; regular vacuum and partitioning keep it healthy.

## DR Exercises
- Test restores to isolated VM IDs (2xx) avoid clashing with production HA groups.
- DNS TTL at 60 seconds enabled quick failover to standby proxy; Cloudflare API tokens must be scoped narrowly.
- Maintaining USB installers for Proxmox/TrueNAS saved time during simulated site rebuild.

## Action Items
- [ ] Add automated Ceph bench tests monthly.
- [ ] Integrate PBS restore tests into CI runner.
- [ ] Document Zigbee/Z-Wave passthrough nuances for future hardware refresh.
