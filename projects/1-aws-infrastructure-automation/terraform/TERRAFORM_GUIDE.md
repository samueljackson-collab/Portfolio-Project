# Terraform Implementation Guide

## Overview

This Terraform configuration creates a complete AWS infrastructure for the portfolio project, including:
- VPC with public/private subnets across multiple availability zones
- EKS (Elastic Kubernetes Service) cluster with managed node groups
- RDS PostgreSQL database with automated backups
- Application Load Balancer with Auto Scaling web tier
- S3 bucket for static assets served through CloudFront
- NAT gateways for private subnet internet access
- Security groups and network ACLs

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         AWS Account                          │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │                      VPC                           │    │
│  │                                                    │    │
│  │  ┌───────────────┐        ┌───────────────┐      │    │
│  │  │ Public Subnet │        │ Public Subnet │      │    │
│  │  │   (AZ-1)      │        │   (AZ-2)      │      │    │
│  │  │               │        │               │      │    │
│  │  │  NAT Gateway  │        │  NAT Gateway  │      │    │
│  │  └───────┬───────┘        └───────┬───────┘      │    │
│  │          │                        │              │    │
│  │  ┌───────▼───────┐        ┌───────▼───────┐      │    │
│  │  │ Private       │        │ Private       │      │    │
│  │  │ Subnet (AZ-1) │        │ Subnet (AZ-2) │      │    │
│  │  │               │        │               │      │    │
│  │  │  EKS Nodes    │        │  EKS Nodes    │      │    │
│  │  └───────────────┘        └───────────────┘      │    │
│  │                                                   │    │
│  │  ┌───────────────┐        ┌───────────────┐      │    │
│  │  │ DB Subnet     │        │ DB Subnet     │      │    │
│  │  │ (AZ-1)        │        │ (AZ-2)        │      │    │
│  │  │               │        │               │      │    │
│  │  │  RDS Instance │◄───────┤ RDS Standby  │      │    │
│  │  └───────────────┘        └───────────────┘      │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Resources Created

### VPC Module
- **VPC** with user-defined CIDR block
- **Public subnets** (2) for load balancers and NAT gateways
- **Private subnets** (2) for application workloads
- **Database subnets** (2) for RDS instances
- **Internet Gateway** for public internet access
- **NAT Gateway(s)** - single in dev/staging, multi-AZ in production
- **Route tables** and associations
- **Security groups**

### EKS Module
- **EKS Control Plane** (Kubernetes 1.28)
- **Managed Node Group** with auto-scaling (2-10 nodes)
- **Instance types**: t3.medium/t3.large (mix of Spot and On-Demand)
- **Cluster Add-ons**: CoreDNS, kube-proxy, VPC CNI
- **IAM roles** for cluster and nodes
- **Security groups** for cluster communication

### RDS Module
- **PostgreSQL 15.4** database
- **Instance class**: db.t3.medium
- **Storage**: 20GB (auto-scaling to 100GB)
- **Multi-AZ** deployment for high availability
- **Automated backups** (7-day retention)
- **Performance Insights** enabled
- **Encryption at rest** enabled by default

### Web Tier (ALB + Auto Scaling)
- **Application Load Balancer** exposed on port 80
- **Target group** with health checks on `/`
- **Launch template** bootstraps NGINX landing page
- **Auto Scaling Group** across private subnets (min 2 / desired 3 / max 6)
- **Security groups** restricting web traffic to ALB ingress only

### Static Assets + CDN
- **S3 bucket** with versioning, SSE, and public access blocks
- **CloudFront distribution** with S3 default origin and ALB `/api/*` behavior
- **Origin Access Identity (OAI)** for least-privilege S3 read access

