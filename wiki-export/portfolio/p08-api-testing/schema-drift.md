---
title: Playbook: Schema Drift Detected
description: 1. **Trigger**: Alert `api_schema_drift > 0` from METRICS. 2. **Validate**: Re-run validator against `/openapi.json` and live responses. 3. **Mitigate**: Pin client version to last known good schema; 
tags: [documentation, portfolio]
path: portfolio/p08-api-testing/schema-drift
created: 2026-03-08T22:19:13.985660+00:00
updated: 2026-03-08T22:04:38.095902+00:00
---

# Playbook: Schema Drift Detected

1. **Trigger**: Alert `api_schema_drift > 0` from METRICS.
2. **Validate**: Re-run validator against `/openapi.json` and live responses.
3. **Mitigate**: Pin client version to last known good schema; notify API owner.
4. **Document**: File a change request using `REPORT_TEMPLATES/test_summary.md`.
5. **Close**: Add contract test covering the new/changed field.
