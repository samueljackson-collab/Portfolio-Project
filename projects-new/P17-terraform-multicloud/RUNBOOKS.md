# Runbooks

- Failed apply: inspect plan logs, clear state lock, rerun with -refresh-only if drift suspected
- State corruption: restore from S3/Blob version, re-run plan, notify stakeholders
- Provider auth errors: refresh credentials, validate env vars, retry plan
