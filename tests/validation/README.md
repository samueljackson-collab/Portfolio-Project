# Terraform validation and policy-as-code checks

This directory houses pytest helpers that run Terraform validation alongside `tfsec` and `Checkov` security scans. These tests are wired into `terraform/scripts/validate.sh` so you can run everything from a single entry point.

## Running the checks directly with pytest

```bash
python -m pytest tests/validation -q
```

Tools are optional; each test gracefully skips itself when the required binary is not present.

## Running via the helper script

The preferred way to execute validation locally or in CI is to call:

```bash
bash terraform/scripts/validate.sh
```

The script will:

1. Initialize and validate the Terraform configuration under `terraform/`.
2. Run `tfsec` against the same directory when installed.
3. Run `Checkov` against the same directory when installed.
4. Invoke the pytest suite in this folder for consistent reporting.

Set `TF_IN_AUTOMATION=true` (done automatically by pytest) to avoid interactive prompts when running Terraform in CI environments.
