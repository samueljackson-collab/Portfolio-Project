# Automation Notes (Private)

These notes capture the intent behind the automation assets that previously carried
high-level instructions directly inside the workflow definitions. Keep this file in
maintainers-only sharing channels when discussing execution details.

## Terraform workflow
- Validates Terraform formatting, initializes providers, and runs `terraform validate` on every change.
- Manual runs (`workflow_dispatch`) can execute a plan/apply cycle by setting `apply=true` once AWS credentials are provided.
- State is expected in the `infrastructure/terraform` directory with environment overrides under `env/`.

## Deploy workflow
- Pull requests execute the deployment script in `--dry-run` mode to rehearse Terraform and Kubernetes changes.
- Manual runs install Terraform, `kubectl`, and Flyway before invoking the deployment and migration scripts against the selected environment.
- Successful runs assume AWS credentials and kubeconfig access for the portfolio cluster.

## Security workflow
- Installs Trivy, Syft, and Conftest before executing `scripts/compliance-scan.sh` against the requested image.
- SBOM output (`sbom.json`) is uploaded as a workflow artifact for traceability.
- Policy evaluations target the Rego definitions stored with the security policies.
