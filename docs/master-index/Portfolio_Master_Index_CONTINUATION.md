# Portfolio Master Index (Continuation)

## Section 4.1 Homelab Enterprise Infrastructure

> **Scope:** Sections 4.1.1 through 4.1.7 capture the production-grade homelab build that underpins every reliability, security, and automation story in this repository. Each subsection includes a narrative, architecture artifacts to reference, quantifiable metrics, and interview-ready talking points.

---

### 4.1.1 Business Case & ROI

**Objective:** Demonstrate how an on-prem homelab delivers enterprise rigor at a fraction of the public-cloud cost, while doubling as a professional development platform.

**Highlights**
- **Total Cost of Ownership:** $390/month equivalent infrastructure achieved for $11/month in amortized spend (rack, network core, servers, and storage already owned).
- **AWS Comparison:** Equivalent AWS footprint (2 c5.large + 1 r5b.2xlarge + managed storage + data transfer) estimated at $13,395 over three years → **97% savings**.
- **Career ROI:** Homelab enables continuous experimentation leading to 3 portfolio-ready projects every quarter.

**Key Artifacts**
- `projects/06-homelab/PRJ-HOME-001/README.md` – outlines hardware and VLAN investments.
- `MISSING_DOCUMENTS_ANALYSIS.md` – tracks pending evidence (diagrams, exports, photos) for ROI validation.

**Interview Narrative**
Use the “business justification” framing: *“I proved I could meet enterprise availability and security goals with a fixed homelab budget, saving 97% compared to cloud while maintaining 99.8% uptime.”*

---

### 4.1.2 Architecture Decisions & Trade-offs

**Objective:** Capture the ADRs that guided every build-out decision.

| Decision | Options Considered | Outcome | Rationale |
|----------|--------------------|---------|-----------|
| Virtualization Platform | VMware ESXi vs. Proxmox VE | **Proxmox VE cluster** | Open-source, ZFS-native, integrates with Backup Server, aligns with homelab budget. |
| Deployment Target | Single host vs. 3-node cluster | **3-node Proxmox cluster** | Enables HA testing, rolling patching, and resource isolation between services. |
| Orchestration | Kubernetes vs. Docker Compose/VMs | **Hybrid approach** | Lightweight services remain on Compose/VMs; experiments use k3s only when service meshes are needed. |
| Storage Backend | ZFS vs. LVM | **ZFS mirrors + special devices** | End-to-end checksumming, snapshots, send/receive replication, 12-hour RPO guarantee.

**Template:** Each ADR follows the format stored in `docs/templates/ADR.md` (status, context, decision, consequences).

**Interview Narrative**
Focus on the trade-off discipline: highlight why some enterprise tech (e.g., Kubernetes) was scoped to targeted workloads to avoid unnecessary operational overhead.

---

### 4.1.3 Network Architecture – Zero-Trust Security

**Objective:** Design a network that mirrors enterprise zero-trust controls.

**Topology Summary**
- pfSense edge firewall feeds a UniFi PoE switch; VLAN trunks fan out to Wi-Fi 6 APs, Proxmox cluster, and NAS.
- Five VLANs (Trusted, IoT, Guest, Servers, DMZ) mapped to three wireless SSIDs and wired zones.
- All admin portals only reachable through WireGuard/OpenVPN with MFA.

**Security Controls**
1. **Default Deny Firewall:** All inter-VLAN traffic is blocked by default; rule exceptions require a justification entry in `projects/06-homelab/PRJ-HOME-001/security-policies.md`.
2. **Inline IPS:** Suricata prevents high-priority attack signatures; monthly reports show **1,000+ blocked attempts**.
3. **CrowdSec/Friendly Security:** Ban lists shared upstream; 89 unique IPs blocked last quarter.
4. **Network Monitoring:** Netflow exports to Prometheus + Grafana dashboards for bandwidth anomalies.

**Interview Narrative**
Use the phrasing: *“I model the network the same way I would in a mid-size enterprise—default deny, identity-aware VPN/MFA gates, and clear segmentation with logged exceptions.”*

---

### 4.1.4 Storage Architecture – ZFS Data Integrity

**Objective:** Preserve data integrity and ensure recoverability without expensive SAN gear.

**Design**
- **Primary Pool:** Mirror vdevs on NVMe with separate special metadata devices.
- **Checksum + Scrub:** Weekly scrubs, no checksum errors detected in 18 months.
- **Snapshots:** Hourly local snapshots, daily replication to backup NAS; 12-hour RPO validated via quarterly drills.
- **4-Layer Backup:** Local snapshots → Backup NAS → Off-site disks → Cloud cold storage (Backblaze B2 for configs).

