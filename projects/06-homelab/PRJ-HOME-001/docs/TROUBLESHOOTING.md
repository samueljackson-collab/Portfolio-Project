# Troubleshooting Guide (Network)

## Service Won't Start
- Symptom: device offline in controller.
- Diagnosis: check PoE budget and port status; confirm VLAN assignment; ping management IP.
- Resolution: re-adopt device, reseat cable, verify power; update firmware.
- Prevention: keep maintenance log and monitor PoE budget.

## High Memory Usage
- Symptom: UDMP memory alerts.
- Diagnosis: controller UI metrics, IDS/IPS load.
- Resolution: disable nonessential DPI categories, reduce logging retention, reboot during maintenance window.
- Prevention: schedule regular reboots; keep firmware current.

## Prometheus Scrape Failures
- Symptom: exporters in Servers VLAN unreachable.
- Diagnosis: check inter-VLAN rules allow HTTP/S; verify DNS resolution.
- Resolution: adjust firewall rules, ensure node exporter listening on host network.
- Prevention: document rule changes; test with curl from Prometheus host.

## Alert Not Firing
- Symptom: expected notification absent.
- Diagnosis: confirm Alertmanager route, check inhibition rules, verify SMTP/Slack keys.
- Resolution: test via `amtool`; fix credentials; adjust severity labels.

## Dashboard Not Loading
- Symptom: Grafana panel errors.
- Diagnosis: datasource health check; network path from Grafana VLAN to Prometheus/Loki.
- Resolution: fix DNS, ensure backend network reachable via compose; restart Grafana provisioning.

## Logs Not Appearing
- Symptom: no new entries in Loki.
- Diagnosis: verify Promtail access to Docker logs, check positions file, query by container label.
- Resolution: restart Promtail, fix label filters; ensure Loki retention not expired.

## Container Restart Loops
- Symptom: repeated restarts of monitoring containers.
- Diagnosis: inspect compose logs; check resource limits and health checks.
- Resolution: increase limits, fix configuration errors, correct permissions on volumes.
