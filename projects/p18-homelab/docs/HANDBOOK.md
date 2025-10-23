# P18 · Homelab Infrastructure — Planning Handbook

This handbook documents the architecture and operating model for the homelab that mirrors the
production landing zone.

## 1. Objectives
- Provide isolated VLANs for trusted, IoT, lab, and guest networks.
- Run Proxmox VE cluster with high-availability storage backed by TrueNAS.
- Expose core services (reverse proxy, identity, monitoring) with automated backups.
- Serve as integration sandbox for IaC modules and security policies before production rollout.

## 2. Hardware Inventory
| Component | Quantity | Notes |
| --- | --- | --- |
| Supermicro E300-9A | 3 | Proxmox cluster nodes (32 GB RAM, 1 TB NVMe each) |
| TrueNAS Mini X+ | 1 | 32 TB usable storage, SSD cache |
| UniFi Dream Machine SE | 1 | Routing, firewall, VPN concentrator |
| UniFi Switch Pro 24 PoE | 1 | VLAN tagging, PoE for APs |
| UniFi U6-Pro AP | 2 | Wi-Fi coverage for home + office |

## 3. Network Topology
- **VLAN 10 (Trusted):** Admin workstations, management interfaces.
- **VLAN 20 (Lab):** Proxmox hosts, Kubernetes cluster.
- **VLAN 30 (IoT):** Smart devices, isolated from trusted networks.
- **VLAN 40 (Guest):** Internet-only access.
- **VLAN 50 (Services):** Reverse proxy, identity provider, monitoring.

Routing handled by UDM-SE; inter-VLAN firewall rules restrict traffic to least privilege. Site-to-site
WireGuard tunnels connect to cloud environments for hybrid testing.

## 4. Core Services
- **Identity:** Keycloak with LDAP bridge to local Active Directory.
- **Reverse Proxy:** Traefik with Let's Encrypt DNS challenges (Cloudflare).
- **Monitoring:** Prometheus + Grafana + Loki stack (mirrors P20 observability).
- **Backups:** Proxmox Backup Server replicating to TrueNAS snapshot dataset.
- **Automation:** Ansible playbooks (see `projects/p18-homelab/automation/ansible/`).

## 5. Security Controls
- VLAN isolation with firewall rules default-deny between segments.
- mTLS between services using internal CA managed via Smallstep.
- Secrets stored in Vault; SSH access gated via short-lived certificates.
- Continuous vulnerability scans using OpenVAS container on lab network.

## 6. Monitoring & Alerting
- Metrics scraped by Prometheus, visualised via Grafana dashboard `Homelab-Overview`.
- Loki collects logs from Proxmox, TrueNAS, and containers via Promtail.
- Alertmanager routes P1/P2 incidents to on-call phone, P3 to email digest.

## 7. Backup Strategy
- Nightly VM snapshots with 14-day retention.
- Weekly off-site replication to encrypted S3 bucket (rclone job from TrueNAS).
- Monthly full configuration backup exported to `documentation/homelab/backups/`.

## 8. Roadmap
1. Add UPS monitoring integration for graceful shutdowns.
2. Deploy Kubernetes (k3s) on VLAN 20 with GitOps managed workloads.
3. Integrate Home Assistant automations with security monitoring feeds.
