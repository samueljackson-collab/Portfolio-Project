# Database Module

## Overview

This module creates a production-ready RDS PostgreSQL instance with Multi-AZ deployment, automated backups, Performance Insights, enhanced monitoring, and encryption at rest.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              VPC                                            │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        Private Subnets                                │  │
│  │     ┌──────────────┐              ┌──────────────┐                    │  │
│  │     │  Application │──────────────│  Application │                    │  │
│  │     │  (AZ-a)      │     │        │  (AZ-b)      │                    │  │
│  │     └──────────────┘     │        └──────────────┘                    │  │
│  │                          │                                            │  │
│  └──────────────────────────┼────────────────────────────────────────────┘  │
│                             │                                               │
│                    ┌────────┴────────┐                                      │
│                    │ Security Group  │                                      │
│                    │ (port 5432)     │                                      │
│                    └────────┬────────┘                                      │
│                             │                                               │
│  ┌──────────────────────────┼────────────────────────────────────────────┐  │
│  │                          ▼                                            │  │
│  │    ┌──────────────────────────────────────────────────┐               │  │
│  │    │              RDS PostgreSQL                      │               │  │
│  │    │  ┌────────────────┐    ┌────────────────┐        │               │  │
│  │    │  │ Primary (AZ-a) │◄──►│ Standby (AZ-b) │        │               │  │
│  │    │  │                │sync│ (Multi-AZ)     │        │               │  │
│  │    │  └───────┬────────┘    └────────────────┘        │               │  │
│  │    │          │                                       │               │  │
│  │    │          ▼                                       │               │  │
│  │    │  ┌────────────────┐                              │               │  │
│  │    │  │ Read Replica   │  (optional)                  │               │  │
│  │    │  │ (AZ-c)         │                              │               │  │
│  │    │  └────────────────┘                              │               │  │
│  │    └──────────────────────────────────────────────────┘               │  │
│  │                     Database Subnets (Isolated)                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Features

- **Multi-AZ Deployment**: Synchronous standby in different AZ for HA
- **Automated Backups**: 7-day retention with configurable window
- **Performance Insights**: Query performance analysis and monitoring
- **Enhanced Monitoring**: OS-level metrics at 60-second intervals
- **Encryption at Rest**: KMS-encrypted storage
- **Auto-scaling Storage**: Automatic storage expansion
- **Read Replicas**: Optional read replica for read scaling
- **CloudWatch Alarms**: Pre-configured alarms for critical metrics

## Input Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| `name_prefix` | Prefix for resource names | `string` | - | Yes |
| `vpc_id` | ID of the VPC | `string` | - | Yes |
| `db_subnet_group_name` | Name of database subnet group | `string` | - | Yes |
| `engine` | Database engine | `string` | `"postgres"` | No |
| `engine_version` | Engine version | `string` | `"15.4"` | No |
| `instance_class` | RDS instance class | `string` | `"db.t3.medium"` | No |
| `allocated_storage` | Initial storage in GB | `number` | `20` | No |
| `max_allocated_storage` | Max storage for autoscaling | `number` | `100` | No |
| `database_name` | Database name | `string` | `"portfolio"` | No |
| `master_username` | Master username | `string` | - | Yes |
| `master_password` | Master password | `string` | - | Yes |
| `port` | Database port | `number` | `5432` | No |
| `multi_az` | Enable Multi-AZ | `bool` | `true` | No |
| `backup_retention_period` | Backup retention days | `number` | `7` | No |
| `deletion_protection` | Enable deletion protection | `bool` | `false` | No |
| `performance_insights_enabled` | Enable Performance Insights | `bool` | `true` | No |
| `monitoring_interval` | Enhanced monitoring interval | `number` | `60` | No |
| `create_read_replica` | Create read replica | `bool` | `false` | No |
| `create_cloudwatch_alarms` | Create CloudWatch alarms | `bool` | `true` | No |
| `allowed_security_groups` | Security groups allowed to connect | `list(string)` | `[]` | No |
| `tags` | Tags to apply to resources | `map(string)` | `{}` | No |

## Outputs

