# Network Troubleshooting Guide

## Service Won't Start
- **Symptoms:** UDMP offline or switch/AP disconnected.
- **Diagnosis:** Ping management IPs; check controller dashboard for heartbeat; verify UPS power.
- **Resolution:** Reboot affected device via controller; reseat cables; confirm DHCP on management VLAN.
- **Prevention:** UPS maintenance, firmware updates during maintenance windows.

## High Memory Usage
- **Symptoms:** UDMP performance degrade, controller slow.
- **Diagnosis:** UDMP dashboard resources; check IDS/IPS load.
- **Resolution:** Disable unused features, reduce logging retention, schedule reboot during low usage.
- **Prevention:** Keep firmware current; avoid excessive DPI categories.

## Prometheus Scrape Failures (for homelab monitors)
- **Symptoms:** `up`=0 for node-exporter/cadvisor in monitoring stack.
- **Diagnosis:** Verify VLAN40 server reachability; confirm firewall rules allow monitoring.
- **Resolution:** Open required ports (9100/8080) from monitoring VLAN; restart exporters.
- **Prevention:** Document monitoring ACLs in firewall and keep consistent tagging.

## Alert Not Firing
- **Symptoms:** Conditions visible but no alerts.
- **Diagnosis:** Check Alertmanager silences; validate SMTP/Slack connectivity; inspect `prometheus_rule_evaluation_failures_total`.
- **Resolution:** Clear silences, fix webhook credentials, correct rule syntax.
- **Prevention:** Test alerts quarterly with amtool.

## Dashboard Not Loading
- **Symptoms:** Grafana unreachable from Trusted VLAN.
- **Diagnosis:** Ensure reverse proxy/localhost binding in monitoring stack; check firewall rules.
- **Resolution:** SSH tunnel or adjust proxy; ensure port 3000 allowed from Trusted to monitoring host.
- **Prevention:** Keep documentation of access paths and update when topology changes.

## Logs Not Appearing
- **Symptoms:** Loki queries empty.
- **Diagnosis:** Verify Promtail permissions on Docker log path; check label filters in dashboards.
- **Resolution:** Fix Promtail file mounts, restart agent, reduce label filters to `job`/`host`.
- **Prevention:** Validate after upgrades with health-check script.

## Container Restart Loops
- **Symptoms:** Monitoring containers repeatedly restarting.
- **Diagnosis:** `docker compose logs` for stack traces; validate .env and permissions; check health checks.
- **Resolution:** Correct config paths, expand start_period for slow services, ensure volumes writable.
- **Prevention:** Run validation before deploy; stagger upgrades.
