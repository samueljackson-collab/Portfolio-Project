---
title: ADR-001: Active/Passive Failover
description: - **Status:** Accepted - **Context:** Simplicity and cost control outweigh active/active complexity. - **Decision:** Use active/passive with Route 53 failover records. - **Consequences:** - Lower cost
tags: [documentation, portfolio]
path: portfolio/p10-multi-region/adr-001-failover-policy
created: 2026-03-08T22:19:14.029773+00:00
updated: 2026-03-08T22:04:38.128902+00:00
---

# ADR-001: Active/Passive Failover
- **Status:** Accepted
- **Context:** Simplicity and cost control outweigh active/active complexity.
- **Decision:** Use active/passive with Route 53 failover records.
- **Consequences:**
  - Lower cost; simpler data sync.
  - Requires drills to ensure RTO met; some cold-start latency on secondary.