## Input Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| `region` | AWS region to deploy resources | string | `us-west-2` | no |
| `environment` | Environment name (dev/staging/production) | string | `dev` | no |
| `vpc_cidr` | CIDR block for VPC | string | `10.0.0.0/16` | no |
| `availability_zones` | List of availability zones | list(string) | `["us-west-2a", "us-west-2b", "us-west-2c"]` | no |
| `private_subnet_cidrs` | CIDR blocks for private subnets | list(string) | `["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]` | no |
| `public_subnet_cidrs` | CIDR blocks for public subnets | list(string) | `["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]` | no |
| `database_subnet_cidrs` | CIDR blocks for database subnets | list(string) | `["10.0.201.0/24", "10.0.202.0/24", "10.0.203.0/24"]` | no |
| `web_instance_type` | Instance type for web ASG | string | `t3.micro` | no |
| `web_min_size` / `web_desired_capacity` / `web_max_size` | Web Auto Scaling Group sizes | number | `2 / 3 / 6` | no |
| `asset_bucket_name` | S3 bucket for static assets | string | `portfolio-static-assets-example` | yes (unique) |
| `cloudfront_price_class` | CloudFront edge coverage | string | `PriceClass_200` | no |
| `db_username` | Master username for RDS | string | n/a | yes |
| `db_password` | Master password for RDS | string | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| `vpc_id` | ID of the created VPC |
| `private_subnets` | IDs of private subnets |
| `eks_cluster_name` | Name of the EKS cluster |
| `rds_endpoint` | Connection endpoint for RDS instance |
| `alb_dns_name` | Public DNS name of the Application Load Balancer |
| `alb_target_group_arn` | Target group ARN backing the ALB |
| `web_autoscaling_group_name` | Name of the web Auto Scaling Group |
| `asset_bucket_name` / `asset_bucket_arn` | Static asset S3 bucket identifiers |
| `cloudfront_domain_name` / `cloudfront_distribution_id` | CloudFront endpoint and distribution ID |

## Usage

### Prerequisites

1. **AWS CLI** configured with credentials:
   ```bash
   aws configure
   ```

2. **Terraform** installed (>= 1.4):
   ```bash
   terraform version
   ```

3. **S3 bucket** for Terraform state (create manually):
   ```bash
   aws s3 mb s3://my-terraform-state-bucket
   aws s3api put-bucket-versioning \
     --bucket my-terraform-state-bucket \
     --versioning-configuration Status=Enabled
   ```

4. **DynamoDB table** for state locking:
   ```bash
   aws dynamodb create-table \
     --table-name terraform-state-lock \
     --attribute-definitions AttributeName=LockID,AttributeType=S \
     --key-schema AttributeName=LockID,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST
   ```

### Deployment Steps

1. **Create terraform.tfvars**:
   ```hcl
   environment = "dev"
   region      = "us-east-1"

   vpc_cidr               = "10.0.0.0/16"
   availability_zones     = ["us-east-1a", "us-east-1b"]
   private_subnet_cidrs   = ["10.0.1.0/24", "10.0.2.0/24"]
   public_subnet_cidrs    = ["10.0.101.0/24", "10.0.102.0/24"]
   database_subnet_cidrs  = ["10.0.201.0/24", "10.0.202.0/24"]

   db_username = "admin"
   db_password = "CHANGE_ME_SECURE_PASSWORD"  # Use AWS Secrets Manager in production
   ```

2. **Configure backend** (update `backend.hcl`):
   ```hcl
   bucket         = "my-terraform-state-bucket"
   key            = "portfolio/dev/terraform.tfstate"
   region         = "us-east-1"
   dynamodb_table = "terraform-state-lock"
   encrypt        = true
   ```

3. **Initialize Terraform**:
   ```bash
   terraform init -backend-config=backend.hcl
   ```

4. **Validate configuration**:
   ```bash
   terraform validate
   terraform fmt -check
   ```

5. **Plan deployment**:
   ```bash
   terraform plan -out=tfplan
   ```

6. **Review and apply**:
   ```bash
   terraform apply tfplan
   ```

7. **Save outputs**:
   ```bash
   terraform output -json > terraform-outputs.json
   ```

### Connect to EKS Cluster

After deployment, configure kubectl:

