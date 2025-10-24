# DevOps File Backup Utility

## Overview
A Python automation script that snapshots critical configuration files, encrypts archives, and uploads them to redundant storage targets. Designed for cron/scheduled execution with idempotent runs.

## Capabilities
- Recursive backup of configured paths with inclusion/exclusion rules.
- Differential backups using file hashes to minimize storage footprint.
- Multi-target upload (S3, SFTP, local NAS) with pluggable transport layer.
- Integrity verification using SHA-256 manifests and optional signed attestations.

## Getting Started
1. Install dependencies: `poetry install`.
2. Configure backup sources and destinations in `config/backup.yaml` (example provided).
3. Run locally: `poetry run backup --config config/backup.yaml`.
4. Schedule via cron or systemd timer using provided unit files under `ops/systemd/`.

## Observability & Reporting
- Emits metrics to Prometheus Pushgateway (`backup_files_total`, `backup_bytes_total`, `backup_duration_seconds`).
- Generates HTML/Markdown reports stored in `reports/` and optionally emailed via SES/SMTP.

## Security Controls
- Secrets (encryption keys, credentials) sourced from AWS Secrets Manager or Vault with fallback to `.env` for local testing.
- Archives encrypted using AES-256 (libsodium) and optionally signed via GPG.
- Compliance mapping to CIS Control 11 (Data Recovery). Evidence stored in `evidence/`.

## Testing
- Unit tests for filesystem abstraction and transport modules.
- Integration tests using LocalStack and mock SFTP server.
- Linting enforced with `ruff` and `mypy`.

