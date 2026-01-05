# Risk Register

| Risk | Impact | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Backend misconfigured | High | Low | `scripts/validate_backends.sh` before apply | Platform |
| Provider version pinning missed | Medium | Medium | Dependabot + lockfiles | DevOps |
| Apply in wrong workspace | High | Low | Terragrunt wrappers enforce env, CI checks context | SRE |
