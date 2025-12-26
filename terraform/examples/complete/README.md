# Complete Example

This example shows how to instantiate the root Terraform configuration with VPC, application, and monitoring modules enabled.

```bash
cd terraform/examples/complete
terraform init
terraform plan -var "aws_region=us-east-1"
```

Override variables in `module "portfolio"` to fit your environment (CIDR ranges, alarms, credentials, and email). The root module automatically enables flow logs, RDS monitoring, and NAT egress unless you disable them.
