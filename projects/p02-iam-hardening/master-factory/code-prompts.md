# Code Prompts — P02 IAM Hardening Master Factory

Use these prompts when collaborating with AI or reviewers to keep IAM work aligned with least privilege, Access Analyzer feedback, MFA enforcement, and unused credential cleanup.

## Policy Authoring
- "Generate an IAM policy that grants only the minimum S3 actions for the listed prefixes; include session MFA requirements and note how `make simulate` will validate it against Access Analyzer findings."
- "Rewrite this wildcard-heavy policy into least-privilege statements, then outline the expected `make validate-policies` and `make policy-diff` outputs before merging."

## Access Analyzer and MFA Checks
- "Given the Access Analyzer report, propose policy updates that remove external access while keeping automation working; show how to verify via `make simulate` and MFA test hooks."
- "Suggest automated cleanups for unused IAM roles/keys and describe how `make test` should assert the cleanup jobs run with MFA enforced."

## CI/CD and IaC
- "Describe the CI/CD gate that runs `make setup`, `make validate-policies`, `make policy-diff`, and `make simulate`; ensure Access Analyzer and MFA checks block promotion until clean."
- "For a Terraform change, produce a plan review script that maps IAM resources to Access Analyzer scans and flags any changes that weaken least privilege before `terraform apply`."

## Operational Guardrails
- "Draft rollback steps that reapply the last known-good IAM bundle, rerun `make validate-policies`, and confirm MFA enforcement for break-glass roles."
- "Propose monitoring queries that detect external access introductions and unused credentials, and describe how they feed `reporting.md` KPIs."
