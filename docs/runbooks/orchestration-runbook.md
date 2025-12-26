# Orchestration Runbook

This runbook documents how to execute and verify platform rollouts using the orchestrator API, Terraform environments, and Ansible playbooks.

## Prerequisites
- Terraform >= 1.6 installed for local execution
- AWS credentials with permissions for VPC, ECS, RDS, and S3
- Ansible >= 2.15 with Docker and community.docker collection available
- Access to the operations console (`/operations`) with an authenticated account

## Standard change (staging/production)
1. **Select plan**: Choose `staging-bluegreen` or `prod-controlled` from the console or call `POST /orchestration/runs` with the plan id and change ticket metadata.
2. **Terraform plan/apply**: From `infrastructure/terraform/environments`, run `terraform init -backend-config="workspace=<env>" -reconfigure` followed by `terraform apply -var-file=<env>.tfvars`.
3. **Configuration drift check**: Validate state with `terraform plan -detailed-exitcode` before approval.
4. **Ansible deploy**: Execute `ansible-playbook -i inventory/hosts.ini playbooks/site.yml -e "target=<env> deployment_channel=planned"` to roll out the container.
5. **Observability smoke**: Confirm traces and metrics in Grafana dashboard `Portfolio Orchestration Overview` and validate OTEL exporter target.
6. **Change closure**: Attach run output and Grafana screenshots to the change ticket referenced in the orchestration parameters.

## Emergency path
1. Use the `emergency` window option and include the incident ticket number as `change_ticket`.
2. Run `terraform apply -parallelism=4 -var-file=<env>.tfvars` to minimize execution time.
3. Use the Ansible role with `deployment_channel=emergency` to annotate deployment metadata.
4. Post-deploy, revert to `standard` and schedule a follow-up stability verification.

## Rollback
1. Re-run the previous stable image tag by setting `app_image` in `group_vars/all.yml` and re-running the Ansible playbook.
2. Restore database snapshots from RDS using the timestamp recorded in `logs/deployment.json` on the target host.
3. Validate health via `/health` and Grafana latency panels before closing the rollback.
