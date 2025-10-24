# Release Notes — v0.1.0 (2025-10-24)

## Highlights

- Added contributor documentation and repository hygiene files to make onboarding easier and prevent accidental commits of secrets or state.
  - .gitignore: exclude Terraform state, tfvars, IDE files, logs, and other common temporary files.
  - docs/github-repository-setup-guide.md: quickstart for cloning, local Terraform validation, CI guidance, and secrets guidance.
  - SECURITY.md: top-level security disclosure guidance pointing to docs/security.md.

- Improved Terraform RDS module safety and configurability:
  - Added module variables skip_final_snapshot (default: false) and apply_immediately (default: true) to avoid unconditional destructive behavior on destroy.
  - Wired the new variables through from root variables so operators can opt into skipping final snapshots explicitly.

## Merged PRs

- #46 — Add docs, .gitignore and safer RDS variables (merged via squash, commit 0c22758b5d59428adb28fa77eb04ea4e60a51eb6)

## Notes for operators

- The default behavior preserves a final RDS snapshot on destroy (skip_final_snapshot = false). If you intentionally want to skip final snapshots, set db_skip_final_snapshot = true in your terraform.tfvars (NOT committed to version control).
- Review CI checks (terraform fmt, validate, tflint) before merging future infra changes.

---

Released by: samueljackson-collab
Date: 2025-10-24
