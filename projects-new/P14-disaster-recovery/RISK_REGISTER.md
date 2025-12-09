# Risk Register

| Risk | Impact | Likelihood | Mitigation | Owner |
| --- | --- | --- | --- | --- |
| Restore exceeds RTO | High | Medium | Tune compression, parallelize restores, rehearse quarterly | DR Team |
| Backups missing critical tables | High | Low | Use backup manifest + post-backup validation scripts | DBA |
| Offsite bucket access compromised | Critical | Low | KMS CMK with rotation, VPC endpoints, MFA delete | Security |
