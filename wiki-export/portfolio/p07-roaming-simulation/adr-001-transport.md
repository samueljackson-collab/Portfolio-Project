---
title: ADR-001: Use gRPC for Event Transport
description: - **Status:** Accepted - **Context:** Producers and consumers exchange high-volume roaming events that need schema enforcement and low latency. - **Decision:** Use gRPC with protobuf schemas instead o
tags: [documentation, portfolio]
path: portfolio/p07-roaming-simulation/adr-001-transport
created: 2026-03-08T22:19:13.966269+00:00
updated: 2026-03-08T22:04:38.078902+00:00
---

# ADR-001: Use gRPC for Event Transport
- **Status:** Accepted
- **Context:** Producers and consumers exchange high-volume roaming events that need schema enforcement and low latency.
- **Decision:** Use gRPC with protobuf schemas instead of REST/JSON.
- **Consequences:**
  - Pros: Strong typing, streaming support, easy mTLS.
  - Cons: Extra tooling for debugging; requires proto compiler in CI.
