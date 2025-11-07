# PRJ-HOME-002 Configuration Files
# ==================================

This directory contains configuration files for the virtualization and services infrastructure project.

## Directory Structure

```
configs/
├── README.md                           # This file
├── cloud-init/                         # VM provisioning templates
│   └── ubuntu-server-template.yaml    # Cloud-init configuration
├── docker-compose-*.yml                # Individual service compose files
├── docker-compose-full-stack.yml       # Complete stack deployment
├── nginx-proxy-manager/                # Reverse proxy configuration
│   └── proxy-hosts-example.json       # NPM export example
├── truenas/                            # Storage configuration
│   └── dataset-structure.md           # ZFS datasets and shares
├── proxmox/                            # Hypervisor configurations
│   └── (configs documented in parent README)
└── services/                           # Application-specific configs
    └── (service configs documented separately)
```

---

## Configuration Files

### Cloud-Init Templates

#### ubuntu-server-template.yaml
**Purpose:** Automated VM provisioning template for Proxmox cloud-init

**Features:**
- User creation with SSH key authentication
- Automatic package installation (Docker, monitoring tools)
- UFW firewall configuration
- SSH hardening (disable root, password-less)
- Automatic security updates
- Docker and Docker Compose setup
- Monitoring agents (node_exporter, Promtail)
- Network configuration (static IP, DNS, NTP)

**Usage:**
```bash
# Apply to Proxmox VM template
qm set 9000 --cicustom "user=local:snippets/ubuntu-server-template.yaml"

# Clone template with cloud-init
qm clone 9000 100 --name wikijs-production
qm set 100 --ipconfig0 ip=192.168.10.100/24,gw=192.168.10.1
qm start 100
```

**Variables to Replace:**
- `{{ hostname }}` - VM hostname
- `{{ ssh_public_key }}` - Your SSH public key
- `{{ ip_address }}` - Static IP address
- `{{ gateway }}` - Default gateway
- `{{ dns_server }}` - DNS server IP

**Post-Deployment:**
- VM boots with all packages installed
- Monitoring automatically integrates with Prometheus/Loki
- Backup job automatically configured
- Ready for application deployment in ~4 minutes

---

### Docker Compose Configurations

#### docker-compose-full-stack.yml
**Purpose:** Complete homelab services stack with monitoring

**Services Included:**
```
Reverse Proxy:
  - nginx-proxy-manager    :80, :443, :81

Monitoring:
  - prometheus             :9090
  - grafana                :3000
  - loki                   :3100
  - promtail               (log shipper)
  - alertmanager           :9093

Applications:
  - wikijs                 :3000
  - homeassistant          :8123
  - immich                 :2283

Infrastructure:
  - postgresql             :5432
  - redis                  :6379

Exporters:
  - cadvisor               :8080
  - node-exporter          :9100
```

**Networks:**
- `frontend`: Public-facing services (Nginx, Grafana)
- `backend`: Internal services (databases, apps)
- `monitoring`: Observability stack (Prometheus, Loki)

**Usage:**
```bash
# Create .env file with credentials
cat > .env <<EOF
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=secure_password
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=homelab
EOF

# Start all services
docker-compose -f docker-compose-full-stack.yml up -d

# View logs
docker-compose -f docker-compose-full-stack.yml logs -f

# Stop services
docker-compose -f docker-compose-full-stack.yml down
```

**Data Persistence:**
- All services use named volumes
- Volumes can be backed up with docker volume commands
- Consider NFS mounts for production

**Health Checks:**
- All services include health check endpoints
- Automatic restart on failure
- Integration with Docker health status

---

### Nginx Proxy Manager

#### proxy-hosts-example.json
**Purpose:** Reverse proxy configuration for homelab services

**Features:**
- Automatic SSL with Let's Encrypt
- WebSocket support for Home Assistant, Grafana
- Access control lists (authentication)
- Custom headers and advanced configs
- Wildcard certificate support

**Proxy Hosts:**
- `wiki.example.com` → Wiki.js (192.168.10.100:3000)
- `homeassistant.example.com` → Home Assistant (192.168.10.101:8123)
- `photos.example.com` → Immich (192.168.10.102:2283)
- `grafana.example.com` → Grafana (192.168.10.103:3000)
- `prometheus.example.com` → Prometheus (admin only)

**Usage:**
1. **Export from NPM:** Settings > Backup
2. **Edit template:** Replace example.com with your domain
3. **Import to NPM:** Settings > Restore
4. **Verify certificates:** Check SSL status in NPM

