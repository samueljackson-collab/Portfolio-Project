# Architecture

Stack: Bash/PowerShell scripts, Postgres/MySQL snapshots, S3/Glacier for offsite copies.

Data/Control flow: Nightly backups captured, integrity verified, copied to offsite bucket, and periodic drills restore to sandbox and validate checksums.

Dependencies:
- Bash/PowerShell scripts, Postgres/MySQL snapshots, S3/Glacier for offsite copies.
- Env/config: see README for required secrets and endpoints.
