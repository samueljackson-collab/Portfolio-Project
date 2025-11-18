# Network Troubleshooting Guide

## Service Won't Start (UDMP/Controller)
- Verify power and PoE budget; check UPS status.
- Confirm management IP reachable (192.168.1.1); ping and SSH.
- Reboot via local console if controller UI unresponsive.

## High Memory Usage on UDMP
- Review IDS/IPS signature set; switch to balanced profile.
- Disable unused applications (Protect/Access) if not required.
- Schedule weekly reboots during maintenance window if memory fragmentation persists.

## Prometheus Scrape Failures (from monitoring stack)
- Confirm firewall rules permit monitoring VLAN to reach exporters on VLAN 40.
- Validate DNS resolving hostnames; fall back to static IPs.
- Inspect exporter logs for auth or TLS failures.

## Alert Not Firing
- Ensure Alertmanager reachable from Prometheus; check routes and inhibition rules.
- Validate rule expression in Prometheus expression browser; confirm labels match expected severity.

## Dashboard Not Loading
- Check Grafana container health and datasource connectivity; refresh provisioned dashboards.
- Clear browser cache; verify time range not empty.

## Logs Not Appearing in Loki
- Verify Promtail reading `/var/log` and docker logs; ensure positions file writable.
- Confirm firewall allows Promtail to Loki on backend network; check `loki-config.yml` retention for deletions.

## Container Restart Loops
- Inspect container logs for configuration errors; review health check definitions.
- Reduce resource limits if OOM kills visible; increase retry delay in Docker health check.

## Wireless Issues
- Check client RSSI; adjust transmit power or channel per `WIRELESS-CONFIG.md` channel plan.
- Ensure band steering not forcing legacy devices off network; temporarily disable if needed.
- Validate VLAN tagging on AP trunk ports aligns with port profile.

## WAN Outage
- Confirm modem synced; check UDMP WAN status.
- If failover available, ensure secondary interface enabled; otherwise tether via temporary hotspot on management laptop.

