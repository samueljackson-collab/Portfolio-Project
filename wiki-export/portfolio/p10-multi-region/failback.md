---
title: Runbook: Failback to Primary
description: 1. **Ensure Primary Healthy**: Verify `/healthz` passes for 15m. 2. **Sync Data**: Copy latest snapshot from secondary to primary bucket (simulated via `jobs/sync.sh`). 3. **Restore Routing**: Mark pr
tags: [documentation, portfolio]
path: portfolio/p10-multi-region/failback
created: 2026-03-08T22:19:14.030572+00:00
updated: 2026-03-08T22:04:38.131902+00:00
---

# Runbook: Failback to Primary

1. **Ensure Primary Healthy**: Verify `/healthz` passes for 15m.
2. **Sync Data**: Copy latest snapshot from secondary to primary bucket (simulated via `jobs/sync.sh`).
3. **Restore Routing**: Mark primary as healthy (`jobs/toggle_primary.sh up`) and wait for Route 53 to converge.
4. **Verify**: Run `consumer/validate.py --report out/failover.json --expect primary`.
5. **Cleanup**: Resume replication schedule; close incident with updated metrics.
