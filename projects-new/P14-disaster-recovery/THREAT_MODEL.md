# Threat Model

## Assets
- Database snapshots in S3/Glacier.
- Backup and restore scripts.
- Encryption keys and credentials for backup storage.

## Threats
- Backup corruption or missing encryption.
- Credential theft for backup buckets.
- Ransomware wiping snapshots.

## Mitigations
- Checksum verification and regular restore tests.
- IAM least privilege with KMS key policies for encryption.
- Versioned S3 buckets with object lock and Glacier vault lock.
