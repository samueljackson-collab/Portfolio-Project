# Threat Model

## Assets
- Raw and curated datasets in S3.
- Airflow metadata database with connection credentials.
- DAG code and plugin logic that drive transformations.

## Threats
- Exfiltration of credentials from Airflow connections/variables.
- Poisoned input files leading to downstream data corruption.
- Unauthorized DAG triggers or task modifications via exposed webserver.
- Ransomware-style deletion or encryption of S3 datasets.

## Mitigations
- Store secrets in AWS Secrets Manager and reference via environment variables; limit Airflow RBAC roles.
- Great Expectations checkpoints block bad data; quarantine path isolates failed rows for investigation.
- Restrict webserver to SSO-enabled users; enforce TLS between components and rotate Fernet keys quarterly.
- Versioned S3 buckets with lifecycle policies; backups of metadata DB via `scripts/backup_metadata.sh`.
