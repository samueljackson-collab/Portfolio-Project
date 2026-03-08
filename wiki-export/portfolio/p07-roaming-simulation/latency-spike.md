---
title: Playbook: Latency Spike in Visited Network
description: - Alert: `roaming_latency_p95_ms > 200` for 5m across two or more visited PLMNs. 1. **Validate** metrics and logs from impairment injector; confirm spike is not due to synthetic test. 2. **Scope** aff
tags: [documentation, portfolio]
path: portfolio/p07-roaming-simulation/latency-spike
created: 2026-03-08T22:19:13.959923+00:00
updated: 2026-03-08T22:04:38.080902+00:00
---

# Playbook: Latency Spike in Visited Network

## Trigger
- Alert: `roaming_latency_p95_ms > 200` for 5m across two or more visited PLMNs.

## Response Steps
1. **Validate** metrics and logs from impairment injector; confirm spike is not due to synthetic test.
2. **Scope** affected PLMNs using `consumer/kpis.py --window 5m --metric latency`.
3. **Mitigate** by applying throttling profile:
   ```bash
   kubectl patch configmap impairment-profiles -n roaming --patch-file k8s/patches/throttle.yaml
   ```
4. **Communicate** with roaming partners; send incident template from `REPORT_TEMPLATES/incident_report.md`.
5. **Observe** recovery for 30 minutes; ensure p95 latency < 120ms.
6. **Close** with postmortem creation and backlog action for capacity tuning.
