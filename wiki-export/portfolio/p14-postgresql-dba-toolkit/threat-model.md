---
title: Threat Model
description: - Unauthorized access via overly privileged roles - Credential leakage in scripts or logs - Unencrypted backup artifacts - SQL injection attempts (audit via pg_stat_statements) Controls: - Least privi
tags: [documentation, portfolio]
path: portfolio/p14-postgresql-dba-toolkit/threat-model
created: 2026-03-08T22:19:13.776029+00:00
updated: 2026-03-08T22:04:37.926902+00:00
---

# Threat Model

- Unauthorized access via overly privileged roles
- Credential leakage in scripts or logs
- Unencrypted backup artifacts
- SQL injection attempts (audit via pg_stat_statements)

Controls:
- Least privilege review SQL
- Encrypted backups + S3 SSE
- Connection logging and audit queries
