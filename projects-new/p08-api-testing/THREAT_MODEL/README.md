# Threat Model

## Assets
- API access tokens
- Test data payloads
- Reports and logs

## Threats
- Leakage of real secrets in Postman environments.
- Malicious schema injection causing false positives/negatives.
- Tampering with test reports to hide regressions.

## Mitigations
- Store secrets in vault/CI variables; only template values in repo.
- Sign schemas and validate checksum before runs.
- Immutable report artifacts with checksum validation in `consumer/report.py`.
