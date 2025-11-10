# AWS Secrets Manager Terraform Module

This module creates and manages secrets in AWS Secrets Manager with support for automatic rotation, KMS encryption, and IAM-based access control.

## Features

- **Automatic Password Generation**: Generates secure random passwords if value not provided
- **KMS Encryption**: Optional customer-managed key encryption
- **Automatic Rotation**: Built-in support for Lambda-based secret rotation
- **Access Control**: IAM-based permissions for secret access
- **Versioning**: Automatic version tracking of secret values
- **Recovery**: Configurable recovery window for deleted secrets

## Usage

### Basic Usage (Generate Random Password)

```hcl
module "db_password" {
  source = "./modules/secrets-manager"

  secret_name = "rds/myapp/master-password"
  description = "RDS master database password"
  environment = "prod"

  recovery_window_in_days = 30

  tags = {
    Application = "MyApp"
    ManagedBy   = "Terraform"
  }
}

# Use the secret in RDS module
module "rds" {
  source = "./modules/rds"

  master_password = module.db_password.secret_reference
  # ... other configuration
}
```

### With Custom Value

```hcl
module "api_key" {
  source = "./modules/secrets-manager"

  secret_name  = "application/api-key"
  description  = "Third-party API key"
  secret_value = var.api_key  # Provided via terraform.tfvars or environment variable
  environment  = "prod"

  tags = {
    Application = "MyApp"
  }
}
```

### With KMS Encryption

```hcl
resource "aws_kms_key" "secrets" {
  description             = "KMS key for secrets encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true
}

module "db_password" {
  source = "./modules/secrets-manager"

  secret_name = "rds/myapp/master-password"
  description = "RDS master database password"
  environment = "prod"

  # Use customer-managed KMS key
  kms_key_id = aws_kms_key.secrets.id

  tags = {
    Application = "MyApp"
  }
}
```

### With Automatic Rotation

```hcl
module "db_password" {
  source = "./modules/secrets-manager"

  secret_name = "rds/myapp/master-password"
  description = "RDS master database password"
  environment = "prod"

  # Enable rotation every 90 days
  enable_rotation = true
  rotation_days   = 90

  # VPC configuration for Lambda function (required if database is in VPC)
  vpc_config = {
    subnet_ids         = module.vpc.private_subnet_ids
    security_group_ids = [aws_security_group.lambda_rotation.id]
  }

  tags = {
    Application = "MyApp"
  }
}
```

### With IAM Access Control

```hcl
module "db_password" {
  source = "./modules/secrets-manager"

  secret_name = "rds/myapp/master-password"
  description = "RDS master database password"
  environment = "prod"

  # Allow specific IAM roles to read the secret
  allowed_iam_arns = [
    aws_iam_role.ecs_task.arn,
    aws_iam_role.lambda_function.arn
  ]

  tags = {
    Application = "MyApp"
  }
}
```

## Retrieving Secret Values

### In Terraform (Not Recommended)

```hcl
# This exposes the secret in Terraform state - avoid if possible
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = module.db_password.secret_id
}

locals {
  db_password = jsondecode(data.aws_secretsmanager_secret_version.db_password.secret_string)
}
```

### In Application Code (Recommended)

**Python (boto3)**:
```python
import boto3
import json

client = boto3.client('secretsmanager', region_name='us-east-1')
response = client.get_secret_value(SecretId='rds/myapp/master-password')
secret = json.loads(response['SecretString'])
password = secret['password']
```

**AWS CLI**:
```bash
aws secretsmanager get-secret-value \
  --secret-id rds/myapp/master-password \
  --query SecretString \
  --output text
```

### In ECS Task Definition

```json
{
  "containerDefinitions": [{
    "secrets": [{
      "name": "DB_PASSWORD",
      "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:rds/myapp/master-password"
    }]
  }]
}
```

## Secret Rotation

This module includes a placeholder for Lambda-based secret rotation. To implement rotation:

1. Create rotation Lambda function code based on database type:
   - [RDS PostgreSQL Rotation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/reference_available-rotation-templates.html#sar-template-postgre-single-user)
   - [RDS MySQL Rotation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/reference_available-rotation-templates.html#sar-template-mysql-single-user)

2. Package Lambda code:
   ```bash
   cd lambda
   zip rotation.zip lambda_function.py
   ```

3. Enable rotation in module configuration:
   ```hcl
   enable_rotation = true
   rotation_days   = 90
   ```

## Cost Considerations

**Secrets Manager Pricing** (us-east-1):
- **Secret Storage**: $0.40 per secret per month
- **API Calls**: $0.05 per 10,000 API calls
- **Rotation**: Lambda and network costs (minimal)

**Example Monthly Cost**:
- 10 secrets × $0.40 = $4.00/month
- 100k API calls × $0.05 / 10k = $0.50/month
- **Total**: ~$4.50/month

## Security Best Practices

1. **Never commit secrets to version control**
   ```bash
   # Add to .gitignore
   *.tfvars
   terraform.tfstate*
   ```

2. **Use IAM policies for least privilege access**
   ```hcl
   allowed_iam_arns = [aws_iam_role.specific_role.arn]
   ```

3. **Enable KMS encryption for sensitive secrets**
   ```hcl
   kms_key_id = aws_kms_key.secrets.id
   ```

4. **Set appropriate recovery window**
   ```hcl
   recovery_window_in_days = 30  # Allows recovery for 30 days
   ```

5. **Enable rotation for database credentials**
   ```hcl
   enable_rotation = true
   rotation_days   = 90
   ```

6. **Use VPC endpoints to keep traffic within AWS**
   ```hcl
   # Create VPC endpoint for Secrets Manager
   resource "aws_vpc_endpoint" "secretsmanager" {
     vpc_id            = module.vpc.vpc_id
     service_name      = "com.amazonaws.us-east-1.secretsmanager"
     vpc_endpoint_type = "Interface"
     subnet_ids        = module.vpc.private_subnet_ids
   }
   ```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| secret_name | Name of the secret | string | - | yes |
| description | Description of the secret | string | "Managed by Terraform" | no |
| environment | Environment name (dev, stage, prod) | string | "dev" | no |
| secret_value | Secret value to store | string | null | no |
| password_length | Length of generated password | number | 32 | no |
| kms_key_id | KMS key ID for encryption | string | null | no |
| recovery_window_in_days | Recovery window (7-30 days, or 0) | number | 30 | no |
| enable_rotation | Enable automatic rotation | bool | false | no |
| rotation_days | Days between rotations | number | 90 | no |
| allowed_iam_arns | IAM ARNs allowed to read secret | list(string) | [] | no |
| vpc_config | VPC config for rotation Lambda | object | null | no |
| tags | Tags to apply to resources | map(string) | {} | no |

## Outputs

| Name | Description |
|------|-------------|
| secret_id | ID of the secret |
| secret_arn | ARN of the secret |
| secret_name | Name of the secret |
| secret_version_id | Version ID of the secret |
| rotation_lambda_arn | ARN of rotation Lambda (if enabled) |
| rotation_enabled | Whether rotation is enabled |
| secret_reference | Reference for use in connection strings |

## Examples

See the [examples](./examples/) directory for complete working examples:
- [Basic secret creation](./examples/basic/)
- [Database password with rotation](./examples/database-rotation/)
- [API key management](./examples/api-key/)

## References

- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/)
- [Rotating Secrets](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html)
- [Secrets Manager Best Practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)
