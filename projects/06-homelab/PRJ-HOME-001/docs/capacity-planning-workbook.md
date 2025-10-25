# Capacity Planning Workbook
**Project:** PRJ-HOME-001 – UniFi Home Network

---

## 1. Current Baseline (May 2024)
| Resource | Current Avg | Peak Observed | Provisioned Capacity | Utilization |
| --- | --- | --- | --- | --- |
| Internet Bandwidth | 420 Mbps | 680 Mbps | 1 Gbps | 68% peak |
| WAN Latency (Seattle target) | 14 ms | 24 ms | SLA < 30 ms | Within SLA |
| Switch PoE Budget | 162 W | 192 W | 250 W | 77% peak |
| UDM-Pro CPU | 32% | 58% | 100% | Healthy |
| Wi-Fi Clients / AP | 18 | 33 | 60 | 55% peak |
| UniFi Protect Storage | 5.2 TB used | 5.4 TB | 8 TB | 67% |

## 2. Growth Forecast
Assumptions:
- Add 2 indoor APs for future expansion (guest house) within 12 months.
- Add 4 IoT devices per quarter (smart sensors, cameras).
- Internet usage grows 12% QoQ due to streaming and remote work.

| Metric | Growth Model | 6-Mo Forecast | 12-Mo Forecast | Notes |
| --- | --- | --- | --- | --- |
| Internet Peak | 680 Mbps × (1.12^2) | 854 Mbps | 1,073 Mbps | Upgrade to 2 Gbps circuit at 12 mo |
| PoE Load | +12 W per quarter | 204 W | 216 W | Within 250 W but consider second PoE switch |
| Wi-Fi Clients/AP | +4 clients per AP per quarter | 25 | 33 | Approach 60-client ceiling by 18 mo |
| Protect Storage | +0.4 TB per quarter | 6.0 TB | 6.8 TB | Expand HDD to 12 TB at 12 mo |

## 3. Upgrade Recommendations
- **0–6 Months:**
  - Monitor PoE draw monthly; pre-stage second 16-port PoE switch for quick install.
  - Purchase additional 8 TB HDD for Protect to enable future RAID1.
- **6–12 Months:**
  - Engage ISP for 2 Gbps fiber plan; verify UDM-Pro Smart Queues sizing.
  - Add Wi-Fi 6E AP in upstairs hallway if client density exceeds 30 per AP.
- **12+ Months:**
  - Evaluate UDM-SE or gateway redundancy if remote work dependency increases.
  - Consider mesh link to detached structures (if constructed) using UniFi Building Bridge.

## 4. Monitoring Thresholds
| Metric | Warning | Critical | Automated Action |
| --- | --- | --- | --- |
| PoE Budget | > 80% sustained 5 min | > 90% | Alert + block port adoption |
| Internet Peak Usage | > 85% circuit capacity | > 95% for 10 min | Alert + capture NetFlow sample |
| Storage Utilization | > 80% | > 90% | Alert + prune old motion events |
| AP Client Count | > 40 | > 50 | Alert + suggest AP roaming tuning |

## 5. Review Cadence
- Monthly: Review Grafana dashboards, update baseline table if trends change.
- Quarterly: Recalculate forecasts with new actuals, align with budget planning.
- Annually: Revisit architecture for modernization (Wi-Fi 7 adoption, backup internet link).

