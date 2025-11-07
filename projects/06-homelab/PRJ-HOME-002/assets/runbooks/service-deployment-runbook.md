# Service Deployment Runbook - Proxmox Homelab

## Overview
**Purpose:** Deploy new service (VM or LXC container) on Proxmox  
**Environment:** Proxmox VE 8.x with TrueNAS storage  
**Estimated Time:** 1-2 hours  
**Risk Level:** Low to Medium

## Pre-Deployment Checklist

- [ ] Service requirements documented
- [ ] Resource requirements determined (CPU, RAM, Storage)
- [ ] VLAN assignment decided
- [ ] Static IP or DHCP reservation planned
- [ ] Backup strategy defined
- [ ] Monitoring metrics identified

## Decision: VM or LXC Container?

**Use LXC Container when:**
- Running Linux-based service
- Want minimal resource overhead
- Don't need kernel customization
- Service is well-containerized

**Use VM when:**
- Running Windows or non-Linux OS
- Need kernel isolation
- Service requires specific kernel modules
- Maximum compatibility needed

---

## Procedure: Deploy LXC Container (Recommended)

### Step 1: Create Container
```bash
# SSH into Proxmox host
ssh root@192.168.10.10

# Create LXC container
pct create 200 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname my-service \
  --cores 2 \
  --memory 2048 \
  --swap 1024 \
  --rootfs local-zfs:8 \
  --net0 name=eth0,bridge=vmbr0,ip=192.168.10.50/24,gw=192.168.10.1,tag=10 \
  --nameserver 192.168.10.2 \
  --searchdomain homelab.local \
  --unprivileged 1 \
  --start 1
```

**Parameters Explained:**
- `200`: Container ID (100-999 available)
- `--hostname`: DNS hostname
- `--cores`: CPU cores (start conservatively)
- `--memory`: RAM in MB
- `--rootfs local-zfs:8`: 8GB root filesystem on ZFS
- `--tag=10`: VLAN 10 (Trusted)
- `--unprivileged 1`: Security best practice

**Validation:**
- [ ] Container created successfully
- [ ] Container started
- [ ] Can ping gateway from container

### Step 2: Initial Configuration
```bash
# Enter container
pct enter 200

# Update system
apt update && apt upgrade -y

# Install essential tools
apt install -y curl wget vim htop net-tools

# Set timezone
timedatectl set-timezone America/Los_Angeles

# Configure auto-updates (security)
apt install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

**Validation:**
- [ ] System updated
- [ ] Tools installed
- [ ] Timezone correct

### Step 3: Install Application

**Example: Deploy Wiki.js**
```bash
# Install Docker (most services use Docker)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Create application directory
mkdir -p /opt/wikijs
cd /opt/wikijs

# Create docker-compose.yml
cat > docker-compose.yml << 'DOCKEREOF'
version: '3'
services:
  wiki:
    image: ghcr.io/requarks/wiki:2
    depends_on:
      - db
    environment:
      DB_TYPE: postgres
      DB_HOST: db
      DB_PORT: 5432
      DB_USER: wikijs
      DB_PASS: changeme
      DB_NAME: wiki
    restart: unless-stopped
    ports:
      - "3000:3000"
    volumes:
      - ./data:/wiki/data

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: wiki
      POSTGRES_USER: wikijs
      POSTGRES_PASSWORD: changeme
    logging:
      driver: "none"
    restart: unless-stopped
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
DOCKEREOF

# Start service
docker-compose up -d
```

**Validation:**
- [ ] Docker installed
- [ ] Containers running
- [ ] Service accessible on port 3000

### Step 4: Configure Reverse Proxy (Nginx Proxy Manager)

**Access Nginx Proxy Manager:**
1. Open http://192.168.10.25
2. Login with admin credentials
3. Add Proxy Host:
   - Domain: wiki.homelab.local
   - Forward to: 192.168.10.50:3000
   - Enable SSL (Let's Encrypt)
   - Force SSL

**Validation:**
- [ ] Reverse proxy configured
- [ ] https://wiki.homelab.local accessible
- [ ] SSL certificate valid

### Step 5: Configure Monitoring
```bash
# Install node exporter for Prometheus
docker run -d \
  --name=node-exporter \
  --restart=unless-stopped \
  -p 9100:9100 \
  prom/node-exporter
```

**Add to Prometheus targets (on monitoring server):**
```yaml
# Edit /opt/observability/prometheus/prometheus.yml
scrape_configs:
  - job_name: 'wikijs-host'
    static_configs:
      - targets: ['192.168.10.50:9100']
        labels:
          service: 'wikijs'
```

**Restart Prometheus:**
```bash
docker-compose restart prometheus
```

**Validation:**
- [ ] Node exporter accessible
- [ ] Prometheus scraping metrics
- [ ] Grafana showing data

### Step 6: Configure Backups

**Add to Proxmox Backup Server:**
```bash
# From Proxmox host
pvesh create /cluster/backup --vmid 200 --storage backup-pool --mode snapshot --compress zstd --dow mon,wed,fri --starttime 02:00
```

**Application data backup:**
```bash
# Inside container, create backup script
cat > /opt/backup.sh << 'BACKUPSCRIPT'
#!/bin/bash
DATE=$(date +%Y%m%d)
docker-compose -f /opt/wikijs/docker-compose.yml exec -T db pg_dump -U wikijs wiki > /backup/wiki-db-$DATE.sql
tar czf /backup/wiki-data-$DATE.tar.gz /opt/wikijs/data
# Sync to TrueNAS
rsync -av /backup/ /mnt/truenas/backups/wikijs/
BACKUPSCRIPT