```bash
# Get cluster name from outputs
CLUSTER_NAME=$(terraform output -raw eks_cluster_name)

# Update kubeconfig
aws eks update-kubeconfig --name $CLUSTER_NAME --region us-east-1

# Verify connection
kubectl get nodes
```

### Connect to RDS Database

```bash
# Get RDS endpoint
RDS_ENDPOINT=$(terraform output -raw rds_endpoint)

# Connect using psql (from within VPC or via bastion host)
psql -h $RDS_ENDPOINT -U admin -d portfolio
```

## Cost Estimation

Run cost estimation before deploying:

```bash
./scripts/cost-estimate.sh dev
```

**Estimated Monthly Costs (dev environment)**:
- EKS Control Plane: ~$73
- EC2 Instances (3x t3.medium): ~$95
- RDS (db.t3.medium): ~$60
- NAT Gateway: ~$35
- **Total**: ~$263/month

**Production environment**: ~$500-800/month depending on scaling

## Security Considerations

### Implemented Security Features
- ✅ VPC with public/private subnet isolation
- ✅ NAT Gateway for secure outbound access
- ✅ RDS in private database subnets
- ✅ Encryption at rest for RDS
- ✅ Automated backups with 7-day retention
- ✅ Deletion protection for production RDS
- ✅ Security groups limiting network access
- ✅ IAM roles with least privilege

### Recommended Enhancements
- [ ] Enable VPC Flow Logs
- [ ] Configure AWS WAF for public endpoints
- [ ] Use AWS Secrets Manager for database credentials
- [ ] Enable AWS GuardDuty for threat detection
- [ ] Configure AWS Config for compliance monitoring
- [ ] Implement network ACLs for additional security
- [ ] Enable EKS Pod Security Policies

## Troubleshooting

### Common Issues

**Issue**: Terraform fails to create NAT Gateway
```
Error: Error creating NAT Gateway
```
**Solution**: Check EIP limits in your AWS account. Request limit increase if needed.

---

**Issue**: EKS nodes not joining cluster
```
Error: Nodes not ready
```
**Solution**:
1. Check node IAM role has `AmazonEKSWorkerNodePolicy`
2. Verify security groups allow communication
3. Check VPC DNS settings enabled

---

**Issue**: Cannot connect to RDS
```
Error: Connection timed out
```
**Solution**:
1. Ensure you're connecting from within VPC (or via bastion)
2. Check security group rules allow PostgreSQL port 5432
3. Verify RDS is in "Available" state

## Maintenance

### Updating Terraform

```bash
# Update provider versions
terraform init -upgrade

# Plan changes
terraform plan

# Apply updates
terraform apply
```

### Backup and Recovery

**State File Backup**:
```bash
# Download current state
terraform state pull > terraform.tfstate.backup

# Upload to S3 for extra safety
aws s3 cp terraform.tfstate.backup s3://my-backups/
```

**RDS Backup**:
- Automated daily backups configured
- 7-day retention period
- Point-in-time recovery available

**Restore from Backup**:
```bash
# List available snapshots
aws rds describe-db-snapshots \
  --db-instance-identifier portfolio-dev

# Restore from snapshot (requires Terraform update)
```

## CI/CD Integration

This configuration is integrated with GitHub Actions:
- Automatic `terraform validate` on PRs
- Security scanning with tfsec
- Automatic `terraform plan` on PRs
- Automatic `terraform apply` on main branch (with approval)

See `.github/workflows/terraform.yml` for pipeline configuration.

## Additional Resources

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [VPC Module Documentation](https://registry.terraform.io/modules/terraform-aws-modules/vpc/aws/latest)
- [EKS Module Documentation](https://registry.terraform.io/modules/terraform-aws-modules/eks/aws/latest)
- [RDS Module Documentation](https://registry.terraform.io/modules/terraform-aws-modules/rds/aws/latest)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Terraform logs: `TF_LOG=DEBUG terraform apply`
3. Review AWS CloudWatch logs for service-specific issues
4. Open an issue in the GitHub repository
