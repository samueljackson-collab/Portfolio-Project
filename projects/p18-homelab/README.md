# P18 · Homelab Infrastructure

**Status:** 🔵 Planned  
**Objective:** Build an enterprise-grade homelab featuring Proxmox virtualization, segmented networking, centralized auth, and observability to mirror production patterns.

---
## 🌐 Scope
- Rack-mounted hardware with redundant power, UPS, and out-of-band management.  
- Proxmox VE cluster with high-availability storage (Ceph/TrueNAS).  
- Network segmentation via UniFi switches, VLANs, and site-to-site VPN.  
- Core services: reverse proxy (Traefik), SSO (Authelia), monitoring (Prometheus/Grafana), backups (Proxmox Backup Server).  

---
## 📚 Planned Documentation
| Artifact | Description |
| --- | --- |
| docs/HANDBOOK.md | Reference architecture, bill of materials, wiring diagrams, service inventory. |
| docs/RUNBOOK.md | Operations cadence, maintenance windows, backup verification. |
| docs/PLAYBOOK.md | Incident response for hardware failure, storage degradation, and network outages. |