chmod +x /opt/backup.sh

# Add to cron
echo "0 3 * * * /opt/backup.sh" | crontab -
```

**Validation:**
- [ ] PBS backup scheduled
- [ ] Application backup script created
- [ ] Cron job added
- [ ] Test backup manually

---

## Procedure: Deploy Virtual Machine

### Step 1: Create VM
```bash
# Download ISO to Proxmox
wget -O /var/lib/vz/template/iso/ubuntu-22.04-server.iso \
  https://releases.ubuntu.com/22.04/ubuntu-22.04.3-live-server-amd64.iso

# Create VM
qm create 300 \
  --name my-vm \
  --memory 4096 \
  --cores 2 \
  --net0 virtio,bridge=vmbr0,tag=10 \
  --scsihw virtio-scsi-pci \
  --scsi0 local-zfs:32 \
  --ide2 local:iso/ubuntu-22.04-server.iso,media=cdrom \
  --boot c --bootdisk scsi0 \
  --ostype l26 \
  --agent 1

# Start VM
qm start 300
```

### Step 2: Install OS
1. Access console via Proxmox web UI
2. Follow standard Ubuntu installation
3. Install qemu-guest-agent

```bash
# Inside VM after OS install
apt update
apt install -y qemu-guest-agent
systemctl enable qemu-guest-agent
systemctl start qemu-guest-agent
```

### Step 3: Configure (similar to LXC steps 2-6 above)

---

## Post-Deployment Validation

### Functionality Tests
- [ ] Service accessible via configured URL
- [ ] All features working as expected
- [ ] SSL certificate valid (if applicable)

### Performance Tests
- [ ] Response time < 500ms
- [ ] Resource usage within allocated limits
- [ ] No memory leaks observed (monitor over 24h)

### Security Tests
- [ ] Default passwords changed
- [ ] Firewall rules applied
- [ ] Service not accessible from incorrect VLANs
- [ ] Security scanning clean (optional: run vulnerability scan)

### Integration Tests
- [ ] Service registered in DNS (Pi-hole)
- [ ] Monitoring metrics flowing to Prometheus
- [ ] Backups successful
- [ ] Logs forwarded to Loki (optional)

---

## Rollback Procedure

**If deployment fails or service has issues:**

### For LXC Container
```bash
# Stop container
pct stop 200

# Delete container
pct destroy 200

# Clean up any external resources (DNS, monitoring, backups)
```

### For VM
```bash
# Stop VM
qm stop 300

# Delete VM
qm destroy 300
```

---

## Documentation Requirements

After successful deployment:
- [ ] Update asset inventory with new CT/VM
- [ ] Add to network diagram
- [ ] Document in wiki (service purpose, access, credentials)
- [ ] Update this runbook if new procedures learned

---

## Common Issues & Troubleshooting

### Issue: Container Won't Start
```bash
# Check logs
pct status 200
pct enter 200  # May fail if not started

# Check Proxmox logs
journalctl -u pve-container@200.service

# Common fix: resource limits
pct set 200 --memory 4096  # Increase RAM
```

### Issue: Can't Reach Service
```bash
# Check if container is running
pct status 200

# Check if service is listening
pct exec 200 -- netstat -tulpn | grep 3000

# Check firewall
# From trusted VLAN client
curl http://192.168.10.50:3000
```

### Issue: High Resource Usage
```bash
# Check resource usage
pct exec 200 -- top
pct exec 200 -- df -h

# Increase resources if needed
pct set 200 --memory 4096 --cores 4
pct reboot 200
```

---

## Service-Specific Examples

### Home Assistant Deployment
```bash
# Privileged container required for USB access
pct create 201 local:vztmpl/debian-11-standard_11.6-1_amd64.tar.zst \
  --hostname homeassistant \
  --cores 2 --memory 2048 \
  --rootfs local-zfs:8 \
  --net0 name=eth0,bridge=vmbr0,ip=192.168.50.10/24,gw=192.168.50.1,tag=50 \
  --unprivileged 0 \
  --features nesting=1 \
  --start 1

# Pass through USB Z-Wave stick
pct set 201 -mp0 /dev/ttyUSB0,mp=/dev/ttyUSB0
```

### Database Server Deployment
```bash
# Create VM with more RAM
qm create 302 --name postgres-db --memory 8192 --cores 4 \
  --net0 virtio,bridge=vmbr0,tag=10 \
  --scsi0 local-zfs:50 \
  --scsi1 local-zfs:100  # Separate disk for data

# Mount data disk
# Inside VM
mkfs.ext4 /dev/sdb
mkdir /var/lib/postgresql/data
echo "/dev/sdb /var/lib/postgresql/data ext4 defaults 0 2" >> /etc/fstab
mount -a
```

---

## Sign-Off Checklist
- [ ] Service deployed and tested
- [ ] Monitoring configured
- [ ] Backups scheduled and verified
- [ ] Documentation updated
- [ ] Firewall rules applied
- [ ] Security review completed
- [ ] Handoff to users (if applicable)

**Deployed by:** _________________  
**Date:** _________________  
**Service URL:** _________________  
**Notes:** _________________
