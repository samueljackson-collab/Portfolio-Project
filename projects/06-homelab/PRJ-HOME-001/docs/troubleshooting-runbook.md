# Troubleshooting Runbook Index
This runbook references detailed procedures contained in the [Troubleshooting Playbook](./troubleshooting-playbook.md). Use this quick index to map common symptoms to their associated playbook sections and supporting evidence requirements.

| Symptom | Likely Layer | Playbook Section | Validation Steps | Artifacts |
| --- | --- | --- | --- | --- |
| Wireless client drops | RF / Layer 2 | §3, §5 | Check channel utilization, RSSI heatmap, run `iperf3` | Grafana screenshot, RF scan export |
| Camera offline | Layer 1/2 | §2 | Verify PoE power, cable test, inspect junction box | Photo of cabling, PoE budget report |
| Doorbell unresponsive | Layer 2/3 | §3, §4 | Confirm VLAN assignment, DHCP lease, firewall rules | DHCP logs, firewall screenshot |
| WAN outage | Layer 3 | §4 | Ping ISP gateway, check ONT, escalate to ISP | Ping output, ISP ticket number |
| High latency | Performance | §5 | Run `iperf3`, inspect Smart Queue load, check WAN graphs | Grafana export, Smart Queue config |

**Evidence Storage Path:** `projects/06-homelab/PRJ-HOME-001/artifacts/incidents/<date-case>/`

Update this index whenever new scenarios are documented to maintain quick lookup during on-call triage.

