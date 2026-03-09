# Deployment Procedures - Proxmox Homelab

## 1. Bootstrap Proxmox Cluster
1. Install Proxmox VE 8.x on each node.
2. Apply `assets/proxmox/network-interfaces` and reboot.
3. Create cluster on proxmox-01:
   ```bash
   pvecm create homelab-cluster
   ```
4. Join additional nodes:
   ```bash
   pvecm add 192.168.40.10
   ```

## 2. Configure Storage
1. Apply `assets/proxmox/storage.cfg` on each node.
2. Mount TrueNAS exports (NFS/iSCSI).
3. Verify PBS storage credentials and fingerprint.

## 3. Build VM Templates
1. Run template scripts:
   ```bash
   ./assets/proxmox/vm-templates/create-ubuntu-template.sh
   ./assets/proxmox/vm-templates/create-debian-template.sh
   ./assets/proxmox/vm-templates/create-rockylinux-template.sh
   ```
2. Upload cloud-init snippets from `assets/configs/cloud-init/`.

## 4. Provision Infrastructure as Code
1. Initialize Terraform in `assets/automation/terraform`.
2. Apply infrastructure:
   ```bash
   terraform init
   terraform apply
   ```

## 5. Configure Core Services
1. Deploy Pi-hole, NTP, DHCP, and Step CA configs.
2. Deploy Traefik reverse proxy (docker-compose).
3. Validate DNS + TLS issuance.

## 6. Enable Monitoring
1. Deploy Prometheus, Alertmanager, and Grafana.
2. Add Proxmox exporter and SNMP exporter configs.
3. Verify targets are up in Prometheus.
