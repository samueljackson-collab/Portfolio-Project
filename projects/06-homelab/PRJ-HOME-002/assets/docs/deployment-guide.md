# Deployment Guide

This guide documents how the Virtualization & Core Services stack is deployed on Proxmox VE with TrueNAS-backed storage and Docker-based services.

## Prerequisites
- Proxmox VE cluster with shared Ceph or TrueNAS storage accessible on VLAN 40.
- Proxmox Backup Server datastore mounted at `/mnt/pbs` (NFS) or local datastore.
- Management workstation with Ansible, Terraform, and `pvesh` CLI access.
- DNS entries in Cloudflare for external access (sanitized to `example.com`).
- TLS certificates issued via Let's Encrypt or imported wildcard certs.

## High-Level Flow
1. Build or refresh cloud-init VM templates on Proxmox.
2. Provision VMs for core services (Wiki.js, Home Assistant, Immich, PostgreSQL, Nginx Proxy Manager).
3. Attach storage (Ceph RBD, LVM-thin, or NFS from TrueNAS) based on workload tier.
4. Deploy service stacks using Docker Compose definitions in `assets/configs/`.
5. Apply reverse proxy definitions (Nginx Proxy Manager) and validate TLS issuance.
6. Register systems with monitoring (Prometheus/Grafana) and logging (Loki/Promtail).
7. Configure scheduled backups (Proxmox Backup Server + TrueNAS snapshots/replication).

## Proxmox Provisioning
- Templates and sample configs live in `../proxmox/`.
- Use `vm-templates/create-ubuntu-template.sh` to build the base template (ID 9000) with cloud-init.
- Apply `vm-templates/cloud-init-config.yml` for hostname, IP, SSH key, and initial packages.
- Networking is defined in `proxmox/network-interfaces` with a bonded uplink and VLAN 40 bridge.

### Example VM Creation
```bash
# Clone template for Wiki.js
qm clone 9000 110 --name wikijs-prod --full --storage ceph-rbd
qm set 110 --memory 8192 --cores 4 --ipconfig0 ip=192.168.40.20/24,gw=192.168.40.1
qm set 110 --nameserver 192.168.40.35 --searchdomain homelab.local
qm set 110 --sshkey ~/.ssh/id_rsa.pub
qm start 110
```

### Storage Selection
- **Ceph RBD:** HA workloads (Wiki.js, Home Assistant, PostgreSQL) supporting live migration.
- **Local LVM-thin:** Non-HA or lab workloads where performance is key.
- **TrueNAS NFS/iSCSI:** Capacity-heavy data (Immich library) or backup datastores.

## Docker Compose Deployment
- Definitions live in `../configs/` (sanitized for sharing).
- Choose a host (VM/LXC) with Docker installed and copy relevant compose file(s):
  - `docker-compose-wikijs.yml`
  - `docker-compose-homeassistant.yml`
  - `docker-compose-immich.yml`
  - `docker-compose-postgresql.yml`
  - `docker-compose-nginx-proxy-manager.yml`
  - `docker-compose-full-stack.yml` (all services together)

### Example: Start Wiki.js
```bash
cd /opt/stacks/wikijs
cp /repo/projects/06-homelab/PRJ-HOME-002/assets/configs/docker-compose-wikijs.yml docker-compose.yml
cp /repo/projects/06-homelab/PRJ-HOME-002/assets/configs/example.env .env
# Update .env with sanitized values before running
sudo docker compose pull
sudo docker compose up -d
```

### Health Checks
- Wiki.js: `curl -I http://localhost:3000`
- Home Assistant: `curl -I http://localhost:8123`
- Immich: `curl -I http://localhost:2283`
- PostgreSQL: `psql -h localhost -U postgres -c "select now();"`

## Nginx Proxy Manager
- Import sanitized config from `../configs/nginx-proxy-manager/proxy-hosts-example.json`.
- Validate DNS challenge credentials are redacted and replaced with environment variables.
- Confirm forced SSL and HSTS are enabled for all proxy hosts.

## Monitoring & Logging
- Prometheus/Grafana stack runs in CT 200; ensures each VM exposes `node_exporter` on `:9100`.
- Loki/Promtail agents forward logs from services; verify pipeline via Grafana Explore.
- Enable Proxmox metrics target (`:9221`) to capture host health.

## Backup Configuration
- Proxmox Backup Server job set uses `assets/proxmox/backup-config.json` for schedules.
- TrueNAS snapshot and replication policies detailed in `../configs/truenas/dataset-structure.md`.
- Verify backup completion via PBS dashboard and in `assets/logs/backup-rotation.log`.

## Acceptance Checklist
- [ ] All VMs reachable over VLAN 40 with correct DNS records.
- [ ] Services responding locally and through Nginx Proxy Manager.
- [ ] TLS certificates issued and renewing (Let's Encrypt HTTP-01 or DNS-01).
- [ ] Monitoring dashboards populated; alerting rules firing from `configs/monitoring/`.
- [ ] Backup jobs completed successfully with retention verified.
- [ ] Documentation updated with any deviations from defaults.
