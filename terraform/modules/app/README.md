# Application Module

Provides shared application infrastructure components including an encrypted S3 assets bucket, CloudWatch log group, and optional PostgreSQL RDS instance.

## Inputs
- `project_tag` (string): Project tag and naming prefix.
- `vpc_id` (string): Target VPC ID.
- `vpc_cidr` (string): CIDR used to scope the database security group.
- `private_subnet_ids` (list(string)): Private subnet IDs for the database subnet group.
- `create_rds` (bool): Toggle database creation.
- `db_name`, `db_username`, `db_password`: Database credentials (password auto-generated when omitted).
- `db_allocated_storage`, `db_instance_class`, `db_engine_version`, `db_backup_retention`: RDS configuration.
- `assets_bucket_name` (string): Override for the assets bucket name.
- `tags` (map(string)): Tags applied to all resources.

## Outputs
- `assets_bucket_name`: Name of the S3 bucket.
- `app_log_group_name`: CloudWatch Log Group for app logs.
- `rds_endpoint`: Database endpoint (when created).
- `rds_identifier`: Database identifier (when created).
- `rds_username`: Database username.
- `rds_password`: Database password (sensitive output).
