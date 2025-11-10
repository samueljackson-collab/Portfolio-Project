# Terraform Setup Guide for PRJ-SDE-001 Database Stack

This guide documents how to bootstrap a workstation or CI agent to manage the AWS RDS PostgreSQL module.

## 1. Install Tooling

| Tool | Version | Installation |
|------|---------|--------------|
| Terraform | 1.6.0 | `tfenv install 1.6.0 && tfenv use 1.6.0` |
| AWS CLI | 2.13.x | `pipx install awscli` |
| tflint | 0.50.x | `brew install tflint` or download from GitHub |
| tfsec | 1.28.x | `brew install tfsec` |
| Checkov | 3.x | `pipx install checkov` |
| Infracost | 0.10.x | `brew install infracost` |

Verify each binary with `--version` to confirm installation.

## 2. Configure AWS Credentials

1. Create or identify an IAM role with the permissions listed in the project README (§3).
2. If using GitHub Actions, configure OIDC federation to assume the role. On workstations run:
   ```bash
   aws configure sso
   aws sts get-caller-identity
   ```
3. Export environment variables for Terraform:
   ```bash
   export AWS_REGION=us-west-2
   export AWS_PROFILE=platform-admin
   ```

## 3. Bootstrap Remote State

```bash
aws s3api create-bucket \
  --bucket terraform-state-prod \
  --region us-west-2 \
  --create-bucket-configuration LocationConstraint=us-west-2
aws s3api put-bucket-versioning --bucket terraform-state-prod --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket terraform-state-prod \
  --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"AES256"}}]}'
aws dynamodb create-table \
  --table-name terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

## 4. Initialize the Workspace

```bash
cd infrastructure/terraform/stacks/database
cp examples/production.tfvars.example production.tfvars
terraform init \
  -backend-config="bucket=terraform-state-prod" \
  -backend-config="key=database/prod/terraform.tfstate" \
  -backend-config="dynamodb_table=terraform-locks" \
  -backend-config="region=us-west-2"
```

## 5. Policy Checks and Planning

```bash
terraform fmt -check
terraform validate
tflint
tfsec .
checkov -d .
terraform plan -var-file=production.tfvars -out=plan.out
infracost breakdown --path=. --terraform-var-file=production.tfvars
```

## 6. Apply Changes

```bash
terraform apply plan.out
```
Monitor AWS Console → RDS for status `available` and verify Multi-AZ.

## 7. Drift Detection

Run weekly (also automated via GitHub Actions):
```bash
terraform plan -refresh-only -var-file=production.tfvars
```
Open a remediation ticket if any drift is detected.

## 8. Secrets Handling

- Inject `TF_VAR_db_password` at runtime via AWS Secrets Manager or GitHub Actions secrets.
- Never commit tfvars files containing credentials.
- Rotate passwords quarterly following the runbook.

## 9. Destroying Non-Production Environments

```bash
terraform destroy -var-file=dev.tfvars
```
Ensure `skip_final_snapshot=false` unless data retention is not required.

## 10. Troubleshooting

- `ExpiredToken`: re-authenticate with SSO and retry.
- `AccessDenied`: confirm role trust policy includes deployment principal.
- `StateLock` errors: run `terraform force-unlock <LOCK_ID>` after verifying no other operations are running.

## 11. Additional References

- [AWS RDS Documentation](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Infracost Usage](https://www.infracost.io/docs/)
