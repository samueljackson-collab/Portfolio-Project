# Deployment Guide

This portfolio export focuses on showcasing the deployment process rather than providing runnable infrastructure.

## Continuous Delivery

The original project automates Terraform provisioning, container image delivery, and security compliance checks with GitHub Actions. This export does not include those workflow definitions—there is no `.github/workflows` directory in this repository, and no pipelines will run automatically after a push.

To replicate the release process when working with this copy:

1. Run your Terraform plans and applies from your local environment or private automation that has access to your state backend.
2. Build, tag, and publish container images manually (for example with `docker build`/`push`) before deploying to your target environment.
3. Execute your compliance and security scans locally or within your own CI runner prior to promoting a release.

Documenting these steps keeps the instructions truthful to what is actually available here while preserving the option to recreate the automation privately.
