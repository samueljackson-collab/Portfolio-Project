# Security Hardening Guide

- Enforce TLS on the ALB with modern ciphers; redirect HTTP to HTTPS.
- Use WAF managed rules for OWASP Top 10 coverage and custom IP reputation lists.
- Store secrets in AWS Secrets Manager and decrypt with KMS CMKs; avoid user data secrets.
- Disable SSH; use SSM Session Manager with least-privilege IAM instance profiles.
- Apply restrictive security groups and avoid `0.0.0.0/0` except on ALB listener ports.
