# Monitoring & Alerting Strategy
**Project:** PRJ-HOME-001 – UniFi Home Network  \
**Tools:** UniFi Network Application, UniFi Protect, Prometheus, Grafana, Alertmanager

---

## 1. Monitoring Architecture
- **Data Sources:**
  - UniFi Network Application metrics via `unifi_exporter` (Prometheus scrape).
  - UniFi Protect event stream forwarded to InfluxDB for camera analytics.
  - UDM-Pro syslog forwarded to Elastic stack for log correlation.
  - UPS SNMP traps to Prometheus `snmp_exporter`.
- **Dashboards:**
  - Grafana board `HOME-NET-001` with panels for WAN health, PoE utilization, wireless KPIs.
  - Protect dashboard showing camera uptime, motion event counts, storage consumption.

## 2. Key Metrics
| Category | Metric | Target |
| --- | --- | --- |
| Availability | WAN up/down status | 99.9% monthly |
| Performance | WAN latency, jitter, packet loss | < 30 ms, < 15 ms, < 0.1% |
| Wireless | RSSI heatmap, channel utilization | > -65 dBm, < 70% |
| Security | IDS alerts per day | < 5 (investigate spikes) |
| PoE | Total draw vs budget | < 80% |
| Storage | Protect disk usage | < 80% |

## 3. Alert Thresholds
| Alert | Warning | Critical | Notification |
| --- | --- | --- | --- |
| WAN Down | > 2 min | > 5 min | SMS + Push via Pushover |
| AP Offline | > 3 min | > 10 min | Email + Slack webhook |
| Camera Recording Gap | Any gap > 1 min | Gap > 5 min | Email |
| PoE Budget | > 80% for 5 min | > 90% | Slack + create change ticket |
| UPS on Battery | Immediate | > 10 min | SMS + initiate shutdown workflow |
| IDS Alert Spike | > 10 alerts/15 min | > 25 alerts/15 min | Slack + incident ticket |

## 4. Alert Routing & Escalation
- Alertmanager routes warnings to personal Slack channel; critical alerts escalate to SMS + email.
- Acknowledge alerts via Grafana or mobile app; auto-resolve when metric returns to normal for 5 minutes.
- After-hours notifications mirrored to Google Voice line for redundancy.

## 5. Reporting
- Weekly summary email with uptime, alert counts, and top talkers (NetFlow sample).
- Monthly capacity report exported from Grafana to PDF and stored in `reports/` directory.
- Quarterly security report summarizing IDS events, firmware status, and failed login attempts.

## 6. Maintenance & Testing
- Test alert channels quarterly by simulating WAN outage (disconnect ONT) and verifying notifications.
- Review dashboards monthly to adjust thresholds as network evolves.
- Update Prometheus scrape targets when adding new devices (APs, switches).

## 7. Integration with Runbooks
- Link relevant Grafana panels within troubleshooting playbook for quick access.
- For each alert, include runbook reference ID (e.g., `TRB-AP-OFFLINE`) to guide response steps.

