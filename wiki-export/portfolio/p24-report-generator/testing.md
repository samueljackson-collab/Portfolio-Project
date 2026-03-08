---
title: Testing Strategy
description: - Run unit-style checks via the CLI harness in `jobs/demo_job.py` (no external deps). - Validate the pipeline by executing `python docker/producer/main.py --validate` which ensures producer -> job -> 
tags: [documentation, portfolio]
path: portfolio/p24-report-generator/testing
created: 2026-03-08T22:19:13.908865+00:00
updated: 2026-03-08T22:04:38.041902+00:00
---

# Testing Strategy

- Run unit-style checks via the CLI harness in `jobs/demo_job.py` (no external deps).
- Validate the pipeline by executing `python docker/producer/main.py --validate` which ensures producer -> job -> consumer flow works.
- For container smoke tests, build the sample Dockerfile: `docker build -t demo-pipeline .`