**Security Features:**
- Force HTTPS (automatic redirect)
- HSTS headers
- Block common exploits
- HTTP/2 support
- Access lists for sensitive services

---

### TrueNAS Configuration

#### dataset-structure.md
**Purpose:** ZFS dataset hierarchy and share configuration

**Dataset Categories:**
```
tank/
├── backups/       - Proxmox Backup Server, workstation backups
├── media/         - Photos, videos, music libraries
├── shares/        - General file shares (home dirs, documents)
├── services/      - Service data volumes (Docker, databases)
└── iso/           - ISO images for VM templates
```

**Export Methods:**
- **NFS:** For Linux clients, Proxmox nodes (high performance)
- **SMB/CIFS:** For Windows clients, general file sharing
- **iSCSI:** For high-performance VM storage (optional)

**Snapshot Strategy:**
- **backups/**: Hourly(24), Daily(7), Weekly(4), Monthly(3)
- **services/**: Hourly(24), Daily(7), Weekly(4), Monthly(3)
- **media/**: Daily(7), Weekly(4), Monthly(3)
- **shares/**: Hourly(24), Daily(7), Weekly(4)

**Replication:**
- Daily offsite replication for critical datasets
- 7-day retention on remote backup NAS
- Encrypted transport via SSH

---

## Environment Variables

### Required Variables (.env)

```bash
# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=change_me_secure_password

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change_me_secure_password
POSTGRES_DB=homelab

# Timezone
TZ=America/Los_Angeles

# Optional: Email for Let's Encrypt
LETSENCRYPT_EMAIL=admin@example.com
```

---

## Security Considerations

### Secrets Management
- **Never commit .env files** (in .gitignore)
- Use strong, unique passwords
- Rotate credentials regularly
- Consider using Docker secrets or HashiCorp Vault

### Network Security
- Services on backend network not directly accessible
- Reverse proxy with SSL for external access
- Consider VPN for sensitive services
- Use access lists for admin interfaces

### Firewall Rules
- Allow only necessary ports
- Block direct database access from outside
- Use VLANs for network segmentation
- Monitor connection attempts

---

## Backup Strategy

### Configuration Backups
```bash
# Backup Docker volumes
docker run --rm \
  -v prometheus_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/prometheus_backup.tar.gz /data

# Backup Nginx Proxy Manager
# Settings > Backup > Download

# Backup cloud-init templates
cp /var/lib/vz/snippets/*.yaml ~/backups/
```

### Restore Procedures
```bash
# Restore Docker volume
docker volume create prometheus_data
docker run --rm \
  -v prometheus_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/prometheus_backup.tar.gz -C /
```

---

## Troubleshooting

### Common Issues

**Services won't start:**
```bash
# Check Docker logs
docker-compose logs service_name

# Check for port conflicts
sudo netstat -tlnp | grep :PORT

# Verify volumes
docker volume ls
docker volume inspect volume_name
```

**Cloud-init not applying:**
```bash
# Check cloud-init logs on VM
sudo cat /var/log/cloud-init.log
sudo cloud-init status

# Verify configuration
qm config VM_ID | grep cicustom
```

**Network connectivity issues:**
```bash
# Verify bridge networks
docker network ls
docker network inspect network_name

# Check DNS resolution
docker exec container_name nslookup google.com
```

---

## Maintenance

### Regular Tasks
- **Weekly:** Review logs for errors
- **Monthly:** Update Docker images
- **Quarterly:** Test backup restores
- **Annually:** Rotate secrets and credentials

### Updates
```bash
# Pull latest images
docker-compose -f docker-compose-full-stack.yml pull

# Restart services
docker-compose -f docker-compose-full-stack.yml up -d

# Cleanup old images
docker image prune -a
```

---

## Related Documentation

- **Parent README:** `../README.md`
- **Deployment Guide:** `../docs/deployment-runbook.md`
- **Disaster Recovery:** `../recovery/disaster-recovery-plan.md`
- **Monitoring:** `../../PRJ-SDE-002/assets/README.md`

---

## Best Practices

1. **Test in Development First:** Always test config changes in dev environment
2. **Version Control:** Keep configs in git, use branches for changes
3. **Document Changes:** Update this README when adding new configs
4. **Validate Syntax:** Use linters (yamllint, jsonlint) before deploying
5. **Backup Before Changes:** Always backup working configs before modifications
6. **Monitor After Deploy:** Check metrics and logs after configuration changes

---

**Last Updated:** 2024-11-06
**Maintained By:** Homelab Infrastructure Team
