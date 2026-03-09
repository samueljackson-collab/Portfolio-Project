---
title: Risk Register
description: Portfolio documentation page
tags: [cryptography, documentation, portfolio, quantum-computing]
path: portfolio/p21-quantum-safe-cryptography/risk-register
created: 2026-03-08T22:19:13.873850+00:00
updated: 2026-03-08T22:04:38.015902+00:00
---

# Risk Register

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Sample payload lacks auth | Medium | Medium | Add API Gateway authorizers or service mesh mTLS. |
| Drift between artifacts | Low | Medium | Validate checksums during `--validate` run. |
| Missing metrics | Low | Low | Extend `METRICS/metrics.md` with service-level indicators. |
