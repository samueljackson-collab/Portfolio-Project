# Portfolio Architecture Diagrams – Part 2

**Owner:** Samuel Jackson  
**Document Status:** Complete  
**Last Updated:** 2025-11-13  
**Context:** Continuation of the homelab architecture visuals that accompany the executive-ready portfolio narrative.

> These diagrams extend Part 1 by covering the platform migration roadmap, core service data flows, total homelab topology, and an AWS equivalency map for interview conversations. Supporting materials (repository layout and interview cheat sheet) ensure each diagram ties back to tangible evidence.

---

## 7. Container Platform – Docker Compose to Kubernetes Migration

### 7.1 Evolution Path Diagram

```
PHASE 1: DOCKER COMPOSE (CURRENT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Docker Host (VM on Proxmox)
├── docker-compose.yml
│   ├── immich-server (photos.andrewvongsady.com)
│   ├── immich-database (PostgreSQL)
│   ├── immich-redis (cache)
│   ├── wikijs (wiki.andrewvongsady.com)
│   ├── wikijs-database (PostgreSQL)
│   ├── homeassistant (home.andrewvongsady.com)
│   ├── grafana (monitor.andrewvongsady.com)
│   ├── prometheus
│   └── loki
└── Storage: NFS mount from TrueNAS

Pros: Simple, fast deployment
Cons: Single host, no auto-scaling, manual updates

PHASE 2: KUBERNETES (K3S) – PLANNED Q2 2026
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

K3s Cluster (Lightweight Kubernetes)
├── Control Plane (Master Node)
│   └── VM: k3s-master (2 vCPU, 4GB RAM)
├── Worker Node 1
│   └── VM: k3s-worker-1 (4 vCPU, 8GB RAM)
└── Worker Node 2
    └── VM: k3s-worker-2 (4 vCPU, 8GB RAM)

Namespaces:
├── production (immich, wikijs, homeassistant)
├── monitoring (grafana, prometheus, loki)
└── ingress-nginx (reverse proxy)

Storage:
├── Persistent Volumes (NFS from TrueNAS)
└── Dynamic Provisioning (nfs-client-provisioner)

Benefits:
✅ High availability (pod restarts, node failover)
✅ Auto-scaling (based on CPU/memory)
✅ Rolling updates (zero-downtime deployments)
✅ Self-healing (restart failed containers)
✅ GitOps (ArgoCD for declarative deployments)

Migration Strategy:
Week 1: Deploy K3s cluster
Week 2: Migrate monitoring stack (non-critical)
Week 3: Migrate Wiki.js (low traffic)
Week 4: Migrate Immich (validate thoroughly)
```

### 7.2 Narrative Summary
- **Current state:** A single Docker host on Proxmox simplifies deployments but concentrates risk (single point of failure, manual updates).
- **Future state:** A 3-node K3s cluster splits control plane and workers, enabling namespace isolation, GitOps automation, and rolling deployments.
- **Key enabler:** NFS-backed persistent volumes via the `nfs-client-provisioner` keep storage simple while unlocking dynamic PVCs.
- **Risk mitigation:** Incremental migration by criticality ensures monitoring is validated before customer-facing services move.

---

## 8. Data Flow – Photo Service End-to-End

### 8.1 Upload Path Diagram

```
USER DEVICE (Phone/Browser)
      │
      │ 1. Upload photo via HTTPS
      │    POST /api/upload
      │
      ▼
┌─────────────────────────────────┐
│  Nginx Reverse Proxy            │
│  (SSL Termination)              │
│  • Validate certificate         │
│  • Check rate limit (100/min)   │
│  • Forward to backend           │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  Immich Server (Docker)         │
│  Port: 3001 (internal)          │
│  • Authenticate user (JWT)      │
│  • Validate file (type, size)   │
│  • Generate UUID for file       │
│  • Save metadata to DB          │
└──────────────┬──────────────────┘
               │
               ├─────────────────────────┐
               │                         │
               ▼                         ▼
┌──────────────────────┐    ┌────────────────────────┐
│  PostgreSQL DB       │    │  Object Storage        │
│  (Metadata)          │    │  NFS: /mnt/tank/photos │
│                      │    │                        │
│  Tables:             │    │  • Original upload     │
│  • users             │    │  • Thumbnails (gen)    │
│  • assets (photos)   │    │  • Encoded video       │
│  • albums            │    │                        │
│  • sharing           │    │  ZFS Features:         │
└──────────────────────┘    │  • Checksums (verify)  │
                            │  • Compression (lz4)   │
                            │  • Snapshots (backup)  │
                            └────────────────────────┘

Performance:
• Upload time (5MB photo): <2 seconds
• Thumbnail generation: <500ms
• Database write: <50ms
• Total latency (user → storage): <3 seconds
```

### 8.2 Reliability & Performance Notes
- Edge-controlled rate limiting stops burst uploads from overloading the backend.
- JWT auth keeps the session stateless across future scaled replicas.
- ZFS checksums plus snapshot cadence provide built-in data integrity and rollback.
- Latency goals (<3 seconds total) map to interview-ready SLIs/SLOs for user experience.

