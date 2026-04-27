# P01 CloudFormation Deploy Playbook

This playbook standardizes how to validate and deploy the P01 networking baseline using CloudFormation. It emphasizes template validation before any deploy and enforces a deterministic order so dependent stacks receive the correct outputs.

## Parameters and validation
- **Required parameters**: `EnvironmentName`, `VpcCIDR`, `SSHKeyName`.
- **Validation**: run `./scripts/validate.sh` before *every* deploy or change set. The script must return zero before proceeding.

## Deployment order
1. **IAM baseline** stack (creates roles, instance profiles, and stack permissions).
2. **VPC stack** (consumes IAM outputs).

## Expected VPC stack resources
- One VPC using `VpcCIDR` with DNS hostnames enabled.
- One Internet Gateway attached to the VPC.
- Public and private subnets across three AZs (at least six total).
- Three NAT Gateways (one per AZ) with elastic IPs.
- Route tables and associations for public/private paths.
- Security groups for bastion, ALB, app tier, and RDS.
- RDS subnet group spanning the private subnets.
- Stack outputs for VPC ID, subnet IDs by tier, route tables, security group IDs, and NAT allocations.

## Deploy steps (CLI)
1. Validate: `./scripts/validate.sh`
2. Package (if templates are modularized): `aws cloudformation package --template-file infra/p01/main.yml --s3-bucket <artifact-bucket> --output-template-file /tmp/p01-packaged.yml`
3. Deploy IAM baseline: `aws cloudformation deploy --template-file infra/p01/iam-baseline.yml --stack-name p01-iam-<env> --parameter-overrides EnvironmentName=<env>`
4. Deploy VPC: `aws cloudformation deploy --template-file /tmp/p01-packaged.yml --stack-name p01-vpc-<env> --capabilities CAPABILITY_NAMED_IAM --parameter-overrides EnvironmentName=<env> VpcCIDR=<cidr> SSHKeyName=<key>`

## Post-deploy verification
- Confirm three NAT gateways and public/private route table associations exist per AZ.
- Validate security group ingress/egress rules match architecture baselines.
- Export stack outputs into parameter store or `.env.<env>` for downstream stacks.
- Capture an architecture diagram PNG for the environment record.