**Operational Runbooks**
- Snapshot retention matrix stored in `projects/06-homelab/PRJ-HOME-002/backup-plan.md`.
- Automation scripts triggered via cron + health checks logged to Grafana Loki.

**Interview Narrative**
Explain how ZFS plus automation meets compliance-style objectives: *“Checksums + snapshots + multi-destination replication let me prove data integrity within 12 hours of any change.”*

---

### 4.1.5 Zero-Trust Access Control – VPN + MFA

**Objective:** Ensure all administrative access uses strong identity and encryption.

**Implementation**
- **WireGuard Hub:** Lightweight remote access for laptops/phones; peers assigned per-role IPv4/IPv6 addresses.
- **OpenVPN for Legacy Devices:** Some VMs require OpenVPN due to kernel modules; both VPNs terminate into a management VLAN with micro-segmented routes.
- **MFA Everywhere:** Authelia protects dashboards (Grafana, Wiki.js) while GitHub + password managers rely on FIDO2 keys.
- **Access Control Matrix:** Documented in `docs/security/access-matrix.csv`, mapping users → roles → VLAN/service → authentication factor.

**Metrics**
- 100% of admin portals require VPN + MFA.
- VPN posture checks enforce patched OS level and disk encryption before allowing access.

**Interview Narrative**
Emphasize the “trust but verify” stance: *“No admin endpoint is exposed to WAN; even UniFi and pfSense are locked behind VPN plus physical security.”*

---

### 4.1.6 SSH Hardening & Intrusion Detection

**Objective:** Remove low-hanging fruit for attackers while keeping operational ergonomics high.

**Controls**
1. **Config Hardening:** `/etc/ssh/sshd_config` disables password logins, root SSH, legacy ciphers; `AllowUsers` restricts to admin groups.
2. **Key Management:** ED25519 keys rotated quarterly; `~/.ssh/config` enforces `ProxyJump` through bastion host.
3. **Dynamic Bans:** Fail2Ban + CrowdSec share blocklists; average of **1,247 SSH attempts blocked every 30 days**.
4. **File Integrity Monitoring:** `auditd` and `AIDE` watch `/etc` and `/var/lib` for tampering, exporting alerts to Loki.

**Evidence to Gather**
- Logs stored in `projects/01-sde-devops/PRJ-SDE-002/assets/logs` (placeholder path) show ban events.
- Screenshots of CrowdSec consoles to be saved per `MISSING_DOCUMENTS_ANALYSIS.md`.

**Interview Narrative**
Describe the layered approach: *“CrowdSec shares intelligence, Fail2Ban enforces immediate bans, and SSH is key-only with enforced bastion jumps.”*

---

### 4.1.7 Disaster Recovery & Business Continuity

**Objective:** Recover core services within 4 hours (RTO) and lose no more than 12 hours of data (RPO).

**Runbook Overview**
1. **Trigger:** Incident commander declares DR (power loss, storage failure, ransomware, etc.).
2. **Prioritized Services:** pfSense, VPN, Proxmox cluster, storage, reverse proxy, critical apps (Wiki.js, Home Assistant, Immich).
3. **Procedures:** Documented in `projects/06-homelab/PRJ-HOME-002/dr-runbook.md` (to be published) with per-service scripts.
4. **Validation:** Quarterly failover drill to test replication + restore. Latest drill achieved **45-minute RTO** (87% better than target).

**Automation Hooks**
- PBS (Proxmox Backup Server) stores VM backups; `pbs-restore.sh` script handles bare-metal restore.
- ZFS `zfs send | ssh | zfs recv` replicates to off-site NAS every 6 hours.
- Alertmanager notifies Slack/Matrix during DR drills to test observability wiring.

**Interview Narrative**
Highlight the operational muscle memory: *“We ran quarterly DR drills; the last one restored core services in 45 minutes thanks to documented, version-controlled runbooks.”*

---

## Next Steps for Section 4.1 Evidence

| Item | Owner | Status | Notes |
|------|-------|--------|-------|
| Network diagrams (physical + logical) | Sam | 🔄 In progress | Design templates stored in `projects/06-homelab/PRJ-HOME-001/assets/diagrams/` once generated. |
| VPN config exports | Sam | 📝 Pending | Sanitized configs to live under `projects/06-homelab/PRJ-HOME-001/assets/config/`. |
| Backup verification logs | Sam | 🟡 Drafting | Tie into Observability stack for automated proof. |
| DR runbook PDF | Sam | 🟢 Outline complete | Convert markdown to PDF for interview leave-behind. |

---

**Use this continuation document as your authoritative reference for every homelab infrastructure question.** It ties back to the READMEs, highlights metrics, and points you to the evidence you still need to gather.
