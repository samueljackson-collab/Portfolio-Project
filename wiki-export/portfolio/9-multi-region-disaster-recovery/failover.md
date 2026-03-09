---
title: Failover Runbook
description: 1. Review CloudWatch dashboards for anomalies. 2. Execute `scripts/failover-drill.sh` with the active global cluster ID. 3. Confirm Route53 health checks mark primary region unhealthy. 4. Validate app
tags: [documentation, portfolio]
path: portfolio/9-multi-region-disaster-recovery/failover
created: 2026-03-08T22:19:13.409148+00:00
updated: 2026-03-08T22:04:38.788902+00:00
---

# Failover Runbook

1. Review CloudWatch dashboards for anomalies.
2. Execute `scripts/failover-drill.sh` with the active global cluster ID.
3. Confirm Route53 health checks mark primary region unhealthy.
4. Validate application availability from synthetic monitors.
5. Document timeline and metrics in incident tracker.
