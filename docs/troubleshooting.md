# Troubleshooting Guide

Use this checklist to resolve the most common problems encountered while working with the repository skeleton and Terraform workflows.

## Terraform Init Errors

- Confirm that the AWS credentials used locally have permission to access the backend S3 bucket and DynamoDB table if remote state is enabled.
- Delete the `.terraform` directory if provider downloads became corrupted, then rerun `terraform init`.
- Double-check that the Terraform version installed locally matches the version pinned in CI (`1.6.x`).

## Validation Failures in CI

- Inspect the GitHub Actions logs to see which step failed (format, init, validate, tflint, or security scan).
- Ensure that all Terraform files have been formatted with `terraform fmt`.
- Verify that any new modules or directories are included in the workflow's `working-directory` or invocation paths.

## GitHub Actions Cannot Access AWS

- Confirm that the `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_REGION` secrets are defined in the repository settings.
- Make sure the IAM user or role associated with the credentials has permissions for Terraform to read and write the required services.
- If using OIDC, update the workflow to assume the correct role and trust policy.

## GitHub Pages Not Publishing

- Ensure that the `docs-site/index.html` file exists and that GitHub Pages is configured to serve from the `docs-site` directory.
- Allow a few minutes for GitHub Pages to build and deploy after pushing changes.
- Check the Pages build logs (if available) for warnings about mixed content or missing files.

## Branch Protection Conflicts

- Update your local branch with `git fetch --all` followed by `git pull --rebase origin main` before pushing new commits.
- Resolve merge conflicts locally before opening a pull request.
- Ensure that the required status checks pass; otherwise, main will reject the merge.
