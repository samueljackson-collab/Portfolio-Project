# Configuration Files

This directory will contain configuration files and templates for all infrastructure components.

## Planned Contents

### Proxmox Configuration
- Host network interfaces and VLAN configuration
- VM and container definitions
- Backup schedules and retention policies
- HA cluster configuration (if applicable)

### TrueNAS Configuration
- ZFS pool and dataset definitions
- Snapshot policies and schedules
- NFS/SMB share configurations
- Backup replication settings

### Networking
- UniFi network configuration exports
- VLAN definitions and assignments
- Firewall rule sets
- WireGuard VPN peer configurations

### Services
- Nginx Proxy Manager host definitions
- Docker Compose files for all services
- Environment variable templates
- Service-specific configurations

### Monitoring Stack
- Prometheus scrape configurations and alerting rules
- Grafana dashboard JSON exports
- Loki pipeline configurations
- Alertmanager routing and notification settings

## Security Note

Actual configuration files containing sensitive information (passwords, API keys, certificates) are **not** included in this repository. This directory contains templates and sanitized examples for demonstration purposes.

---

**Status:** 📝 Documentation Pending
Configurations will be added as the infrastructure is deployed.
