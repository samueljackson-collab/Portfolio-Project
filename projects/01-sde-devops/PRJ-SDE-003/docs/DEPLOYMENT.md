# Deployment Procedures

1. Configure remote state in `terraform/environments/<env>/backend.tf` and provide credentials.
2. Populate `terraform/environments/<env>/terraform.tfvars` using the provided example file.
3. Run `terraform init`, `terraform validate`, and `terraform plan` using the wrappers in `terraform/scripts/`.
4. Apply changes after review and monitor CloudWatch alarms during rollout.

Use staging for full validation before promoting the same configuration to production.
