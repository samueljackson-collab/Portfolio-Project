---
title: SOP: Managing API Test Environments
description: - **Variables**: Store base URLs and secrets in Postman environments under `producer/env/*.postman_environment.json`. - **Rotation**: Rotate tokens weekly; update secrets store and regenerate environm
tags: [documentation, portfolio]
path: portfolio/p08-api-testing/environment
created: 2026-03-08T22:19:13.991025+00:00
updated: 2026-03-08T22:04:38.098902+00:00
---

# SOP: Managing API Test Environments

- **Variables**: Store base URLs and secrets in Postman environments under `producer/env/*.postman_environment.json`.
- **Rotation**: Rotate tokens weekly; update secrets store and regenerate environment files.
- **Data Reset**: Use `jobs/reset_data.sh` to reseed mock data before performance runs.
- **Access**: Limit ability to edit environments to QA leads; review changes in PRs.
