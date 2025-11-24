# Dual-region roaming simulation infrastructure

This plan provisions paired VPCs, subnets, ALBs, and security groups in two AWS regions to host the FastAPI roaming simulator. Use it for ephemeral simulation stacks or blue/green drills.

## Usage

```bash
cd infrastructure/terraform/dual-region
terraform init
terraform plan -var "project=roaming-sim" -var "primary_region=us-east-1" -var "secondary_region=us-west-2"
terraform apply
```

Key outputs:
- `regional_vpcs`: IDs and CIDRs per region
- `api_endpoints`: ALB DNS names to target with Ansible/Argo rollouts

Remote state/backends can be configured by extending `backend` blocks if required for enterprise deployments.
