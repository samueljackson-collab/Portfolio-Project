---
title: SOP: Logging and PII Handling
description: - **Hash identifiers**: Always run `producer/utils.py --hash-identifiers` before exporting logs outside the lab. - **Log levels**: Default to `INFO`; enable `DEBUG` only in non-production overlays. - 
tags: [documentation, portfolio]
path: portfolio/p07-roaming-simulation/logging
created: 2026-03-08T22:19:13.964438+00:00
updated: 2026-03-08T22:04:38.082902+00:00
---

# SOP: Logging and PII Handling

- **Hash identifiers**: Always run `producer/utils.py --hash-identifiers` before exporting logs outside the lab.
- **Log levels**: Default to `INFO`; enable `DEBUG` only in non-production overlays.
- **Retention**: Keep simulator logs for 30 days; KPI summaries for 90 days.
- **Access control**: Limit raw logs to roaming engineering; anonymized metrics can be shared with partners.
- **Verification**: Run `python consumer/main.py --validate-logs out/events.jsonl` weekly to ensure schema parity.
