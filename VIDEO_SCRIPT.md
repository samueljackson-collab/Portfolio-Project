# 5-Minute Portfolio Video Demo Script

**Total Runtime:** 5 minutes  
**Format:** Screen recording with voiceover  
**Recording Tool:** OBS Studio or Loom

---

## Slide 1 – Title (10s)
**Visual:** Title slide with name + role  
**Script:**
"Hi, I'm Sam Jackson, and this is a 5-minute walkthrough of my technical portfolio. I'll show you how I built enterprise-grade infrastructure achieving 99.8% uptime while saving 97% compared to cloud alternatives."

---

## Segment 1 – Architecture Overview (60s)
**Visual:** Network topology diagram (Architecture_Diagrams_Collection.md)  
**Script:**
"Let's start with the network architecture. I designed a zero-trust security model with 5 VLANs: Management, Services, Clients, Cameras, and Guest. Each VLAN is isolated with default-deny firewall rules.

The only port exposed to the internet is WireGuard VPN on port 51820. All admin access requires VPN plus multi-factor authentication, similar to AWS VPC + security group principles.

Inter-VLAN traffic is blocked by default. A compromised camera in VLAN 40 cannot reach VLAN 10 where Proxmox and TrueNAS live. That's defense-in-depth."

---

## Segment 2 – Grafana Monitoring (90s)
**Visual:** Grafana Infrastructure Overview dashboard  
**Script:**
"Next, observability. This dashboard tracks all infrastructure in real-time.

CPU, memory, disk, and network stats show overall host health—currently 45% CPU, 65% memory, 59% disk utilization.

Here's the service uptime table. Immich, my photo service, is at 99.87% uptime over the last 30 days. The target is 99.5%, so I'm exceeding the SLO. Error budget remaining is highlighted here—Immich has only used 5.6 minutes, so 37.4 minutes remain.

Alerts trigger on error budget burn rate, not just raw metrics like CPU. That reduces alert fatigue by 75% and ensures I only get paged when reliability is at risk."

---

## Segment 3 – Security Evidence (60s)
**Visual:** OpenSCAP scan, Nmap results, Fail2Ban status  
**Script:**
"Security is critical. Monthly CIS compliance scans score 92.3%, with 82 of 89 controls passing; the remainder are documented exceptions.

This Nmap scan of my public IP shows only the VPN port is reachable—SSH, HTTPS, and Proxmox admin are all blocked externally.

Fail2Ban and CrowdSec have blocked 1,247 SSH brute-force attempts this month. No successful breaches so far."

---

## Segment 4 – Performance Benchmarks (45s)
**Visual:** Terminal with `fio` results + Grafana latency chart  
**Script:**
"Performance: Storage benchmarks on the ZFS mirrored pool deliver 12,450 read IOPS and 9,876 write IOPS with 2.3 ms p95 latency. Sequential throughput hits 596 MB/s read and 511 MB/s write.

In production, p95 latency for the photo service is under 200 ms against a 500 ms target—over 2.5x better than required."

---

## Segment 5 – Automation & CI/CD (45s)
**Visual:** GitHub Actions workflow diagram  
**Script:**
"Automation keeps everything consistent. This GitHub Actions pipeline has six stages: Build, Test, Artifacts, Staging, Manual Approval, Production. Tests cover lint, unit, integration, and E2E, plus Snyk and Trivy security scans.

Deployments follow a blue-green pattern for zero downtime and instant rollback. This pipeline cut deployment time from two hours to 15 minutes and eliminated manual errors entirely."

---

## Segment 6 – Disaster Recovery (30s)
**Visual:** DR architecture diagram + RTO/RPO table  
**Script:**
"Disaster recovery follows the 3-2-1 rule. ZFS snapshots cover rapid restores, local backups protect against hardware failure, and offsite replication spans two geographic locations. Quarterly DR drills validate RTO of 45 minutes and RPO under four hours."

---

## Closing – Key Metrics (30s)
**Visual:** Summary slide with top metrics  
**Script:**
"To wrap up: 97% cost savings versus AWS, 99.8% uptime, zero security breaches, 480 hours per year of toil eliminated, and storage performance exceeding targets by 24%. Thanks for watching—connect with me at andrewvongsady.com."

---

## Recording Tips
- Clean desktop, hide bookmarks
- Light mode for Grafana, large fonts for terminal
- Test mic + camera before recording
- If you misspeak, pause 3 seconds and re-read the line for easy editing
- Trim intro/outro, add light fades, and upload to YouTube/LinkedIn

*Portfolio Supporting Materials – Video Script*
