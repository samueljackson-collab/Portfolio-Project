# Threat Model

Threats:
- Backup corruption or missing encryption
- Credential theft for backup buckets
- Ransomware wiping snapshots

Mitigations:
- Checksum verification + restore tests
- IAM least privilege with KMS key policies
- Versioned buckets with object lock and Glacier vault lock
