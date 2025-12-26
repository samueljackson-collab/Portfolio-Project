# Database Module

Builds a Multi-AZ Amazon RDS instance with encryption, retention, and subnet isolation. The module provisions:
- Dedicated DB subnet group using the networking module private database subnets.
- Parameterizable RDS instance (engine, size, storage) with encryption via customer-managed KMS (optional).
- Enforced deletion protection, automated backups, and performance insights for proactive tuning.