---

## 9. High-Level System Architecture – Complete Homelab

### 9.1 Topology Diagram

```
                            INTERNET
                               │
                         ┌─────▼─────┐
                         │  ISP Modem │
                         │  (Gateway) │
                         └─────┬─────┘
                               │
                    ┌──────────▼──────────┐
                    │  UniFi Dream Machine │
                    │  (Router/Firewall)   │
                    └──────────┬───────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │ Management VLAN      │ Services VLAN        │ Client VLAN
        │ 10.0.10.0/24         │ 10.0.20.0/24         │ 10.0.30.0/24
        │                      │                      │
    ┌───▼─────┐         ┌──────▼───────┐      ┌──────▼──────┐
    │ Proxmox │         │ Docker Host  │      │ Client      │
    │  Host   │         │  (Services)  │      │  Devices    │
    │         │         │              │      │             │
    │ VMs:    │         │ Containers:  │      │ • Phones    │
    │ TrueNAS │         │ • Immich     │      │ • Laptops   │
    │ Docker  │         │ • Wiki.js    │      │ • Tablets   │
    │ Monitor │         │ • Home Asst  │      │             │
    └─────────┘         └──────────────┘      └─────────────┘
        │                      │
        │ NFS Mount (Storage)  │
        └──────────┬───────────┘
                   │
              ┌────▼────┐
              │ TrueNAS │
              │   VM    │
              │         │
              │ ZFS:    │
              │ • Photos│
              │ • Docs  │
              │ • Backup│
              └─────────┘

Total Infrastructure:
• Physical Hosts: 1 (HP Z440)
• Virtual Machines: 4
• Containers: 10+
• Storage: 2TB ZFS (mirrored)
• Network: 5 VLANs
• Users: 10+ family members
```

### 9.2 Takeaways
- VLAN segmentation mirrors enterprise zero-trust: separate management, services, clients, and (not shown) IoT/guest networks.
- Proxmox hosts the entire stack; TrueNAS exposes NFS/SMB for services, while Docker host consumes the storage for stateful apps.
- Numbers at the bottom double as fast metrics when presenting the homelab’s scale.

---

## 10. Cloud Translation – Homelab to AWS Mapping

### 10.1 Skills Transfer Matrix

```
HOMELAB COMPONENT          AWS EQUIVALENT           TRANSFERABLE SKILLS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Network Layer:
─────────────────────────────────────────────────────────────────────────
UniFi VLANs               → VPC Subnets             • Network segmentation
Firewall Rules            → Security Groups/NACLs   • Default deny policies
WireGuard VPN             → AWS VPN Gateway         • Secure remote access
Nginx Reverse Proxy       → Application Load Bal    • TLS termination, routing

Compute Layer:
─────────────────────────────────────────────────────────────────────────
Proxmox VMs               → EC2 Instances           • Resource allocation
Docker Containers         → ECS/Fargate             • Containerization
Proxmox Snapshots         → EC2 AMIs                • Backup/restore procedures
Resource Overcommit       → Auto Scaling            • Capacity planning

Storage Layer:
─────────────────────────────────────────────────────────────────────────
ZFS Mirroring             → EBS Multi-AZ            • Data redundancy
NFS Shares                → EFS                     • Shared file storage
Backup Scripts            → AWS Backup              • Retention policies
Snapshots                 → EBS Snapshots           • Point-in-time recovery

Observability:
─────────────────────────────────────────────────────────────────────────
Prometheus                → CloudWatch Metrics      • Time-series monitoring
Grafana Dashboards        → CloudWatch Dashboards   • Visualization
Loki Logs                 → CloudWatch Logs         • Centralized logging
Alertmanager              → SNS + Lambda            • Alert routing

Security:
─────────────────────────────────────────────────────────────────────────
SSH Key Auth              → IAM Key Pairs           • Credential management
Fail2Ban                  → AWS WAF                 • Brute force protection
CrowdSec                  → GuardDuty               • Threat intelligence
MFA (TOTP)                → AWS MFA                 • Multi-factor auth

Automation:
─────────────────────────────────────────────────────────────────────────
Bash Scripts              → Lambda Functions        • Event-driven automation
Ansible Playbooks         → Systems Manager         • Configuration management
Cron Jobs                 → EventBridge             • Scheduled tasks
Backup Scripts            → AWS Backup Plans        • Automated backups
```

### 10.2 Interview Talking Points
- VLAN → VPC stories translate 1:1 into subnet design, least privilege, and zero-trust discussions.
- Observability stack (Prometheus, Loki, Grafana) mirrors CloudWatch patterns; highlight SLO-based alerting and burn-rate detection.
- Backup conversations map to the 3-2-1 rule; reference ZFS snapshots, USB/offsite copies, and how that becomes EBS snapshots + S3 + cross-region replication.

---

## Supporting Materials

### A. Configuration File Repository Structure

Use this canonical tree to back claims made in the diagrams. Each directory is present (or planned) inside the `homelab-infrastructure/` repository.

