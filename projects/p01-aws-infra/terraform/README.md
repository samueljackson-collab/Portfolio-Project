# Terraform Infrastructure - P01 AWS Infrastructure Automation

This directory contains Terraform modules that replicate the CloudFormation template's functionality, providing an alternative Infrastructure-as-Code approach.

## Architecture

The Terraform configuration deploys:
- **VPC** with public/private subnets across 3 availability zones
- **Internet Gateway** for public subnet internet access
- **NAT Gateways** for private subnet outbound connectivity
- **RDS PostgreSQL** Multi-AZ instance with automated backups
- **IAM Roles** with least-privilege policies
- **Security Groups** for network isolation
- **CloudWatch Alarms** for monitoring
- **VPC Flow Logs** for network traffic analysis

## Prerequisites

- Terraform >= 1.5.0
- AWS CLI configured with appropriate credentials
- S3 bucket for Terraform state (recommended)
- DynamoDB table for state locking (recommended)

## State Backend Setup

Create an S3 bucket and DynamoDB table for Terraform state:

```bash
# Create S3 bucket for state
aws s3api create-bucket \
  --bucket my-terraform-state-bucket \
  --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket my-terraform-state-bucket \
  --versioning-configuration Status=Enabled

# Create DynamoDB table for state locking
aws dynamodb create-table \
  --table-name terraform-state-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
  --region us-east-1
```

## Quick Start

1. **Copy configuration file:**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. **Edit terraform.tfvars with your values:**
   ```bash
   # Use a secure password from AWS Secrets Manager
   aws secretsmanager create-secret \
     --name /p01/dev/db-password \
     --secret-string "$(openssl rand -base64 32)"

   # Get the password
   DB_PASSWORD=$(aws secretsmanager get-secret-value \
     --secret-id /p01/dev/db-password \
     --query SecretString --output text)

   # Update terraform.tfvars
   sed -i "s/CHANGE_ME_USE_AWS_SECRETS_MANAGER/$DB_PASSWORD/" terraform.tfvars
   ```

3. **Initialize Terraform:**
   ```bash
   terraform init \
     -backend-config="bucket=my-terraform-state-bucket" \
     -backend-config="key=p01-aws-infra/terraform.tfstate" \
     -backend-config="region=us-east-1" \
     -backend-config="dynamodb_table=terraform-state-locks"
   ```

4. **Plan deployment:**
   ```bash
   terraform plan -out=tfplan
   ```

5. **Apply configuration:**
   ```bash
   terraform apply tfplan
   ```

6. **View outputs:**
   ```bash
   terraform output
   ```

## Module Structure

```
terraform/
├── main.tf                    # Root module configuration
├── variables.tf               # Input variables
├── outputs.tf                 # Output values
├── terraform.tfvars.example   # Example configuration
├── modules/
│   ├── vpc/                   # VPC, subnets, NAT, IGW
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── rds/                   # RDS PostgreSQL instance
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── iam/                   # IAM roles and policies
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
```

## Deployment Environments

### Development
```bash
terraform workspace new dev
terraform workspace select dev
terraform apply -var="environment=dev" -var="single_nat_gateway=true"
```

### Staging
```bash
terraform workspace new stage
terraform workspace select stage
terraform apply -var="environment=stage" -var="single_nat_gateway=false"
```

### Production
```bash
terraform workspace new prod
terraform workspace select prod
terraform apply -var="environment=prod" -var="single_nat_gateway=false"
```

## Cost Optimization

**Development environment (single NAT):**
- Estimated cost: ~$50-70/month
- Uses single NAT Gateway to reduce costs
- RDS db.t3.micro instance

**Production environment (high availability):**
- Estimated cost: ~$150-200/month
- NAT Gateway per AZ (3 total)
- RDS Multi-AZ with larger instance class

## Validation

Run Terraform validation:
```bash
terraform fmt -check
terraform validate
```

Run security scanning with tfsec:
```bash
docker run --rm -v "$(pwd):/src" aquasec/tfsec /src
```

## Disaster Recovery Testing

Test RDS failover:
```bash
# Get DB instance identifier
DB_INSTANCE=$(terraform output -raw db_instance_identifier)

# Initiate failover (Multi-AZ only)
aws rds reboot-db-instance \
  --db-instance-identifier $DB_INSTANCE \
  --force-failover

# Monitor failover
aws rds describe-events \
  --source-identifier $DB_INSTANCE \
  --duration 60
```

## Cleanup

Destroy infrastructure when no longer needed:
```bash
# Review what will be destroyed
terraform plan -destroy

# Destroy all resources
terraform destroy
```

## Comparison: Terraform vs CloudFormation

| Feature | Terraform | CloudFormation |
|---------|-----------|----------------|
| Syntax | HCL (readable) | YAML/JSON (verbose) |
| State Management | S3 + DynamoDB | AWS-managed |
| Multi-cloud | Yes | AWS-only |
| Modules | Reusable | Nested stacks |
| Plan/Preview | terraform plan | change sets |

## Security Best Practices

1. **Never commit secrets:**
   - Use AWS Secrets Manager for sensitive values
   - Reference secrets in Terraform via data sources

2. **Enable state encryption:**
   - S3 bucket encryption enabled by default
   - Use KMS for additional security

3. **Least-privilege IAM:**
   - IAM roles scoped to specific resources
   - Use assume-role for cross-account access

4. **Network isolation:**
   - RDS in private subnets only
   - Security groups with minimal ingress rules

## Troubleshooting

**Issue:** "Error creating DB Instance: InvalidParameterCombination"
**Fix:** Verify db.t3.micro is available in your region. Use `aws rds describe-orderable-db-instance-options` to check.

**Issue:** "Error acquiring the state lock"
**Fix:** Another Terraform process is running. Wait or force-unlock: `terraform force-unlock <lock-id>`

**Issue:** "Insufficient IAM permissions"
**Fix:** Ensure AWS credentials have required permissions for EC2, RDS, IAM, CloudWatch.

## References

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
