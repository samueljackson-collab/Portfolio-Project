# Deployment Attempt Log (Terraform)

## Summary
- **Goal:** Deploy `projects/9-multi-region-disaster-recovery/terraform` into two regions (primary + DR).
- **Outcome:** Deployment not executed because the environment lacks the Terraform CLI.

## Commands & Output
```bash
$ terraform -version
bash: command not found: terraform
```

## Next Steps
1. Install Terraform in the execution environment.
2. Re-run deployment with region-scoped variables:
   ```bash
   cd projects/9-multi-region-disaster-recovery/terraform
   terraform init
   terraform apply -var-file=production.tfvars
   ```
3. Capture apply output for both regions and attach to this evidence directory.