```
homelab-infrastructure/
│
├── README.md
├── LICENSE
├── .gitignore
│
├── docs/
│   ├── architecture/
│   │   ├── network-diagram.png
│   │   ├── storage-architecture.md
│   │   ├── security-model.md
│   │   └── adr/
│   │       ├── 001-proxmox-over-esxi.md
│   │       ├── 002-single-host-vs-cluster.md
│   │       └── 003-zfs-mirroring.md
│   ├── runbooks/
│   ├── guides/
│   └── evidence/
│       ├── grafana-dashboards/
│       ├── benchmarks/
│       └── security-scans/
│
├── configs/
│   ├── proxmox/
│   ├── truenas/
│   ├── network/
│   ├── monitoring/
│   └── services/
│
├── scripts/
├── ansible/
├── terraform/
└── tests/
```

> **Tip:** When presenting in interviews, pair this tree with screenshots or JSON exports (Grafana, Prometheus alerts, UniFi config) stored in `docs/evidence/` to demonstrate depth.

### B. Interview Preparation Cheat Sheet

#### B.1 Top 5 Quantified Achievements
1. **Cost Savings:** 97% reduction ($13,005 over 3 years) – homelab vs AWS.
2. **Reliability:** 99.8% uptime, 18-minute average MTTR.
3. **Security:** 1,695 threats blocked, 0 successful breaches, 92% CIS compliance.
4. **Automation:** 480+ hours/year manual work eliminated.
5. **Performance:** 12,450 IOPS (24% over target), 596 MB/s throughput.

#### B.2 STAR Stories (30-second versions)
- **Improved Reliability:** Built observability stack (Prom/Graf/Loki), fixed top failure modes, moved Immich uptime from 97.2% → 99.8% and MTTR 45 → 18 minutes.
- **Trade-Off Decision:** Chose single host + multi-site backup over 3-node cluster to stay within $240 budget, saved $450 while hitting 45-minute RTO.
- **Automation Win:** Automated backup verification via Python, Prometheus integration, and runbook — 83% time savings (~100 hrs/yr) and error rate <0.1%.
- **Security Implementation:** Designed seven-layer defense (VPN, MFA, VLAN isolation, SSH hardening, IDS); blocked 1,695 threats/month with zero breaches.
- **Learning New Tech:** Self-taught ML/computer vision to build AstraDup video deduplication with 95%+ precision, processing 250+ videos/hour.

#### B.3 Technical Deep-Dive Bullets
- **Monitoring System:** 3-tier approach (collection → storage → visualization), SLO-based alerts with fast/slow burn-rate, runbooks for 18-minute MTTR.
- **Secure SSH Access:** Network isolation (VPN-only), key-based auth with MFA, host hardening (Fail2Ban/CrowdSec), and telemetry alerts for anomalies.
- **Disaster Recovery:** 3-2-1 backups using ZFS snapshots, local/offsite copies, quarterly DR drills with documented RPO/RTO targets.

#### B.4 Key Metrics Table

| Category | Metric | Value |
| --- | --- | --- |
| Cost | Homelab vs AWS (3-year) | $675 vs $13,680 (95% savings) |
| Reliability | Uptime | 99.8% (target 99.5%) |
| Reliability | MTTR | 18 minutes avg |
| Security | Threats blocked | 1,695/month |
| Security | Successful breaches | 0 |
| Security | CIS compliance | 92.3% |
| Performance | Storage IOPS (read) | 12,450 |
| Performance | Storage throughput | 596 MB/s |
| Automation | Manual work eliminated | 480 hours/year |

#### B.5 Skill Demonstration Map
- **Infrastructure:** End-to-end ownership from hardware through application.
- **DevOps:** CI/CD (+80% velocity) and IaC (Terraform, Ansible) coverage.
- **SRE:** SLO-based alerting, incident response, capacity planning.
- **Security:** Zero-trust design, 7-layer defense, 92% CIS compliance.
- **Cloud:** AWS-ready vocabulary (VPC, EC2, S3) grounded in homelab practice.

#### B.6 Elevator Pitch (60 seconds)
> “I built an enterprise-grade homelab that demonstrates production infrastructure skills at 97% less cost than AWS. The system achieves 99.8% uptime serving 10+ family members, with comprehensive security (zero breaches, 92% CIS compliance) and observability (18-minute MTTR). I automated 480 hours/year of manual work and documented everything with runbooks and ADRs. Skills map directly to AWS—VLAN segmentation ↔ VPC subnets, Prometheus ↔ CloudWatch, and 3-2-1 backups ↔ multi-tier AWS recovery. I also self-taught machine learning to ship AstraDup video deduplication at 95%+ precision. I design, build, and operate reliable systems while tying every decision to cost, risk, and business value.”

---

## Next Deliverables
- **Executive Summary:** Tailored narrative referencing these diagrams.
- **Screenshot Guide:** Pair visuals with evidence and CLI captures.
- **Video Script:** Walkthrough that tracks diagrams 7–10.
- **Full GitHub Structure:** Detailed mapping of each repo folder to artifacts.
