# Service Inventory

| Service | Role | Host | IP | Notes |
| --- | --- | --- | --- | --- |
| Proxmox VE | Hypervisor | proxmox-01/02/03 | 192.168.40.10-12 | 3-node HA cluster |
| TrueNAS | Storage | truenas-01 | 192.168.40.20 | ZFS + NFS + SMB |
| PBS | Backup | pbs-01 | 192.168.40.50 | Deduplicated backups |
| Pi-hole | DNS | lxc-pihole | 192.168.40.35 | Primary resolver |
| DHCP | DHCP | lxc-dhcp | 192.168.40.36 | ISC DHCP server |
| NTP | Time sync | lxc-ntp | 192.168.40.37 | Chrony/ntp |
| Step CA | Certificate authority | ca-01 | 192.168.40.38 | Internal PKI |
| Traefik | Reverse proxy | proxy-01 | 192.168.40.40 | TLS termination |
| Prometheus | Monitoring | monitoring-01 | 192.168.40.30 | Metrics + alerts |
| Grafana | Dashboards | monitoring-01 | 192.168.40.30 | Visualization |
