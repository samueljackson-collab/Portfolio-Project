# Homelab Operations Log Samples
# ================================

This directory contains sanitized sample logs from homelab virtualization operations.

## Available Log Samples

### vm-deployment-sample.log
**Purpose:** Complete VM deployment walkthrough using Proxmox and cloud-init
**Content:**
- Template cloning process
- Cloud-init configuration
- Network configuration (static IP, DNS, gateway)
- Post-deployment automation:
  - Package installation
  - Docker setup
  - Firewall configuration
  - Security hardening
  - Monitoring agent installation
- Integration with:
  - Prometheus (node_exporter)
  - Loki (Promtail)
  - Proxmox Backup Server
  - Ansible inventory

**Deployment Timeline:**
- Template clone: 1m16s
- Configuration: 30s
- Cloud-init: 1m10s
- Post-deployment: 2m32s
- **Total:** 4m19s (fully automated)

**Key Features Demonstrated:**
- Infrastructure-as-Code principles
- Automated VM provisioning
- Immediate monitoring integration
- Backup job auto-configuration
- Configuration management (Ansible)

---

## Log Collection

### Sources
```
Proxmox API ──┬── VM creation events
              ├── Clone operations
              └── Configuration changes

Cloud-init ────── First boot logs

SSH/Ansible ───── Post-deployment tasks

Monitoring ────── Health checks
```

### Storage
- **Local:** `/var/log/` on Proxmox nodes
- **Centralized:** Loki (via Promtail)
- **Retention:** 30 days local, 90 days in Loki

---

## About This Log

### What It Shows
This log demonstrates a **production-grade VM deployment workflow**:

1. **Template-Based Provisioning**
   - Uses pre-built cloud-init template
   - Consistent, repeatable deployments
   - Fast deployment times (~4 minutes)

2. **Configuration Management**
   - Cloud-init for initial setup
   - Ansible for ongoing management
   - Standardized configurations

3. **Day-2 Operations**
   - Automatic monitoring integration
   - Backup job configuration
   - Security baseline application
   - Inventory management

### Real-World Benefits
- **Speed:** 4 minutes vs. 30+ minutes manual
- **Consistency:** Every VM identical
- **Reliability:** No human error
- **Observability:** Monitoring from minute-one
- **Recovery:** Backups start immediately

---

## VM Deployment Architecture

```
┌──────────────┐
│  Template    │
│  (Ubuntu     │
│  22.04 +     │
│  cloud-init) │
└──────┬───────┘
       │ Clone
       ▼
┌──────────────┐
│  New VM      │
│  (Stopped)   │
└──────┬───────┘
       │ Apply cloud-init
       │ (IP, hostname, SSH key)
       ▼
┌──────────────┐
│  VM Started  │
│  (Booting)   │
└──────┬───────┘
       │ Cloud-init runs
       │ (user creation, packages)
       ▼
┌──────────────┐
│  VM Ready    │
│  (SSH        │
│  accessible) │
└──────┬───────┘
       │ Post-deploy automation
       │ (Ansible, monitoring, backups)
       ▼
┌──────────────┐
│  Production  │
│  Ready       │
└──────────────┘
```

---

## Key Configurations

### Cloud-Init Config Applied
```yaml
# Network
IP: 192.168.10.100/24 (static)
Gateway: 192.168.10.1
DNS: 192.168.10.2 (Pi-hole)
Hostname: wikijs-production.homelab.local

# User
Username: admin
SSH Key: (public key from template)
Sudo: NOPASSWD

# Packages
- docker.io
- docker-compose
- node-exporter
- promtail
```

### Post-Deployment Automation
```bash
# Security
- UFW firewall (SSH, HTTP, HTTPS)
- Automatic security updates
- SSH hardening

# Monitoring
- Node exporter: :9100/metrics
- Promtail: → Loki logging

# Backup
- PBS job: Daily 02:00 AM
- Retention: 7d/4w/3m

# Management
- Ansible inventory: production_vms
```

---

## Related Files

### In This Repository
- **Templates:** `../configs/proxmox/vm-templates/`
- **Cloud-Init:** `../configs/cloud-init/`
- **Ansible:** `../automation/ansible/`
- **Monitoring:** `../../PRJ-SDE-002/`

### In Production
- Template ID: 9000 (ubuntu-22.04-cloudinit-template)
- Template Location: local-lvm:base-9000-disk-0
- Ansible Inventory: `/etc/ansible/hosts.yml`

---

## Usage Examples

### Clone This Workflow
1. **Create cloud-init template:**
   ```bash
   # Download Ubuntu cloud image
   wget https://cloud-images.ubuntu.com/releases/22.04/release/ubuntu-22.04-server-cloudimg-amd64.img

   # Create VM template
   qm create 9000 --name ubuntu-22.04-cloudinit-template --memory 2048 --cores 2
   qm importdisk 9000 ubuntu-22.04-server-cloudimg-amd64.img local-lvm
   qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9000-disk-0
   qm set 9000 --ide2 local-lvm:cloudinit
   qm set 9000 --boot c --bootdisk scsi0
   qm set 9000 --serial0 socket --vga serial0
   qm template 9000
   ```

2. **Deploy new VM:**
   ```bash
   # Clone template
   qm clone 9000 100 --name wikijs-production

   # Configure cloud-init
   qm set 100 --ipconfig0 ip=192.168.10.100/24,gw=192.168.10.1
   qm set 100 --nameserver 192.168.10.2
   qm set 100 --searchdomain homelab.local
   qm set 100 --sshkey ~/.ssh/id_rsa.pub

   # Start VM
   qm start 100
   ```

3. **Run post-deployment automation:**
   ```bash
   # Wait for VM to be ready
   while ! ssh admin@192.168.10.100 'echo ready'; do sleep 5; done

   # Run Ansible playbook
   ansible-playbook -i production playbooks/setup-monitoring.yml --limit wikijs-production
   ```

---

## Troubleshooting

### Common Issues

**VM doesn't get IP address:**
- Check cloud-init logs: `sudo cat /var/log/cloud-init.log`
- Verify network bridge: `qm config 100 | grep net`

**SSH key auth fails:**
- Verify key in template: `cat /var/lib/vz/snippets/cloud-init.yml`
- Check cloud-init user data: `sudo cloud-init query userdata`

**Monitoring not showing up:**
- Check node_exporter: `curl localhost:9100/metrics`
- Verify Prometheus scrape config
- Check Promtail logs: `sudo journalctl -u promtail`

---

## Future Improvements

- [ ] Terraform module for VM provisioning
- [ ] GitOps workflow with ArgoCD
- [ ] Automated testing of deployed VMs
- [ ] Integration with HashiCorp Vault for secrets
- [ ] Automated disaster recovery drills

---

**Note:** All hostnames, IP addresses, and credentials in logs are sanitized examples. Real production logs would include actual infrastructure identifiers.

**Last Updated:** 2024-11-06
