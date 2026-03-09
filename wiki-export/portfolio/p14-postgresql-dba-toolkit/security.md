---
title: Security
description: - Run `sql/security/user_audit.sql` and `sql/security/permission_review.sql` quarterly. - Validate encryption settings with `sql/security/encryption_verification.sql`. - Ensure `password_encryption = 
tags: [documentation, portfolio]
path: portfolio/p14-postgresql-dba-toolkit/security
created: 2026-03-08T22:19:13.781909+00:00
updated: 2026-03-08T22:04:37.927902+00:00
---

# Security

## Audit
- Run `sql/security/user_audit.sql` and `sql/security/permission_review.sql` quarterly.
- Validate encryption settings with `sql/security/encryption_verification.sql`.

## Password Policy
- Ensure `password_encryption = scram-sha-256` where possible.
- Review `sql/security/password_policy.sql` results.

## Connection Auditing
- Enable `log_connections` and `log_disconnections`.
- Use `sql/security/connection_audit.sql` to validate config.
