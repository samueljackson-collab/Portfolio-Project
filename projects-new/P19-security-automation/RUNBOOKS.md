# Runbooks

- Finding remediation failed: inspect SSM automation logs, rerun with debug, escalate if repeated
- GuardDuty integration broken: verify detector status, check webhook signer, resend sample finding
- Config rule drift: run `scripts/refresh_config_rules.sh` and confirm evaluation status
