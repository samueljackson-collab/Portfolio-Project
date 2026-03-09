# Deployment Guide

This guide describes how to deploy the Virtualization & Core Services stack, including Proxmox, TrueNAS-backed storage, core infrastructure services, and application containers.

## Prerequisites
- Three Proxmox VE nodes with management network on `192.168.40.0/24`.
- TrueNAS system reachable on dedicated storage VLAN with NFS and iSCSI enabled.
- DNS entries created in Pi-hole for all services (e.g., `proxmox.example.com`, `wiki.example.com`).
- Ansible control node with SSH access to Proxmox and VMs.
- Terraform installed with access to the Proxmox API and state backend configured in `assets/automation/terraform/backend.tf`.

## High-Level Sequence
1. **Bootstrap Cluster**: Install Proxmox VE, apply `assets/proxmox/network-interfaces`, and create the cluster via `pvecm create`/`pvecm add`.
2. **Attach Storage**: Configure Ceph using `assets/proxmox/cluster.conf` and add TrueNAS-backed NFS/iSCSI targets as described in `assets/configs/truenas/dataset-layout.md`.
3. **Publish Templates**: Run `assets/proxmox/vm-templates/create-ubuntu-template.sh` to generate the base cloud-init image with QEMU guest agent enabled.
4. **Provision VMs**: Apply Terraform (`assets/automation/terraform/main.tf`) to create FreeIPA, Pi-hole, Nginx, Rsyslog, Home Assistant, Immich, and Wiki.js VMs.
5. **Configure Services**: Execute Ansible playbooks from `assets/automation/ansible/playbooks/` to install service packages and push configs in `assets/services/`.
6. **Deploy Containers**: Use the Docker Compose bundles in `assets/configs/` for application services, starting with PostgreSQL then Wiki.js, Home Assistant, and Immich.
7. **Front Door**: Import sanitized Nginx Proxy Manager host entries from `assets/configs/nginx-proxy-manager/proxy-hosts.yml` to expose services with TLS.
8. **Monitoring**: Apply Prometheus/Loki stack configs from `assets/configs/monitoring/` and add targets for Proxmox, PBS, and TrueNAS.
9. **Backups**: Configure backup jobs using `assets/proxmox/backup-config.json` and verify retention with the steps in `assets/docs/backup-strategy.md`.

## Validation Checklist
- Cluster quorum healthy and Ceph status `HEALTH_OK`.
- Templates available and Terraform outputs list all service IPs.
- Ansible run completes without changes on second pass (idempotent).
- Reverse proxy resolves to expected backends with valid TLS.
- Monitoring dashboards show node metrics, VM metrics, and backup job results.
