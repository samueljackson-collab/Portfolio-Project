---
title: Readme.Demo Index
description: Artifacts: `dashboards/cloudwatch/vpn-ecmp.json` + `evidence/iperf.txt` *What to say (10s):* 'Both tunnels carry; kill one, traffic converges; asymmetry alert fires if paths skew.' Artifacts: `infra/a
tags: [documentation, portfolio]
path: portfolio/docs/readme-demo-index
created: 2026-03-08T22:19:14.071035+00:00
updated: 2026-03-08T22:04:37.809902+00:00
---

## Network & Routing
### Dual-tunnel ECMP (Active/Active)
Artifacts: `dashboards/cloudwatch/vpn-ecmp.json` + `evidence/iperf.txt`
*What to say (10s):* "Both tunnels carry; kill one, traffic converges; asymmetry alert fires if paths skew."

### BGP over IPsec to TGW
Artifacts: `infra/aws/terraform/vpn-bgp/` + CloudWatch alarm screenshot
*What to say:* "Dynamic routes over IPsec; alarms on TunnelState/BGP state."

### TGW hub plan
Artifacts: `infra/aws/terraform/tgw-hub/` (plan file)
*What to say:* "Regional hub avoids peering sprawl; attachments route via tables."

## DNS & Traffic Steering
### Route 53 latency + health checks
Artifacts: `infra/aws/terraform/r53-latency/` + `docs/runbooks/chaos/r53-failover-drill.md` + `evidence/dig/*.txt`
*What to say:* "Low TTL + health checks; failover within TTL; drill evidence recorded."

### Anycast decision record
Artifacts: `docs/adr/ADR-0004-anycast-vs-dns.md`
*What to say:* "Stateless/edge OK; not for sticky sessions—prefer regional VIP + DNS."

## Security & Identity
### mTLS control-plane demo & rotation
Artifacts: `docs/pki/CA-design.md` + `scripts/pki/rotate.sh` + logs
*What to say:* "Short-lived certs; rotate live; expiry alarms; strict SANs/pinning."

### Least-privilege AWS access (OIDC)
Artifacts: CI config + role trust policy snippet
*What to say:* "GitHub OIDC assumes scoped roles—no static keys—audited via CloudTrail."

## Observability & SRE
### Gateway health dashboard
Artifacts: `dashboards/cloudwatch/base.json` (Tunnel/BGP/latency/loss/capacity/change overlay)
*What to say:* "Fleet health at a glance; error-budget burn and recent changes visible."

### Prometheus + Alertmanager rules
Artifacts: `observability/prometheus/rules/kuiper-gateway.yml` + `observability/alertmanager/routes/kuiper.yaml`
*What to say:* "Labels drive routing/inhibition; alerts link runbooks."

### Post-change evidence
Artifacts: `docs/runbooks/change/tgw-vpn-change-template.md` + screenshots
*What to say:* "Prechecks→staged apply→verify→rollback; alarms muted/unmuted with timers."

## Resilience & Testing
### Satellite-like impairment (netem)
Artifacts: `scripts/netem/apply_profile.sh` + graphs in `evidence/experiments/netem/`
*What to say:* "Latency/jitter/loss injected; SLOs/alerts tuned from outcomes."

### Backups/restore proof (TrueNAS/ZFS)
Artifacts: snapshot/replication job screenshot + restore notes
*What to say:* "Replicated snapshots; periodic restore tests—evidence captured."
