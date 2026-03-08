---
title: Risk Register
description: Portfolio documentation page
tags: [cloud, documentation, iac, portfolio, terraform]
path: portfolio/p17-terraform-multicloud/risk-register
created: 2026-03-08T22:19:13.819971+00:00
updated: 2026-03-08T22:04:37.980902+00:00
---

# Risk Register

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Sample payload lacks auth | Medium | Medium | Add API Gateway authorizers or service mesh mTLS. |
| Drift between artifacts | Low | Medium | Validate checksums during `--validate` run. |
| Missing metrics | Low | Low | Extend `METRICS/metrics.md` with service-level indicators. |
