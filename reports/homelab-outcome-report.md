# Homelab Program — Outcome & Evidence Report

**Updated:** November 18, 2025  
**Owner:** Samuel Jackson  
**Scope:** PRJ-HOME-001 (Secure Network), PRJ-HOME-002 (Virtualisation & Core Services), PRJ-HOME-004 (Program Proposal)

---

## 1. Executive Summary

The homelab initiative has progressed from a proposal deck into a fully documented, production-style environment. Key achievements include:

- ✅ Segmented UniFi/pfSense network with defence-in-depth controls and detailed runbooks (PRJ-HOME-001)
- ✅ Highly-available Proxmox + TrueNAS core services cluster with automated backups, DR rehearsals, and observability hooks (PRJ-HOME-002)
- ✅ Executive-ready programme documentation aligning technical artefacts with business goals and KPIs (PRJ-HOME-004)

These deliverables demonstrate enterprise-grade design, operational rigour, and documentation quality suitable for recruiters, hiring managers, and consulting clients.

---

## 2. Programme Overview

| Capability | Summary | Primary Evidence |
|------------|---------|------------------|
| **Network Foundation** | Five-VLAN pfSense architecture with Suricata IPS, OpenVPN, and WPA3 Enterprise Wi-Fi. | [`projects/06-homelab/PRJ-HOME-001/README.md`](../projects/06-homelab/PRJ-HOME-001/README.md) |
| **Core Services Platform** | 3-node Proxmox cluster, Ceph storage tiers, PBS backups, Wiki.js/Home Assistant/Immich stack. | [`projects/06-homelab/PRJ-HOME-002/README.md`](../projects/06-homelab/PRJ-HOME-002/README.md) |
| **Programme Narrative** | Business case, KPIs, budget, risk, and implementation timeline. | [`projects/06-homelab/PRJ-HOME-004/README.md`](../projects/06-homelab/PRJ-HOME-004/README.md) |
| **Operations** | Daily/weekly/incident/disaster runbooks for network and services. | [`projects/06-homelab/PRJ-HOME-001/RUNBOOK.md`](../projects/06-homelab/PRJ-HOME-001/RUNBOOK.md), [`projects/06-homelab/PRJ-HOME-002/assets/runbooks/`](../projects/06-homelab/PRJ-HOME-002/assets/runbooks/) |
| **Observability** | Prometheus/Grafana/Loki stack measuring homelab services with PBS integration. | [`projects/01-sde-devops/PRJ-SDE-002/`](../projects/01-sde-devops/PRJ-SDE-002/) |

---

## 3. Evidence Map

| Area | Artefact Highlights | Notes |
|------|--------------------|-------|
| **Network Design** | `assets/diagrams/physical-topology.mermaid`, `assets/documentation/network-architecture.md`, `assets/configs/firewall-rules-matrix.md` | Shows rack layout, VLAN segmentation, firewall rules, and SSID posture.
| **Configuration Management** | `assets/pfsense/pfsense-config.xml`, `assets/unifi/unifi-config.json`, `assets/configs/wifi-ssid-matrix.md` | Sanitised exports suitable for replication or review.
| **Operational Runbooks** | `assets/runbooks/network-deployment-runbook.md`, `RUNBOOK.md` | Covers greenfield deployment, maintenance, incident response, and recovery testing.
| **Virtualisation & Services** | `PRJ-HOME-002/assets/configs/docker-compose-full-stack.yml`, `assets/automation/ansible/playbooks/`, `assets/proxmox/backup-config.json` | Demonstrates infrastructure-as-code, service orchestration, and backup automation.
| **Disaster Recovery** | `PRJ-HOME-002/assets/recovery/`, `PRJ-HOME-004/assets/documentation/runbooks/disaster-recovery.md` | Aligns technical procedures with programme-level RTO/RPO commitments.
| **Observability & Backups** | `PRJ-SDE-002/assets/grafana/dashboards/`, `assets/prometheus/prometheus.yml`, `assets/logs/README.md` | Provides metrics, alerting policies, backup verification scripts, and retention summaries.

---

## 4. Outcomes Against KPIs

| KPI | Target (PRJ-HOME-004) | Evidence | Status |
|-----|-----------------------|----------|--------|
| **Availability** | ≥ 99.9% uptime (90 days) | Grafana SLO dashboards + operational runbooks | 🟢 Ready (monitoring + runbooks in place)
| **Security** | 0 WAN-exposed admin interfaces | pfSense/UniFi config exports, firewall matrices | 🟢 Enforced (VPN-only admin access)
| **Data Protection** | RPO ≤ 24h, RTO ≤ 4h | PBS backup logs, DR runbooks, snapshot schedules | 🟢 Achieved (automation + rehearsal docs)
| **Observability** | Actionable dashboards + low-noise alerts | Prometheus/Grafana configs, alert runbooks | 🟢 Achieved
| **Family Service UX** | Elder-friendly photo sharing | Immich deployment plan + accessibility notes in proposal | 🟠 In progress (Phase 2 service UX polish)

---

## 5. Cross-Project Integrations

- **Observability Alignment:** PRJ-SDE-002 provides monitoring, alerting, and PBS verification that instrument both homelab projects.
- **Documentation Fabric:** Programme proposal (PRJ-HOME-004) now links directly to evidence folders, enabling seamless narrative from business objectives to technical proof.
- **Automation Hooks:** Ansible/Terraform scaffolding in PRJ-HOME-002 aligns with infrastructure modules planned in PRJ-SDE-001 for future hybrid deployments.

---

## 6. Recommendations & Next Steps

1. **Visual Enhancements:** Capture optional Wi-Fi heatmaps, rack photos, and service UI screenshots to complement technical docs.
2. **Recruiter Packet:** Reference this outcome report in resume variants and PR descriptions to highlight end-to-end delivery.
3. **Resume Integration:** Link the new portfolio evidence packs directly inside each tailored resume and cover letter to reinforce credibility.
4. **Phase 2 Focus:** Continue Immich UX validation and multi-site replication testing per PRJ-HOME-004 timeline.
5. **Public-Friendly Summaries:** Consider exporting condensed PDFs (proposal + outcome highlights) for stakeholders who prefer slide-style collateral.

---

## 7. Change Log

| Date | Update | Author |
|------|--------|--------|
| 2025-11-18 | Initial outcome report consolidating homelab evidence and KPI alignment. | Samuel Jackson |
