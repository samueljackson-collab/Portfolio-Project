# Threat Model

- Unauthorized access via overly privileged roles
- Credential leakage in scripts or logs
- Unencrypted backup artifacts
- SQL injection attempts (audit via pg_stat_statements)

Controls:
- Least privilege review SQL
- Encrypted backups + S3 SSE
- Connection logging and audit queries
