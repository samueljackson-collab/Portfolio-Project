# Threat Model

Threats:
- Workflow execution abuse
- Unvetted automation making prod changes
- Secrets in workflow history

Mitigations:
- RBAC on namespaces/queues
- Approval steps for high-risk tasks
- Secret redaction in logs
