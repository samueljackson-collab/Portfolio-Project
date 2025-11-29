# Screenshot & Evidence Collection Guide

## Portfolio Evidence Capture Checklist

This guide ensures every screenshot or artifact in the portfolio proves a measurable outcome. Follow the requirements for each capture so hiring teams can validate every metric you claim.

---

| Category | Priority | Evidence Name | Filename | Purpose |
|----------|----------|---------------|----------|---------|
| Grafana dashboards | ⭐ High | Infrastructure Overview | `grafana_infrastructure_overview_dashboard.png` | Proves real-time observability |
| Grafana dashboards | ⭐ High | SLO Tracker | `grafana_slo_tracking_dashboard.png` | Demonstrates error-budget tracking |
| Grafana dashboards | ⭐ High | Latency + Errors | `grafana_performance_metrics.png` | Shows performance headroom |
| Prometheus | ◼︎ Medium | PromQL query + alerts | `prometheus_promql_query.png`, `prometheus_alert_rules.png` | Proves metrics + alerting skills |
| Security | ⭐ High | CIS / Nmap / Fail2Ban | see filenames below | Shows zero-trust and monitoring |
| Storage | ◼︎ Medium | FIO + DD | `storage_fio_benchmark_results.png`, `storage_dd_throughput.png` | Validates performance claims |
| Network | ⭐ High | UniFi topology | `unifi_network_topology.png` | Visualizes segmentation |
| Terminal health | ◼︎ Medium | ZFS + Compose | `zfs_pool_status_healthy.png`, `docker_compose_services_running.png` | Confirms runtime state |
| Runbooks | ⭐ High | DR runbook | `disaster_recovery_runbook.pdf` | Shows operational maturity |
| GitHub | ⭐ High | Repo overview | `github_repository_overview.png` | Demonstrates structure + cadence |

Use this matrix to prioritize capture sessions before interviews.

## 1. Grafana Dashboards (High Priority)

### Infrastructure Overview Dashboard

**Steps**
1. Select *Last 24 hours* and ensure data is streaming (no `N/A`).
2. Expand the dashboard (hide side nav) so all panels are visible without scrolling.
3. Hover over the uptime table to show 99.8%+ values and the tooltip timestamp.

**Must include** CPU/Memory/Disk stat panels, Network I/O line graph, and Service Uptime table.

**Filename:** `grafana_infrastructure_overview_dashboard.png`

**Story to tell:** “Here’s the single pane that tracks fleet health and SLO compliance in real time.”

### Service Health & SLO Tracking

| Requirement | Detail |
|-------------|--------|
| Time range | Last 30 days |
| Columns | Service name, uptime %, error budget remaining |
| Rows | ≥5 services (Immich, Wiki.js, Home Assistant, Grafana, Prometheus) |
| Styling | Green/yellow/red indicators visible |

**Filename:** `grafana_slo_tracking_dashboard.png`

**Talking point:** “I alert on burn-rate instead of noisy CPU alarms; the error-budget column makes that obvious.”

### Response Time & Error Rate

**Layout checklist**
- P95 latency line chart (last 7 days) with target threshold line at 500ms.
- HTTP error rate (%) chart stacked under latency with red threshold line at 1%.
- Shared legend showing key services (Immich API, reverse proxy, wiki).

**Filename:** `grafana_performance_metrics.png`

**Narrative:** “Performance isn’t just uptime; I track latency/error trends to catch regressions before users notice.”

---

## 2. Prometheus Evidence (Medium Priority)

### PromQL Query Example

**Command path:** `https://prometheus.home/graph`

**Query to run:**

```promql
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)
```

1. Paste query, hit **Execute**, and select both **Graph** and **Table** tabs.
2. Toggle each host label so the legend reads `proxmox`, `truenas`, etc.
3. Capture the whole viewport (URL bar optional) to show PromQL proficiency.

**Filename:** `prometheus_promql_query.png`

**Usage:** “Calculates real CPU usage from idle counters; demonstrates comfort with PromQL math.”

### Alert Rules

- Navigate to `https://prometheus.home/alerts`.
- Filter for `severity=page` so critical alerts are shown first.
- Ensure at least one **FIRING** or **PENDING** example is visible (e.g., `SLOBurnRateFast`), plus a **Normal** entry.

**Filename:** `prometheus_alert_rules.png`

**Usage:** “Shows that every alert has severity/state labels and routes to Alertmanager.”

---

## 3. Security Scans (High Priority)

### OpenSCAP CIS Benchmark

```bash
sudo oscap xccdf eval \
  --profile xccdf_org.ssgproject.content_profile_cis \
  --report /tmp/cis-$(date +%F).html \
  /usr/share/xml/scap/ssg-content/ssg-ubuntu2204-ds.xml | tee cis.txt
```

