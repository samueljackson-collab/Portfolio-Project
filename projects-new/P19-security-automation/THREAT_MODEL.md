# Threat Model

Threats:
- Over-permissive remediation role
- False positives muting real issues
- Webhook tampering

Mitigations:
- Scoped IAM roles
- Two-tier severity routing
- Signed webhook payloads and WAF
