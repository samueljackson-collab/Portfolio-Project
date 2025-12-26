# AWS Setup Guide (us-west-2, SamSJPortfolio)

This guide walks through **setting up AWS from scratch** in **us-west-2**, using the naming suffix **SamSJPortfolio**. The steps are written for someone new to AWS.

## Step 0: What you will create
- An AWS account with billing, MFA, and cost controls
- IAM users/roles with least-privilege access
- A VPC with public and private subnets
- S3 buckets for report storage and logs
- Compute (ECS Fargate or EC2) behind an ALB
- RDS Postgres database
- Logging/monitoring (CloudWatch, CloudTrail)
- CI/CD for automated deployments

## Step 1: Create your AWS account
1. Go to https://aws.amazon.com
2. Choose **Create an AWS Account**.
3. Use a unique email and strong password.
4. Verify your email and phone number.
5. Add a payment method.
6. **Enable MFA for the root user** (IAM → Security Credentials → MFA).

## Step 2: Set billing and cost controls
1. In the AWS Console, open **Billing**.
2. Enable **Receive Billing Alerts**.
3. Create a **Budget** (e.g., $20/month):
   - Billing → Budgets → Create budget
   - Alerts to your email

## Step 3: Create an admin IAM user (stop using root)
1. Go to **IAM → Users → Create user**.
2. Username: `admin-SamSJPortfolio`
3. Select **Provide user access to the AWS Management Console**.
4. Set a password and require reset on first sign-in.
5. Attach the policy **AdministratorAccess**.
6. Create access keys for programmatic access (download the CSV securely).
7. Enable MFA for the new IAM user.

## Step 4: Create groups and standard IAM roles
1. Create groups:
   - `portfolio-admins-SamSJPortfolio` → AdministratorAccess
   - `portfolio-devs-SamSJPortfolio` → scoped policy (S3 + ECS + CloudWatch)
2. Add users to appropriate groups.
3. Create roles for services:
   - `ecsTaskExecutionRole-SamSJPortfolio` → AmazonECSTaskExecutionRolePolicy
   - `report-gen-task-role-SamSJPortfolio` → custom least-privilege policy

## Step 5: Configure AWS CLI
1. Install AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
2. Run:
   ```bash
   aws configure
   ```
3. Enter:
   - Access key / secret key
   - Region: `us-west-2`
   - Output: `json`

## Step 6: Create a VPC and networking (us-west-2)
1. Go to **VPC → Create VPC**.
2. Name: `portfolio-vpc-SamSJPortfolio`
3. CIDR: `10.0.0.0/16`
4. Create subnets:
   - Public: `10.0.1.0/24`, `10.0.2.0/24` (two AZs)
   - Private: `10.0.3.0/24`, `10.0.4.0/24` (two AZs)
5. Create an **Internet Gateway** and attach it to the VPC.
6. Create a **NAT Gateway** in a public subnet (allocate Elastic IP).
7. Create route tables:
   - Public route → `0.0.0.0/0` to IGW
   - Private route → `0.0.0.0/0` to NAT
8. Enable **VPC Flow Logs** → send to CloudWatch log group `/vpc/flowlogs/SamSJPortfolio`.

## Step 7: Security groups
Create these security groups:
- **sg-web-SamSJPortfolio**
  - Allow inbound 80/443 from 0.0.0.0/0
  - Allow SSH from your IP only
- **sg-app-SamSJPortfolio**
  - Add an inbound rule allowing traffic on your application port, with the source set to the ID of `sg-web-SamSJPortfolio`.
- **sg-db-SamSJPortfolio**
  - Add an inbound rule for port 5432 (Postgres), with the source set to the ID of `sg-app-SamSJPortfolio`.

## Step 8: S3 buckets
1. Create bucket: `reports-SamSJPortfolio-us-west-2`
2. Enable **block public access**.
3. Turn on **versioning** and **default encryption**.
4. Optional lifecycle rule: move objects to Glacier after 90 days.

## Step 9: Secrets and configuration
1. Use **Secrets Manager** for DB credentials:
   - Secret name: `SamSJPortfolio/reporting-db`
