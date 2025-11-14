# Portfolio Master Index – Continuation

## 4.1 Homelab Enterprise Infrastructure Deep Dive

### 4.1.1 Business Case & ROI

**Objective:** Gain production-grade infrastructure experience without corporate datacenter access.

**Financial Analysis (3-Year TCO):**

```
Homelab Solution
├── CAPEX: $225 (existing HP Z440 workstation + upgrades)
├── OPEX: $150/year (power + domain)
└── 3-Year TCO: $675

AWS Equivalent
├── Compute (2×t3.medium): $720/year
├── Storage (2 TB EBS + backups): $2,400/year
├── Networking & Monitoring: $1,440/year
└── 3-Year TCO: $13,680
```

**Result:** 95% cost reduction ($13,005 saved) while enabling experimentation without risking production systems.

**Career ROI:** Skills transfer (network architecture, IaC, monitoring) accelerates eligibility for SDE/SRE roles, conservatively valued at $40k/year salary uplift if realized one year sooner.

### 4.1.2 Architecture Decisions & Trade-offs

**ADR-001: Virtualization Platform**

- **Options:** VMware ESXi, Docker-only, Proxmox VE
- **Decision:** Proxmox VE selected for zero licensing cost, VM + LXC support, built-in backups.
- **Trade-off:** Smaller enterprise adoption than VMware, but virtualization concepts transfer.

**ADR-002: Topology – Single Host vs Multi-Host Cluster**

- **Decision:** Single host + multi-site replication.
- **Rationale:** Budget/power limits; demonstrates HA concepts via replication/DR. Accepted risk of host failure mitigated via 45-minute RTO.

**ADR-003: Orchestration – Kubernetes vs Docker Compose**

- **Decision:** Docker Compose for Phase 1, plan K3s migration Phase 2.
- **Rationale:** Compose provides 80% of benefits with 20% complexity; establishes baseline before layering K8s.

**ADR-004: Storage – ZFS on TrueNAS vs Native LVM**

- **Decision:** TrueNAS VM with ZFS mirror.
- **Rationale:** Checksums, snapshots, replication, NFS/SMB sharing justify extra complexity.

### 4.1.3 Network Architecture – Zero-Trust Security Model

**VLAN Segmentation:**

```
VLAN 10 – Management: VPN + MFA required; default deny.
VLAN 20 – Services: Exposed via reverse proxy; limited east/west access.
VLAN 30 – Clients: User devices; can reach services only.
VLAN 40 – Cameras/IoT: No internet; allowlisted control path.
VLAN 50 – Guest: Internet-only, blocks RFC1918 ranges.
```

**Firewall Philosophy:** Default deny between VLANs; explicitly allow flows (e.g., Immich → TrueNAS NFS, Services → Cameras). Mitigates lateral movement.

**Zero-Trust Benefits:** IoT compromise confined to VLAN 40; admin panels require VPN + MFA; attack surface limited to single VPN port.

### 4.1.4 Storage Architecture – ZFS Data Integrity

**ZFS Features Leveraged:**

- End-to-end checksums catch bit-rot.
- Copy-on-write snapshots (hourly/daily/weekly/monthly retention).
- LZ4 compression (+20% effective capacity).
- ZFS send/receive replication (multi-site backups).

**Pool Configuration:** 2×1 TB NVMe mirror (`tank`), atime off, compression on.

**Performance Benchmarks:** Sequential read 596 MB/s, write 511 MB/s; random 4K read 12,450 IOPS, write 9,876 IOPS—exceeding requirements for photo workloads.

**Data Protection Strategy:**

1. RAID1 mirror (drive failure tolerance)
2. Hourly snapshots (ransomware/accidental deletion)
3. Offsite replication via Syncthing (site disasters)
4. Optional S3 Glacier (multi-site catastrophic events)

### 4.1.5 Zero-Trust Access Control – VPN + MFA

**Problem:** Exposed admin ports invite brute force/zero-days.

**Solution:**

- WireGuard VPN as sole WAN entry (port 51820).
- MFA enforced on Proxmox, TrueNAS, UniFi, Nginx Proxy Manager, Grafana.
- Access control matrix ensures services require VPN + MFA as appropriate.

**WireGuard Example:**

```
[Interface]
PrivateKey = <server>
Address = 10.0.60.1/24
ListenPort = 51820

[Peer] # Laptop
PublicKey = <client>
AllowedIPs = 10.0.60.10/32
```

**Result:** Attackers must compromise VPN keys + MFA + underlying service. Zero admin ports exposed publicly.

### 4.1.6 SSH Hardening & Intrusion Detection

**Hardening Checklist:**

- Disable password auth (`PasswordAuthentication no`).
- Deny root login (`PermitRootLogin no`).
- Restrict users (`AllowUsers sam`).
- Enforce modern crypto suites (chacha20, curve25519).
- Limit sessions/auth attempts (`MaxAuthTries 3`).

**Defense Layers:**

1. VPN requirement.
2. SSH keys only.
3. Fail2Ban bans after 3 failures (exponential backoff).
4. CrowdSec shares threat intelligence globally.
5. Grafana dashboards monitor failed logins.

**Metrics:** 1,247 brute force attempts blocked/month; 0 compromises.

### 4.1.7 Disaster Recovery & Business Continuity

**Service Tiers:**

- Tier 1 (Photos): RPO 12h, RTO 45m.
- Tier 2 (Wiki, Home Assistant): RPO 24h, RTO 4h.
- Tier 3 (Monitoring, test VMs): RPO 7d, RTO 24h.

**Backup Architecture:**

1. Hourly ZFS snapshots (onsite)
2. Nightly Proxmox backups to USB
3. Weekly Syncthing replication to family sites
4. Monthly optional cloud archive

**DR Runbook Highlights:**

- Hardware prep (60m), network restore (30m), VM restore (120m), verification (30m).
- Quarterly DR drills validate 45m actual RTO (<4h target) and RPO objectives.

**Outcome:** 87% faster recovery than 4h target, 3-2-1 rule satisfied, documentation updated after each drill.