| Name | Description |
|------|-------------|
| `db_instance_id` | The ID of the RDS instance |
| `db_instance_arn` | The ARN of the RDS instance |
| `db_instance_endpoint` | The endpoint of the RDS instance |
| `db_instance_address` | The address of the RDS instance |
| `db_instance_port` | The port of the RDS instance |
| `db_instance_name` | The database name |
| `db_instance_multi_az` | Whether instance is multi-AZ |
| `security_group_id` | The ID of the RDS security group |
| `parameter_group_name` | The name of the parameter group |
| `kms_key_arn` | The ARN of the KMS key |
| `connection_string` | PostgreSQL connection string |
| `jdbc_connection_string` | JDBC connection string |
| `replica_instance_endpoint` | Endpoint of read replica (if created) |

## Example Usage

### Development Database

```hcl
module "database" {
  source = "./modules/database"

  name_prefix          = "myapp-dev"
  vpc_id               = module.networking.vpc_id
  db_subnet_group_name = module.networking.database_subnet_group_name

  instance_class     = "db.t3.micro"
  allocated_storage  = 20
  multi_az           = false
  skip_final_snapshot = true

  master_username = "admin"
  master_password = var.db_password

  allowed_security_groups = [module.compute.app_security_group_id]

  tags = {
    Environment = "dev"
  }
}
```

### Production Database (High Availability)

```hcl
module "database" {
  source = "./modules/database"

  name_prefix          = "myapp-prod"
  vpc_id               = module.networking.vpc_id
  db_subnet_group_name = module.networking.database_subnet_group_name

  instance_class        = "db.r6g.large"
  allocated_storage     = 100
  max_allocated_storage = 500
  multi_az              = true
  deletion_protection   = true
  skip_final_snapshot   = false

  backup_retention_period = 30
  backup_window           = "03:00-04:00"
  maintenance_window      = "Mon:04:00-Mon:05:00"

  master_username = "admin"
  master_password = var.db_password

  performance_insights_enabled          = true
  performance_insights_retention_period = 31
  monitoring_interval                   = 30

  create_cloudwatch_alarms = true
  alarm_actions            = [aws_sns_topic.alerts.arn]

  allowed_security_groups = [module.compute.app_security_group_id]

  tags = {
    Environment = "production"
    Backup      = "enabled"
  }
}
```

### With Read Replica

```hcl
module "database" {
  source = "./modules/database"

  name_prefix          = "myapp-prod"
  vpc_id               = module.networking.vpc_id
  db_subnet_group_name = module.networking.database_subnet_group_name

  instance_class      = "db.r6g.large"
  create_read_replica = true
  replica_instance_class = "db.r6g.medium"

  master_username = "admin"
  master_password = var.db_password

  tags = {
    Environment = "production"
  }
}
```

## Parameter Group Settings

The module creates a custom parameter group with optimized settings:

| Parameter | Value | Description |
|-----------|-------|-------------|
| `log_min_duration_statement` | 1000ms | Log slow queries |
| `shared_preload_libraries` | pg_stat_statements | Query analysis |
| `max_connections` | 100 | Maximum connections |
| `work_mem` | 4MB | Memory per operation |
| `log_statement` | ddl | Log DDL statements |

## CloudWatch Alarms

Pre-configured alarms (when `create_cloudwatch_alarms = true`):

| Alarm | Threshold | Description |
|-------|-----------|-------------|
| CPU Utilization | > 80% | High CPU usage |
| Free Storage | < 5GB | Low disk space |
| Database Connections | > 80 | High connection count |
| Freeable Memory | < 256MB | Low available memory |

## Important Notes

1. **Encryption**: All data is encrypted at rest using KMS. The module creates a dedicated KMS key.

2. **Backups**: Automated daily backups with point-in-time recovery. Snapshots are retained based on `backup_retention_period`.

3. **Multi-AZ**: For production, always use `multi_az = true` for automatic failover.

4. **Security**: Database is only accessible from specified security groups. Never expose to public internet.

5. **Deletion Protection**: Enable `deletion_protection = true` for production databases.

## Security Best Practices

- Store credentials in AWS Secrets Manager
- Use IAM database authentication when possible
- Regularly rotate master password
- Enable SSL/TLS for connections
- Restrict security group access to application subnets only

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.4 |
| aws | ~> 5.0 |
