# Deployment Guide

This repository export focuses on documenting the deployment process rather than providing runnable automation.

## Continuous Delivery

This repository does not include the automation from the original project: there is no .github/workflows directory and no pipelines will run automatically after a push.

## Reproducing the release process

1. Terraform provisioning
   - Run Terraform from an environment with access to your state backend and credentials:
     - terraform init
     - terraform plan -out=tf.plan
     - terraform apply tf.plan
   - Use a remote state backend (for example: S3, Consul, or Terraform Cloud) and secret management.

2. Build and publish container images
   - Build and push images before deploying:
     - docker build -t registry.example.com/<org>/<repo>:<tag> .
     - docker push registry.example.com/<org>/<repo>:<tag>
   - Replace registry.example.com with your container registry (Docker Hub, GHCR, ECR, etc.).

3. Security and compliance scans
   - Run static and image scans locally or in your private CI:
     - terraform validate && tflint && tfsec .
     - trivy image registry.example.com/<org>/<repo>:<tag>
   - Do not promote releases until scans pass.

4. Deploy to target environment
   - Deploy using your chosen mechanism (kubectl/helm/ops tool):
     - kubectl apply -f manifests/
     - helm upgrade --install my-release ./chart --set image.tag=<tag>

## Notes and troubleshooting

- This file documents the manual process required to reproduce deployments; it intentionally does not include workflow definitions.
- Ensure credentials, registry access, and network access are available to the environment performing these actions.
- If you’d like example GitHub Actions workflows or sample pipelines for private use, I can add them.

Why keep this documentation
- Keeps instructions truthful to what exists in the repository while preserving the option to recreate automation privately.