- Keep the terminal output visible showing **Score 92.3%** and category breakdown.
- Mention the HTML report path in the screenshot to show traceability.

**Filename:** `openscap_cis_compliance_scan.png`

**Usage:** “Monthly CIS scan proves 92% compliance; HTML report available in repo.”

### Nmap External Scan

```bash
nmap -Pn -sS -sU -p- my.public.ip.address
```

- Highlight the single allowed port (`51820/udp open`), annotate others as `filtered`.
- Use `date` command beforehand so the prompt shows capture date.

**Filename:** `nmap_external_security_scan.png`

**Usage:** “Confirms only VPN is reachable from WAN; no admin surfaces exposed.”

### Fail2Ban Status

```bash
sudo fail2ban-client status sshd
sudo fail2ban-client status crowdsec
```

- Capture both summary lines and the list of recently banned IPs.
- Include the terminal clock/prompt to reinforce recency.

**Filename:** `fail2ban_blocked_ips.png`

**Usage:** “1,200+ SSH brute-force attempts blocked this month.”

---

## 4. Storage Benchmarks (Medium Priority)

### FIO Random IOPS Test

```bash
fio --name=randrw --rw=randrw --bs=4k --iodepth=32 --numjobs=4 \
    --size=20G --runtime=120 --time_based --group_reporting \
    --filename=/tank/benchmarks/fio-test.img
```

- Keep the command plus the final summary block (IOPS, BW, latency percentiles).
- Highlight the line showing **read IOPS 12,450** and **write IOPS 9,876**.

**Filename:** `storage_fio_benchmark_results.png`

**Usage:** “Backs up the 24% performance headroom claim.”

### DD Sequential Throughput

```bash
sudo dd if=/dev/zero of=/tank/benchmarks/dd-test.img bs=1M count=20000 oflag=direct status=progress
sudo dd if=/tank/benchmarks/dd-test.img of=/dev/null bs=1M iflag=direct status=progress
```

- Keep the `status=progress` bar visible plus the final MB/s summary.
- Run `date` before/after so the prompt shows capture date.

**Filename:** `storage_dd_throughput.png`

**Usage:** “Shows sequential throughput at ~596 MB/s read / 511 MB/s write.”

---

## 5. Network Topology (High Priority)

### UniFi Network Map

- Open UniFi → Topology → select *Show VLANs*.
- Hover over each network to display VLAN IDs (10/20/30/40/50) and subnets.
- Expand the sidebar that lists firewall rules so “x Rules” is visible.

**Filename:** `unifi_network_topology.png`

**Usage:** “Visual explanation of the 5-VLAN zero-trust layout.”

---

## 6. Terminal Evidence (Medium Priority)

### ZFS Pool Health

```bash
sudo zpool status tank
sudo zpool list tank
```

- Capture mirror members, scrub date, and `errors: 0` lines.
- Optional: include `smartctl -H` snippet for each disk in the same screenshot.

**Filename:** `zfs_pool_status_healthy.png`

**Usage:** “Shows mirrored NVMe pool with clean checksums.”

### Docker Compose Services

```bash
cd /opt/compose/services
docker compose ps
docker compose ls
```

- Terminal width ≥120 cols so the entire table (Name, Command, State, Ports) is readable.
- Highlight services with dependencies (e.g., Immich API + PostgreSQL) to show multi-tier orchestration.

**Filename:** `docker_compose_services_running.png`

**Usage:** “Demonstrates everything is running via declarative Compose files.”

---

## 7. Runbooks (High Priority)

### Disaster Recovery Runbook

**Document layout:**

| Section | Must show |
|---------|-----------|
| Scenario | “Primary storage failure” or similar |
| RTO/RPO | Numeric targets (e.g., RTO 1h, RPO 15m) |
| Procedure | Step-by-step list with numbering |
| Verification | Command output or checklist confirming success |
| Success Criteria | Bullet list tied to business impact |

Export as PDF named `disaster_recovery_runbook.pdf` and include page numbers.

---

## 8. GitHub Repository Evidence (High Priority)
```
Requirements:
- GitHub repo overview
- Show folder structure (configs/, docs/, scripts/)
- Display README preview + latest commits
- Include Insights → Commits sparkline to highlight cadence
Filename: github_repository_overview.png
Usage: Confirms documentation + code hygiene
```

---

## Capture Best Practices

- Set terminal to 120x40 with light theme
- Clear old commands before capturing
- Include date/time stamp when possible
- Mask sensitive IPs but keep structure readable
- Capture full context—no cropped legends
- Store files using the filenames listed in this guide
- Commit raw artifacts under `docs/evidence/<category>/` with README pointers so reviewers can trace claims

*Portfolio Supporting Materials – Screenshot & Evidence Guide*
