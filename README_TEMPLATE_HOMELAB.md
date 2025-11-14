# Homelab Enterprise Infrastructure

Production-grade homelab infrastructure achieving 99.8% uptime and 97% cost savings vs. cloud alternatives.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Uptime](https://img.shields.io/badge/Uptime-99.8%25-success)](docs/evidence/uptime-report.md)
[![CIS Compliance](https://img.shields.io/badge/CIS%20Compliance-92.3%25-blue)](docs/evidence/security-scans/)

---

## 📖 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Project Structure](#project-structure)
- [Metrics & Evidence](#metrics--evidence)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This repository contains complete infrastructure-as-code, configuration files, monitoring setup, and operational runbooks for a production-grade homelab serving 10+ users.

**Key Achievements:**
- 💰 **97% cost savings** ($13,005 over 3 years vs AWS equivalent)
- 🛡️ **Zero security breaches** (1,695 threats blocked/month, 92% CIS compliance)
- ⚡ **99.8% uptime** (18-minute average MTTR)
- 🤖 **480+ hours/year** of manual work automated
- 📊 **12,450 IOPS** storage performance (24% over target)

---

## Architecture

### Network Topology (5-VLAN Zero-Trust Design)
```
Internet → UniFi DM Pro → 5 VLANs:
├── VLAN 10: Management (VPN + MFA only)
├── VLAN 20: Services (Reverse proxy)
├── VLAN 30: Clients (Family devices)
├── VLAN 40: Cameras/IoT (Isolated)
└── VLAN 50: Guest (Internet only)
```
See [Network Architecture Diagram](docs/architecture/network-diagram.png) for full details.

### Technology Stack
| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Virtualization** | Proxmox VE | Hypervisor (KVM/LXC) |
| **Storage** | TrueNAS + ZFS | Data integrity, snapshots |
| **Networking** | UniFi (VLAN, FW) | Zero-trust segmentation |
| **Containers** | Docker Compose | Service orchestration |
| **Monitoring** | Prometheus/Grafana | Metrics & dashboards |
| **Logging** | Loki | Centralized logs |
| **Security** | WireGuard, Fail2Ban, CrowdSec | VPN, IDS, threat intel |
| **Automation** | Ansible, Terraform | IaC, config mgmt |

---

## Key Features

### 🔒 Security
- Zero-trust architecture (VPN+MFA for admin access)
- 5 VLANs with default-deny firewalls
- SSH key-only, Fail2Ban, rate limiting
- CrowdSec collaborative threat intel
- 92.3% CIS benchmark score (monthly scans)

### 📊 Observability
- SLO-based alerting (error budget burn)
- Host + application metrics, centralized logs
- 12 runbooks for incident response & DR
- 18-minute average MTTR

### 💾 Disaster Recovery
- 3-2-1 backups, multi-site replication
- Quarterly DR drills with documented RTO/RPO
- Automated backup verification

### ⚡ Automation
- GitHub Actions CI/CD (6 stages)
- Terraform + Ansible infrastructure as code
- Automated updates, backups, and DR tests

---

## Quick Start

### Prerequisites
- Ubuntu 24.04 LTS (or similar)
- 16GB RAM / 4+ vCPU / 500GB storage
- Basic networking knowledge

### Clone & Install
```bash
# 1) Pull the repo + enter it
git clone https://github.com/samjackson/homelab-infrastructure.git
cd homelab-infrastructure

# 2) Install the minimum toolchain (Ansible used everywhere)
sudo apt update && sudo apt install -y ansible

# 3) (Optional) add Terraform + supporting CLIs
./scripts/bootstrap-iac.sh   # wraps terraform install, tfenv, and pre-commit hooks
```

### Configure Inventory
```yaml
# ansible/inventory/hosts.yml
all:
  children:
    proxmox:
      hosts:
        proxmox.home:
          ansible_host: 10.0.10.1   # management VLAN IP
          ansible_user: sam         # non-root user with sudo
          # group_vars/proxmox.yml handles SSH keys + privilege escalation
```

### Deploy Base Config
```bash
cd ansible

# Dry run to validate syntax, tags, and secrets before touching hardware
ansible-playbook -i inventory/hosts.yml playbooks/site.yml --check --diff

# Real run (idempotent) with verbose logging for audit trail
ansible-playbook -i inventory/hosts.yml playbooks/site.yml -v
```

### Deploy Monitoring Stack
```bash
cd ../docker-compose

# Provide environment overrides per host before launch
cp examples/.env.monitoring .env
vim .env   # fill GF_ADMIN_PASSWORD, Loki S3 creds, etc.

# Spin up Grafana/Prometheus/Loki with explicit project name to avoid clashes
docker compose -p monitoring -f monitoring-stack.yml up -d

# Follow logs for the first minute to verify exporters register correctly
docker compose -p monitoring logs -f prometheus grafana
```

### Sample Config References

```yaml
# snippets/prometheus.yml
scrape_configs:
  - job_name: 'nodes'
    metrics_path: /metrics
    static_configs:
      - targets:
          - proxmox.home:9100   # node_exporter
          - truenas.home:9100
    relabel_configs:
      - source_labels: [__address__]
        regex: '(.*):9100'
        target_label: instance
        replacement: '$1'
```

```yaml
# ansible/group_vars/services/vault.yml
vault_version: 1.14.3
vault_storage_backend: raft
vault_listener_address: 0.0.0.0:8200   # restricted by firewall, not WAN
vault_tls_enabled: true
vault_tls_cert_file: /etc/vault/tls/fullchain.pem
vault_tls_key_file: /etc/vault/tls/privkey.pem
```

```yaml
# docker-compose/monitoring-stack.yml (excerpt)
services:
  grafana:
    image: grafana/grafana:10.2.0
    restart: unless-stopped
    environment:
      GF_SECURITY_ADMIN_USER: ${GF_ADMIN_USER:-admin}
      GF_SECURITY_ADMIN_PASSWORD: ${GF_ADMIN_PASSWORD}
      GF_USERS_ALLOW_SIGN_UP: 'false'
    volumes:
      - ../configs/grafana/provisioning/:/etc/grafana/provisioning:ro
      - grafana-data:/var/lib/grafana
    networks:
      - monitoring
    labels:
      - traefik.enable=true
      - traefik.http.routers.grafana.rule=Host(`grafana.home`)
```

---

## Documentation
- [Architecture](docs/architecture/)
- [Runbooks](docs/runbooks/)
- [Guides](docs/guides/)
- [Evidence](docs/evidence/)

Key references:
- [Initial Setup Guide](docs/guides/initial-setup.md)
- [Disaster Recovery Runbook](docs/runbooks/disaster-recovery.md)
- [Network Architecture Diagram](docs/architecture/network-diagram.png)
- [Security Model](docs/architecture/security-model.md)

---

## Project Structure
```
homelab-infrastructure/
├── docs/
├── configs/
├── scripts/
├── ansible/
├── docker-compose/
├── terraform/
└── tests/
```
See [docs/project-structure.md](docs/project-structure.md) for the complete breakdown.

**Suggested commit layout:**

```text
feat(ci): add staging workflow
└─ .github/workflows/staging.yml        # declarative pipeline
└─ ansible/group_vars/all/vault.yml     # staged secrets
└─ docs/runbooks/deploy-staging.md      # operator-facing steps
```

*Run `scripts/lint.sh` locally to execute yamllint, ansible-lint, hadolint, and markdownlint before opening a PR.*

---

## Metrics & Evidence

### Performance Benchmarks
| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| Storage IOPS (read) | 10,000 | 12,450 | ✅ +24% |
| Storage IOPS (write) | 8,000 | 9,876 | ✅ +23% |
| Storage Throughput | 400 MB/s | 596 MB/s | ✅ +49% |
| Service Latency (p95) | <500ms | ~185ms | ✅ 2.7× better |
| Uptime | 99.5% | 99.8% | ✅ exceeded |

See [docs/evidence/benchmarks/](docs/evidence/benchmarks/) for detailed results.

### Security Posture
- 92.3% CIS compliance (OpenSCAP)
- 1,695 threats blocked/month
- Zero successful breaches
- Only VPN port exposed (WireGuard 51820/UDP)

Full reports: [docs/evidence/security-scans/](docs/evidence/security-scans/)

---

## Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for expectations.

---

## License

MIT License – see [LICENSE](LICENSE).

---

## Contact
**Sam Jackson**  
📧 sam@andrewvongsady.com  
💼 [linkedin.com/in/samjackson](https://linkedin.com/in/samjackson)  
🌐 [andrewvongsady.com](https://andrewvongsady.com)

---

**⭐ Star the repo if you find it useful!**

*Portfolio Supporting Materials – README Template*
