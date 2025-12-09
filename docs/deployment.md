# Deployment Guide
1. Confirm AWS credentials are exported or stored in a profile with permissions to deploy.
2. Clone the repository and change into the infrastructure directory for the project.
3. Review terraform.tfvars.example and create a terraform.tfvars file with environment values.
4. Validate the vpc cidr, subnet counts, and tags match the target environment requirements.
5. Run `terraform init` to download providers and set up the backend configuration.
6. Execute `terraform fmt` to ensure formatting consistency before committing changes.
7. Use `terraform validate` to check that the configuration is syntactically correct.
8. Plan the deploy by running `terraform plan -out plan.out` to preview the execution graph.
9. Review the plan output carefully, confirming vpc, subnet, nat gateway, and ec2 details.
10. Apply the infrastructure with `terraform apply plan.out` when the plan looks correct.
11. For smaller changes you can also run `terraform apply` directly after confirming the diff.
12. Monitor the AWS console or CLI to confirm resources create successfully during the apply.
13. Capture the outputs for vpc ids, public_subnet_ids, and any EC2 public_ip values.
14. If errors occur, inspect the state file and recent changes before retrying `terraform apply`.
15. To destroy a non-production environment run `terraform destroy` after double-checking the workspace.
16. Use workspaces or separate state buckets to isolate dev, staging, and prod deployments.
17. Lock the state with DynamoDB when running `terraform init` in team environments.
18. For automated pipelines, integrate `terraform fmt`, `validate`, `plan`, and `apply` steps into CI.
19. Store sensitive variables like db_password in environment variables or a secrets manager, not in git.
20. After a successful deploy, document the applied version and tag the repository for traceability.
21. Periodically rotate credentials and review security groups to ensure least privilege is maintained.
22. When adding new modules, rerun `terraform init` to download any new provider dependencies.
23. Use `terraform state pull` and `terraform state list` for troubleshooting drift scenarios.
24. Always back up remote state and enable versioning on the storage bucket to protect history.
