# Runbook: Deploy New Service to Homelab

## Purpose
Deploy a new containerized or VM-based service to the Proxmox homelab with proper networking, storage, backups, and monitoring.

## When to Use
- Adding new self-hosted application (Wiki, monitoring tool, database, etc.)
- Testing new software in isolated environment
- Deploying production-ready service for homelab use

## Prerequisites

### Required Access
- Proxmox VE web interface (https://192.168.40.10:8006)
- TrueNAS web interface (https://192.168.40.20)
- Nginx Proxy Manager (https://192.168.40.50:81)
- SSH access to Proxmox host

### Required Tools
- Web browser with homelab network access
- SSH client (Terminal, PuTTY)
- Text editor for configuration files

### Required Information
- Service name and description
- Resource requirements (CPU, RAM, storage)
- Network requirements (ports, VLAN assignment)
- Domain name for reverse proxy (e.g., `service.homelab.local`)

### Time Required
- LXC Container: 15-30 minutes
- Full VM: 30-60 minutes
- Complex multi-container: 1-2 hours

### Skill Level
Intermediate - Requires basic Linux and networking knowledge

---

## Pre-Deployment Checklist

Before starting, verify:

- [ ] Service requirements documented (resources, ports, dependencies)
- [ ] VMID/Container ID available (check Proxmox inventory)
- [ ] Storage capacity available on TrueNAS (min 10% free recommended)
- [ ] Network port not in use (check firewall rules)
- [ ] DNS name decided and available
- [ ] Backup strategy planned (daily/weekly/retention)

---

## Procedure

### Step 1: Create Storage on TrueNAS

**Goal:** Provision dedicated ZFS dataset for service data persistence

**Commands:**
```bash
# SSH to TrueNAS
ssh root@192.168.40.20

# Create ZFS dataset
zfs create pool1/appdata/[SERVICE_NAME]

# Set permissions
chown -R 1000:1000 /mnt/pool1/appdata/[SERVICE_NAME]
chmod 770 /mnt/pool1/appdata/[SERVICE_NAME]

# Verify dataset creation
zfs list | grep [SERVICE_NAME]
```

**Expected Output:**
```
pool1/appdata/[SERVICE_NAME]  31.0K  1.23T  31.0K  /mnt/pool1/appdata/[SERVICE_NAME]
```

**Validation:**
- [ ] Dataset appears in `zfs list`
- [ ] Correct permissions set (770)
- [ ] Parent directory is `/mnt/pool1/appdata/`

**If this fails:**
- Check pool capacity: `zpool list`
- Verify naming convention: lowercase, no special characters
- See [Troubleshooting](#troubleshooting-issue-1-dataset-creation-fails)

---

### Step 2: Create LXC Container or VM

#### Option A: LXC Container (Recommended for most services)

**Goal:** Create lightweight container for service deployment

**Commands:**
```bash
# SSH to Proxmox host
ssh root@192.168.40.10

# Download Ubuntu template if not present
pveam update
pveam download local ubuntu-22.04-standard_22.04-1_amd64.tar.zst

# Create LXC container
pct create [VMID] local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname [SERVICE_NAME] \
  --cores 2 \
  --memory 4096 \
  --swap 512 \
  --storage local-zfs \
  --rootfs local-zfs:32 \
  --net0 name=eth0,bridge=vmbr0,tag=40,ip=192.168.40.[IP]/24,gw=192.168.40.1 \
  --nameserver 192.168.40.1 \
  --features nesting=1 \
  --unprivileged 1 \
  --onboot 1

# Expected output:
# Creating container...
# Container created with ID [VMID]
```

**Start container:**
```bash
pct start [VMID]

# Verify container is running
pct status [VMID]
# Expected: status: running
```

**Initial container setup:**
```bash
# Enter container
pct enter [VMID]

# Update system
apt update && apt upgrade -y

# Install essential tools
apt install -y curl wget git vim htop

# Exit container
exit
```

#### Option B: Full VM (For services requiring kernel modules or Docker)

**Goal:** Create full virtual machine with complete OS

**Commands:**
```bash
# Create VM
qm create [VMID] \
  --name [SERVICE_NAME] \
  --memory 4096 \
  --cores 2 \
  --net0 virtio,bridge=vmbr0,tag=40 \
  --scsihw virtio-scsi-pci \
  --scsi0 local-zfs:32 \
  --ide2 local:iso/ubuntu-22.04-server-amd64.iso,media=cdrom \
  --boot order=scsi0 \
  --ostype l26 \
  --agent enabled=1 \
  --onboot 1

# Start VM and install OS via console
qm start [VMID]

# Open console
qm terminal [VMID]
```

**Validation:**
- [ ] Container/VM created successfully
- [ ] Status shows "running"
- [ ] Network connectivity verified (ping 1.1.1.1)
- [ ] Correct VLAN assignment (VLAN 40)

---

### Step 3: Mount TrueNAS Storage

**Goal:** Attach persistent storage from TrueNAS via NFS

**Create NFS share on TrueNAS:**
```bash
# On TrueNAS web UI:
# 1. Sharing → Unix (NFS) → Add
# 2. Path: /mnt/pool1/appdata/[SERVICE_NAME]
# 3. Authorized Networks: 192.168.40.0/24
# 4. Mapall User: root
# 5. Mapall Group: root
# 6. Save and enable service
```

**Mount NFS in container:**
```bash
# Enter container
pct enter [VMID]

# Install NFS client
apt install -y nfs-common

# Create mount point
mkdir -p /mnt/appdata

# Test mount
mount -t nfs 192.168.40.20:/mnt/pool1/appdata/[SERVICE_NAME] /mnt/appdata

# Verify mount
df -h | grep appdata
# Expected: 192.168.40.20:/mnt/pool1/appdata/[SERVICE_NAME]  1.2T  100G  1.1T   9% /mnt/appdata
```

**Make mount permanent:**
```bash
# Add to /etc/fstab
echo "192.168.40.20:/mnt/pool1/appdata/[SERVICE_NAME] /mnt/appdata nfs defaults,_netdev 0 0" >> /etc/fstab

# Verify fstab syntax
mount -a

# Exit container
exit
```

**Validation:**
- [ ] NFS share created on TrueNAS
- [ ] Mount successful
- [ ] Data persists after container restart
- [ ] Mount listed in fstab

---

### Step 4: Deploy Application

**Goal:** Install and configure the target service

**Example: Deploy Wiki.js (Node.js application)**

```bash
# Enter container
pct enter [VMID]

# Install Node.js and PostgreSQL
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs postgresql postgresql-contrib

# Create Wiki.js database
sudo -u postgres psql << EOF
CREATE DATABASE wikijs;
CREATE USER wikijs WITH ENCRYPTED PASSWORD 'SECURE_PASSWORD_HERE';
GRANT ALL PRIVILEGES ON DATABASE wikijs TO wikijs;
\q
EOF

# Install Wiki.js
mkdir -p /opt/wikijs
cd /opt/wikijs
wget https://github.com/Requarks/wiki/releases/download/2.5.300/wiki-js.tar.gz
tar xzf wiki-js.tar.gz
rm wiki-js.tar.gz

# Configure Wiki.js
cp config.sample.yml config.yml
vim config.yml
# Update:
#   db:
#     type: postgres
#     host: localhost
#     port: 5432
#     user: wikijs
#     pass: SECURE_PASSWORD_HERE
#     db: wikijs
#   dataPath: /mnt/appdata

# Create systemd service
cat > /etc/systemd/system/wikijs.service << EOF
[Unit]
Description=Wiki.js
After=network.target postgresql.service

[Service]
Type=simple
ExecStart=/usr/bin/node server
Restart=always
User=root
WorkingDirectory=/opt/wikijs
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
systemctl daemon-reload
systemctl enable wikijs
systemctl start wikijs

# Verify service running
systemctl status wikijs
# Expected: active (running)

# Test local access
curl http://localhost:3000
# Expected: HTTP 200 response

# Exit container
exit
```

**Validation:**
- [ ] Service installed successfully
- [ ] Service running (systemctl status shows active)
- [ ] Local access works (curl returns 200)
- [ ] Data directory on NFS mount

**If this fails:** See [Troubleshooting](#troubleshooting-issue-2-service-wont-start)

---

### Step 5: Configure Reverse Proxy (Nginx Proxy Manager)

**Goal:** Enable external HTTPS access with automatic SSL certificate

**Access Nginx Proxy Manager:**
1. Open browser: https://192.168.40.50:81
2. Login with admin credentials

**Create Proxy Host:**
```
Settings:
- Domain Names: [SERVICE_NAME].homelab.local
- Scheme: http
- Forward Hostname/IP: 192.168.40.[IP]
- Forward Port: 3000 (or service-specific port)
- Block Common Exploits: ✓
- Websockets Support: ✓ (if needed)

SSL:
- SSL Certificate: Request New Certificate
- Force SSL: ✓
- HTTP/2 Support: ✓
- HSTS Enabled: ✓
- Email: admin@homelab.local
```

**Verification steps:**
```bash
# From workstation, test DNS resolution
nslookup [SERVICE_NAME].homelab.local
# Expected: 192.168.40.50 (Nginx Proxy Manager IP)

# Test HTTP redirect to HTTPS
curl -I http://[SERVICE_NAME].homelab.local
# Expected: HTTP/1.1 301 Moved Permanently
#           Location: https://[SERVICE_NAME].homelab.local

# Test HTTPS access
curl -I https://[SERVICE_NAME].homelab.local
# Expected: HTTP/2 200
#           Server: nginx
```

**Validation:**
- [ ] Proxy host created successfully
- [ ] SSL certificate issued (Let's Encrypt)
- [ ] HTTP redirects to HTTPS
- [ ] Service accessible via domain name

---

### Step 6: Configure Backup Job

**Goal:** Automated daily backups to Proxmox Backup Server

**Configure via Proxmox UI:**
1. Navigate to Datacenter → Backup
2. Click "Add" to create backup job

**Backup Configuration:**
```
General:
- Node: proxmox-01
- Storage: PBS (192.168.40.30)
- Schedule: Daily 02:00
- Selection Mode: Include selected VMs/CTs
- Selected: [VMID]

Retention:
- Keep Last: 7
- Keep Daily: 7
- Keep Weekly: 4
- Keep Monthly: 3

Mode: Snapshot
Compression: ZSTD
```

**Or via CLI:**
```bash
# Create backup job
pvesh create /cluster/backup --storage PBS \
  --vmid [VMID] \
  --dow mon,tue,wed,thu,fri,sat,sun \
  --starttime 02:00 \
  --mode snapshot \
  --compress zstd \
  --prune-backups 'keep-last=7,keep-daily=7,keep-weekly=4,keep-monthly=3'

# Verify backup job created
pvesh get /cluster/backup
```

**Manual backup test:**
```bash
# Trigger immediate backup
vzdump [VMID] --storage PBS --mode snapshot

# Expected output:
# INFO: starting new backup job...
# INFO: creating archive '/mnt/pbs/...'
# INFO: backup job finished successfully
```

**Validation:**
- [ ] Backup job created
- [ ] Manual backup completes successfully
- [ ] Backup appears in PBS web interface
- [ ] Retention policy applied

---

### Step 7: Add Monitoring

**Goal:** Integrate service with Prometheus/Grafana monitoring stack

**Install node_exporter in container:**
```bash
# Enter container
pct enter [VMID]

# Download and install node_exporter
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.1/node_exporter-1.6.1.linux-amd64.tar.gz
tar xzf node_exporter-1.6.1.linux-amd64.tar.gz
cp node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/
rm -rf node_exporter-*

# Create systemd service
cat > /etc/systemd/system/node_exporter.service << EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/node_exporter
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
systemctl daemon-reload
systemctl enable node_exporter
systemctl start node_exporter

# Verify
curl http://localhost:9100/metrics | head
# Expected: Prometheus metrics output

# Exit container
exit
```

**Add to Prometheus scrape config:**
```bash
# SSH to monitoring container
ssh 192.168.40.201

# Edit prometheus config
vim /etc/prometheus/prometheus.yml

# Add new scrape target:
#  - job_name: '[SERVICE_NAME]'
#    static_configs:
#      - targets: ['192.168.40.[IP]:9100']
#        labels:
#          service: '[SERVICE_NAME]'

# Reload Prometheus
systemctl reload prometheus

# Verify target in Prometheus UI
# Open: http://192.168.40.201:9090/targets
# Expected: [SERVICE_NAME] target UP
```

**Validation:**
- [ ] node_exporter running on service
- [ ] Prometheus scraping metrics
- [ ] Target shows "UP" in Prometheus UI
- [ ] Metrics visible in Grafana

---

## Post-Deployment Validation

**Comprehensive health check:**

```bash
# 1. Service health
curl -I https://[SERVICE_NAME].homelab.local
# Expected: HTTP/2 200

# 2. Container/VM status
pct status [VMID]  # or: qm status [VMID]
# Expected: status: running

# 3. Storage mount
pct exec [VMID] -- df -h | grep appdata
# Expected: NFS mount present with correct size

# 4. Backup verification
pvesh get /nodes/proxmox-01/storage/PBS/content --vmid [VMID]
# Expected: At least one backup present

# 5. Monitoring check
curl http://192.168.40.201:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.service=="[SERVICE_NAME]")'
# Expected: JSON with state: "up"

# 6. DNS resolution
dig [SERVICE_NAME].homelab.local
# Expected: Resolves to 192.168.40.50

# 7. SSL certificate
echo | openssl s_client -connect [SERVICE_NAME].homelab.local:443 2>/dev/null | openssl x509 -noout -dates
# Expected: Valid not before/after dates
```

**Final checklist:**
- [ ] Service accessible via HTTPS with valid certificate
- [ ] Data persisting to TrueNAS storage
- [ ] Automated backups configured and tested
- [ ] Monitoring active with metrics visible
- [ ] Documentation updated (network inventory, service catalog)
- [ ] Firewall rules verified (if external access required)

---

## Rollback Procedure

**If deployment fails or service is unstable:**

### Quick Rollback (Stop service, keep data)

```bash
# Stop container
pct stop [VMID]

# Disable autostart
pct set [VMID] --onboot 0

# Remove from Nginx Proxy Manager
# (Manual: Delete proxy host in web UI)
```

### Full Rollback (Remove everything)

```bash
# 1. Stop and destroy container
pct stop [VMID]
pct destroy [VMID]

# 2. Remove backup jobs
pvesh delete /cluster/backup/[JOB_ID]

# 3. Remove Prometheus monitoring
# Edit /etc/prometheus/prometheus.yml, remove scrape config

# 4. Remove NFS share (on TrueNAS)
# Web UI: Sharing → NFS → Delete share

# 5. OPTIONAL: Remove dataset (destroys all data!)
# zfs destroy pool1/appdata/[SERVICE_NAME]

# 6. Remove DNS entry (if custom)
# pfSense: Services → DNS Resolver → Host Overrides → Delete
```

---

## Troubleshooting

### Issue 1: Dataset Creation Fails

**Symptoms:**
```
cannot create 'pool1/appdata/service': dataset already exists
```

**Cause:** Dataset name collision

**Solution:**
```bash
# Check if dataset exists
zfs list | grep [SERVICE_NAME]

# If present, use different name or remove old dataset:
zfs destroy pool1/appdata/[SERVICE_NAME]  # WARNING: Deletes all data!
```

### Issue 2: Service Won't Start

**Symptoms:**
```
systemctl status shows: failed (Result: exit-code)
```

**Cause:** Configuration error, missing dependencies, or port conflict

**Solution:**
```bash
# Check service logs
journalctl -u [SERVICE_NAME] -n 50 --no-pager

# Common issues:
# - Port already in use: netstat -tlnp | grep [PORT]
# - Missing dependencies: apt install [PACKAGE]
# - Incorrect config: vim /path/to/config.yml
# - Permission issues: chown -R [USER]:[GROUP] /path/to/app

# Restart after fixes
systemctl restart [SERVICE_NAME]
```

### Issue 3: NFS Mount Fails

**Symptoms:**
```
mount.nfs: access denied by server
```

**Cause:** TrueNAS NFS permissions or network ACL

**Solution:**
```bash
# On TrueNAS, verify NFS share settings:
# 1. Authorized Networks includes 192.168.40.0/24
# 2. Mapall User/Group set to root
# 3. NFS service is running: service nfs-server status

# On container, verify network:
ping 192.168.40.20
showmount -e 192.168.40.20
```

### Issue 4: SSL Certificate Fails

**Symptoms:** Let's Encrypt certificate request fails

**Cause:** DNS resolution issue or port 80/443 blocked

**Solution:**
```bash
# Verify DNS resolves correctly
nslookup [SERVICE_NAME].homelab.local

# Check firewall allows HTTP challenge (port 80)
# pfSense: Firewall → Rules → WAN → Verify port 80 allowed

# Use DNS challenge instead of HTTP-01 if internal-only
# NPM: SSL → DNS Challenge → Select provider
```

### Issue 5: Backup Job Fails

**Symptoms:**
```
ERROR: Backup failed - transport error: peer closed connection
```

**Cause:** PBS connectivity issue or insufficient storage

**Solution:**
```bash
# Verify PBS accessible
ping 192.168.40.30
curl https://192.168.40.30:8007

# Check PBS storage capacity
pvesh get /nodes/pbs/storage/datastore/status

# If full, prune old backups:
proxmox-backup-client prune --keep-last 3 --dry-run
```

---

## Related Runbooks
- [Disaster Recovery: VM Restoration](./restore-from-backup.md)
- [Service Maintenance: Update Procedure](./update-service.md)
- [Troubleshooting: Network Connectivity](./network-troubleshooting.md)

## Contact & Escalation
- **Documentation:** https://github.com/samueljackson-collab/Portfolio-Project
- **Monitoring:** http://192.168.40.201:3000 (Grafana)
- **Backup Server:** https://192.168.40.30:8007 (Proxmox Backup Server)

---

**Document Version:** 1.0
**Last Updated:** November 6, 2025
**Author:** Sam Jackson
**Review Frequency:** Quarterly
