# Monitoring Dashboard Specification
**Dashboard ID:** HOME-NET-001  \
**Platform:** Grafana 10.x  \
**Data Sources:** Prometheus, InfluxDB, Elasticsearch

---

## 1. Dashboard Layout
| Row | Panels | Description |
| --- | --- | --- |
| 1 | WAN Status (stat), Latency (graph), Packet Loss (stat) | Real-time WAN health |
| 2 | PoE Budget (gauge), Switch Port Errors (table) | Power & layer-1 health |
| 3 | Wireless Client Count (graph), RSSI Heatmap (geomap), Channel Utilization (bar) | RF insight |
| 4 | Protect Recording Uptime (table), Storage Utilization (gauge) | Video surveillance |
| 5 | Security Events (bar), IDS Severity (pie) | Threat monitoring |
| 6 | Alert Summary (table), Change Log Highlights (text panel) | Operations snapshot |

## 2. Panel Details
- **WAN Status (Stat):** Displays `up`/`down` via Prometheus metric `probe_success`; color-coded (green/red).
- **Latency Graph:** `probe_latency_seconds` with 95th percentile annotation lines.
- **PoE Budget Gauge:** Prometheus query `sum(unifi_switch_poe_power)` vs `unifi_switch_poe_max_power`.
- **Wireless Client Count:** Query `sum(unifi_ap_clients)` with thresholds (green < 30, yellow 30-45, red > 45).
- **RSSI Heatmap:** Custom panel using InfluxDB data exported from UniFi; overlays floor plan SVG.
- **Protect Recording Uptime:** Table showing each camera's last recording timestamp; highlight > 5 min gaps.
- **Security Events:** Elasticsearch query on IDS logs; stacked by severity.
- **Alert Summary:** Displays unresolved Alertmanager alerts with severity, age, assigned owner.

## 3. Variables
| Variable | Type | Source | Usage |
| --- | --- | --- | --- |
| `site` | Query | Prometheus label `site` | Filter for additional locations in future |
| `ap_group` | Query | Prometheus label `ap_group` | Drill into Downstairs/Upstairs/Outdoor |
| `camera` | Query | InfluxDB measurement `protect_camera_events` | Filter Protect panels |

## 4. Annotations & Alerts
- **Annotations:**
  - Change events pulled from `change-log.md` (converted via webhook) overlayed on latency graph.
  - Power events from UPS SNMP traps annotated on PoE row.
- **Panel Alerts:**
  - WAN status stat triggers Grafana alert when `probe_success == 0` for 2 polls.
  - PoE gauge alert at > 85% for 5 minutes.
  - Recording uptime table triggers alert if `last_recording_age > 300` seconds.

## 5. Access & Sharing
- Dashboard accessible to admin users (MFA required) and read-only viewers for homeowner.
- Night mode default for readability in NOC display.
- Export PDF weekly via Grafana schedule; send to `reports/` folder and email distribution list.

## 6. Maintenance
- Update floor plan overlay annually or after remodel.
- Review panel queries quarterly to ensure compatibility with exporter upgrades.
- Archive JSON export of dashboard to repository under `assets/dashboards/HOME-NET-001.json` after each major change.

