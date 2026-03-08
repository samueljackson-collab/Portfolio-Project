---
title: ADR-001: Choose FastAPI for POC
description: - **Status:** Accepted - **Context:** Need fast iteration, OpenAPI support, async IO. - **Decision:** Use FastAPI + uvicorn instead of Flask. - **Consequences:** - Built-in docs and validation reduce 
tags: [documentation, portfolio]
path: portfolio/p09-cloud-native-poc/adr-001-framework
created: 2026-03-08T22:19:14.011165+00:00
updated: 2026-03-08T22:04:38.113902+00:00
---

# ADR-001: Choose FastAPI for POC
- **Status:** Accepted
- **Context:** Need fast iteration, OpenAPI support, async IO.
- **Decision:** Use FastAPI + uvicorn instead of Flask.
- **Consequences:**
  - Built-in docs and validation reduce boilerplate.
  - Requires async-friendly patterns and type hints.
