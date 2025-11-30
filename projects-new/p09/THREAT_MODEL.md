# Threat Model
- Unauthorized access: use namespace RBAC and service accounts with least privilege.
- Data tampering: sign messages with HMAC in producer.
- DoS: rate-limit ingress and enable autoscaling.
