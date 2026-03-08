---
title: Playbook: Initiate Controlled Failover
description: 1. **Notify** stakeholders and freeze writes on primary. 2. **Trigger** failover by setting health check to fail via `jobs/toggle_primary.sh down`. 3. **Validate** secondary receives traffic; monitor 
tags: [documentation, portfolio]
path: portfolio/p10-multi-region/failover
created: 2026-03-08T22:19:14.023683+00:00
updated: 2026-03-08T22:04:38.129902+00:00
---

# Playbook: Initiate Controlled Failover

1. **Notify** stakeholders and freeze writes on primary.
2. **Trigger** failover by setting health check to fail via `jobs/toggle_primary.sh down`.
3. **Validate** secondary receives traffic; monitor `consumer/validate.py` metrics.
4. **Promote** secondary DB (simulated) and enable writes.
5. **Document** results in `REPORT_TEMPLATES/failover_report.md`.
