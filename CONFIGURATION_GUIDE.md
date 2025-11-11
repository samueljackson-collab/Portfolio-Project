# Portfolio Configuration Guide

This guide explains how to configure the various components of this enterprise portfolio for deployment.

## Table of Contents

1. [Terraform Backend Configuration](#terraform-backend-configuration)
2. [Environment Variables](#environment-variables)
3. [IAM Policy Configuration](#iam-policy-configuration)
4. [Alertmanager Configuration](#alertmanager-configuration)
5. [Database Configuration](#database-configuration)
6. [Security Best Practices](#security-best-practices)

---

## Terraform Backend Configuration

### Location
`/terraform/backend.tf`

### Current State
The backend configuration is set up for local state by default. To use S3 remote state:

### Setup Instructions

1. **Run the bootstrap script** to create required AWS resources:
   ```bash
   cd scripts
   ./bootstrap_remote_state.sh <project-name> <aws-region>

   # Example:
   ./bootstrap_remote_state.sh my-portfolio us-east-1
   ```

2. **The script will output** the bucket name and DynamoDB table name.

3. **Uncomment and configure** the S3 backend block in `/terraform/backend.tf`:
   ```hcl
   terraform {
     backend "s3" {
       bucket         = "my-portfolio-tfstate-xxxxx"  # From bootstrap output
       key            = "my-portfolio/terraform.tfstate"
       region         = "us-east-1"
       dynamodb_table = "my-portfolio-tfstate-lock"   # From bootstrap output
       encrypt        = true
     }
   }
   ```

4. **Initialize Terraform**:
   ```bash
   terraform init
   ```

   Terraform will migrate your local state to S3.

### Why This Approach?

- **No placeholders to replace**: The bootstrap script generates actual values
- **Secure by default**: Encryption and locking enabled automatically
- **Version controlled**: You track the backend config, not the secrets

---

## Environment Variables

### For Homelab Projects

**Location**: `/projects/06-homelab/PRJ-HOME-002/assets/configs/example.env`

**Setup**:
```bash
cd projects/06-homelab/PRJ-HOME-002/assets/configs/
cp example.env .env
chmod 600 .env
nano .env  # Edit with your actual values
```

**Key Variables**:
- `POSTGRES_SUPERUSER_PASSWORD`: PostgreSQL admin password
- `GRAFANA_ADMIN_PASSWORD`: Grafana dashboard access
- `ALERTMANAGER_SMTP_PASSWORD`: Email notification credentials
- `CLOUDFLARE_API_TOKEN`: DNS and SSL management

**Security Notes**:
- `.env` is in `.gitignore` - never commit it
- Use strong passwords (32+ characters): `openssl rand -base64 32`
- Store backup copy in password manager (Bitwarden/1Password)
- Rotate credentials quarterly (schedule in example.env comments)

### For AWS Projects

Set these in your shell or CI/CD pipeline:

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

**For GitHub Actions**, use encrypted secrets (never hardcode).

---

## IAM Policy Configuration

### Location
`/terraform/iam/policy-config.example.json`

### Setup Instructions

1. **Copy the example file**:
   ```bash
   cd terraform/iam/
   cp policy-config.example.json policy-config.json
   ```

2. **Edit with your AWS values**:
   ```json
   {
     "variables": {
       "TFSTATE_BUCKET_NAME": "my-portfolio-tfstate-xxxxx",
       "TFSTATE_LOCK_TABLE": "my-portfolio-tfstate-lock",
       "AWS_REGION": "us-east-1",
       "AWS_ACCOUNT_ID": "123456789012",
       "PROJECT_NAME": "my-portfolio"
     }
   }
   ```

3. **Generate the final policy**:
   ```bash
   # Export variables from config
   export $(jq -r '.variables | to_entries | .[] | "\(.key)=\(.value)"' policy-config.json)

   # Substitute into policy template (run from repository root)
   envsubst < terraform/iam/github_actions_ci_policy.json > terraform/iam/github_actions_ci_policy_final.json
   ```

4. **Create IAM policy in AWS**:
   ```bash
   aws iam create-policy \
     --policy-name GitHubActionsTerraformPolicy \
     --policy-document file://terraform/iam/github_actions_ci_policy_final.json
   ```

5. **Add to .gitignore**:
   ```bash
   echo "policy-config.json" >> .gitignore
   echo "terraform/iam/github_actions_ci_policy_final.json" >> .gitignore
   ```

---

## Alertmanager Configuration

### Locations
- `/projects/01-sde-devops/PRJ-SDE-002/assets/alertmanager/alertmanager.yml`
- `/projects/06-homelab/PRJ-HOME-002/assets/configs/monitoring/alertmanager/alertmanager.yml`

### How It Works

The configuration files use **environment variable substitution**:

```yaml
global:
  smtp_auth_password: '${ALERTMANAGER_SMTP_PASSWORD}'
  slack_api_url: '${ALERTMANAGER_SLACK_WEBHOOK_URL}'
pagerduty_configs:
  - service_key: '${ALERTMANAGER_PAGERDUTY_SERVICE_KEY}'
```

### Setup Instructions

1. **Set environment variables** (from `.env` file or export):
   ```bash
   export ALERTMANAGER_SMTP_PASSWORD="your-app-specific-password"
   export ALERTMANAGER_SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/HERE"
   export ALERTMANAGER_PAGERDUTY_SERVICE_KEY="your-pagerduty-key"
   ```

2. **Substitute variables** before deploying:
   ```bash
   envsubst < alertmanager.yml > alertmanager-production.yml
   ```

3. **Deploy the production file**:
   ```bash
   docker-compose up -d alertmanager
   # or
   kubectl apply -f alertmanager-production.yml
   ```

4. **Add production file to .gitignore**:
   ```bash
   echo "alertmanager-production.yml" >> .gitignore
   ```

### Obtaining Credentials

**Gmail App Password** (for SMTP):
1. Go to https://myaccount.google.com/apppasswords
2. Create new app password for "Alertmanager"
3. Copy the 16-character password
4. Use in `ALERTMANAGER_SMTP_PASSWORD`

**Slack Webhook**:
1. Go to https://api.slack.com/messaging/webhooks
2. Create incoming webhook for your workspace
3. Select channel (e.g., #homelab-alerts)
4. Copy webhook URL
5. Use in `ALERTMANAGER_SLACK_WEBHOOK_URL`

**PagerDuty Service Key**:
1. Login to PagerDuty
2. Go to Services > Select Service > Integrations
3. Add Integration > Events API V2
4. Copy Integration Key
5. Use in `ALERTMANAGER_PAGERDUTY_SERVICE_KEY`

---

## Database Configuration

### For Development/Testing

The DR drill and backup scripts use these environment variables:

```bash
# PostgreSQL
export DB_TYPE="postgresql"
export DB_HOST="localhost"
export DB_USER="postgres"
export DB_NAME="mydb"
export PGPASSWORD="your-db-password"

# MySQL
export DB_TYPE="mysql"
export DB_HOST="localhost"
export DB_USER="root"
export DB_NAME="mydb"
export MYSQL_PWD="your-db-password"
```

### For Homelab Services

Configure in `/projects/06-homelab/PRJ-HOME-002/assets/configs/.env`:

```bash
POSTGRES_SUPERUSER_PASSWORD="strong-password-here"
WIKIJS_DB_PASSWORD="unique-password-for-wikijs"
HOMEASSISTANT_DB_PASSWORD="unique-password-for-homeassistant"
IMMICH_DB_PASSWORD="unique-password-for-immich"
```

Each service gets its own database and user for isolation.

---

## Security Best Practices

### Never Commit Secrets

**Always in .gitignore**:
```
.env
*.production.yml
policy-config.json
*_final.json
terraform.tfvars
deployments.json
```

### Use Environment-Specific Configs

```
config/
├── example.env              # Committed (template with placeholders)
├── .env                     # NOT committed (actual secrets)
├── alertmanager.yml         # Committed (uses ${VARS})
└── alertmanager-production.yml  # NOT committed (substituted values)
```

### Password Generation

**Strong passwords**:
```bash
# 32-character base64 password
openssl rand -base64 32

# 64-character hex string
openssl rand -hex 32

# Alphanumeric with symbols
pwgen -s 40 1
```

### Credential Rotation Schedule

From `example.env`:

| Credential Type | Rotation Frequency | Example |
|----------------|-------------------|---------|
| Database passwords | Every 3 months | POSTGRES_PASSWORD |
| API tokens | Every 6 months | CLOUDFLARE_API_TOKEN |
| Session secrets | Every 6 months | WIKIJS_SESSION_SECRET |
| VPN keys | Every 12 months | WIREGUARD_PRIVATE_KEY |

### Encrypted Backup

**Encrypt secrets before backup**:
```bash
# Encrypt
gpg -c .env
# Creates .env.gpg

# Decrypt (when needed)
gpg -d .env.gpg > .env
chmod 600 .env
```

**Store in password manager**:
- Bitwarden: Secure Note with .env contents
- 1Password: Document with .env contents
- Enable 2FA on password manager
- Set up emergency access

---

## Deployment Checklist

Before deploying to production:

- [ ] Copy all `example.env` files to `.env` and fill in real values
- [ ] Generate strong passwords for all services (32+ chars)
- [ ] Run Terraform bootstrap script for S3 backend
- [ ] Configure IAM policies with actual AWS account ID
- [ ] Substitute environment variables in alertmanager configs
- [ ] Verify all `.env` and `*-production.yml` files are in `.gitignore`
- [ ] Test database backups actually create files
- [ ] Test DR drill can decompress backups
- [ ] Store encrypted backup of secrets in password manager
- [ ] Set up credential rotation reminders (quarterly)
- [ ] Enable AWS CloudTrail for audit logging
- [ ] Set up AWS Budgets alerts (50%, 80%, 100%)
- [ ] Review and tighten IAM policies (least privilege)
- [ ] Enable MFA on all AWS IAM users

---

## Troubleshooting

### "Backend configuration changed" error

You enabled S3 backend but didn't run `terraform init`. Run:
```bash
terraform init -migrate-state
```

### "Authentication failed" in alertmanager

Check that environment variables are set:
```bash
echo $ALERTMANAGER_SMTP_PASSWORD
```

If empty, source your .env file:
```bash
set -a
source .env
set +a
```

### Database backup file is empty

The backup command might not have correct credentials. Check:
```bash
# PostgreSQL
echo $PGPASSWORD
# or create ~/.pgpass file

# MySQL
echo $MYSQL_PWD
# or create ~/.my.cnf file
```

### DR drill fails to find backups

Check `BACKUP_DIR` environment variable points to correct location:
```bash
export BACKUP_DIR="/path/to/actual/backups"
python3 scripts/dr_drill.py
```

---

## Additional Resources

- [Terraform Backend Documentation](https://www.terraform.io/docs/language/settings/backends/s3.html)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Alertmanager Configuration Reference](https://prometheus.io/docs/alerting/latest/configuration/)
- [PostgreSQL Password File](https://www.postgresql.org/docs/current/libpq-pgpass.html)
- [MySQL Option Files](https://dev.mysql.com/doc/refman/8.0/en/option-files.html)

---

**Questions?** Check individual project READMEs or open an issue in the repository.