2. Use **SSM Parameter Store** for non-secret config:
   - `/SamSJPortfolio/reporting/api-base-url`

## Step 10: Compute (ECS Fargate recommended)
1. Create an ECS cluster: `report-gen-cluster-SamSJPortfolio`.
2. Register a task definition for the report generator.
3. Create an ECS service:
   - `report-gen-service-SamSJPortfolio`
   - Place in private subnets
4. Create an **ALB** in public subnets:
   - Name: `alb-report-SamSJPortfolio`
   - HTTPS listener with ACM certificate
   - Target group to ECS service

## Step 11: Database (RDS Postgres)
1. Create RDS Postgres:
   - DB name: `reporting-db-SamSJPortfolio`
   - Subnets: private
   - Security group: `sg-db-SamSJPortfolio`
2. Enable encryption and backups.

## Step 12: Monitoring and logging
1. CloudWatch log groups:
   - `/report-gen/app/SamSJPortfolio`
   - `/report-gen/alb/SamSJPortfolio`
2. Alarms for CPU, memory, 5XX errors, RDS storage.
3. Enable **CloudTrail** to an S3 bucket:
   - `cloudtrail-SamSJPortfolio-us-west-2`

## Step 13: CI/CD (GitHub Actions OIDC)
1. Create IAM role `gha-deploy-SamSJPortfolio`.
2. Trust policy for GitHub OIDC.
3. Attach policies for ECR + ECS deploy.
4. Add GitHub Actions workflow to build and deploy.

## Step 14: Final checklist
- HTTPS enabled
- WAF attached to ALB
- S3 buckets are private
- Alarms notify via SNS topic `alerts-SamSJPortfolio`
- Access restricted to least privilege

---

# Recreated Documentation Templates

## README.md template
```md
# Report Generator (SamSJPortfolio)

## Overview
Describe the app and its purpose.

## Architecture
- Region: us-west-2
- VPC: portfolio-vpc-SamSJPortfolio
- Compute: ECS Fargate service `report-gen-service-SamSJPortfolio`
- Storage: S3 bucket `reports-SamSJPortfolio-us-west-2`
- Database: RDS Postgres `reporting-db-SamSJPortfolio`

## Getting Started
1. Install AWS CLI and Docker.
2. Configure AWS CLI: `aws configure` with us-west-2.
3. Run locally using Docker or `npm run dev`.

## Deployment
- Build container
- Push to ECR
- Update ECS service

## Environment Variables
List required environment variables and where they live (SSM/Secrets Manager).

## Monitoring
CloudWatch logs, alarms, and dashboards.

## Security
MFA, least privilege, S3 block public access.
```

## CONTRIBUTING.md template
```md
# Contributing

## Development Setup
- Install dependencies
- Configure `.env`

## Testing
- `npm test` or `pytest`

## Linting
- `npm run lint` or `ruff`/`eslint`

## Security
Never commit secrets. Use AWS Secrets Manager and SSM.
```

---

# UI/UX Templates for Report Generator

## UI Flow
1. Dashboard → Generate Report
2. Choose data source
3. Filters + date range
4. Output format (PDF/CSV)
5. Review & generate
6. Track status in history

## Layout Template
```
Header: logo | environment badge | user menu
Sidebar: Dashboard | Generate | History | Templates | Settings
Main: page title + primary action button + content cards
Footer: version + region (us-west-2)
```

## Components
- Data source dropdown
- Date range picker (presets: 7/30/90 days)
- Filters as chips
- Output format radio buttons
- Schedule toggle (cron presets)
- Status chips (Queued/Running/Completed/Failed)

## Table Template (History)
- Columns: Report Name, Status, Format, Created By, Started, Completed, Actions
- Toolbar: search, filters, bulk actions

## Visual Tokens
- Primary: #2563EB
- Success: #10B981
- Warning: #F59E0B
- Danger: #EF4444
- Radius: 8px
- Typography: Inter/Roboto

## Accessibility
- Labels for all controls
- Keyboard navigable
- Focus states visible
- Color contrast AA
