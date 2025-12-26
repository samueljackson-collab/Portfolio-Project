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
