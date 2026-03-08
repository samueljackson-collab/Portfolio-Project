---
title: ADR-001: Contract Tests as Gate for Deployments
description: - **Status:** Accepted - **Context:** APIs are versioned but occasionally change without notice. We need early detection of breaking changes. - **Decision:** Make contract tests blocking in CI/CD; no 
tags: [documentation, portfolio]
path: portfolio/p08-api-testing/adr-001-contract-tests
created: 2026-03-08T22:19:13.992610+00:00
updated: 2026-03-08T22:04:38.093902+00:00
---

# ADR-001: Contract Tests as Gate for Deployments
- **Status:** Accepted
- **Context:** APIs are versioned but occasionally change without notice. We need early detection of breaking changes.
- **Decision:** Make contract tests blocking in CI/CD; no deploy if drift detected.
- **Consequences:**
  - Ensures consumers are protected; adds gate time (~2 minutes) per pipeline.
  - Requires API owners to update schemas promptly.
