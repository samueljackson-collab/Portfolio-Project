# Architecture

Stack: Temporal workflows, Kubernetes operators, and Python workers.

Data/Control flow: Git events trigger workflows that build, scan, deploy, and remediate; health signals feed back to adjust policies.

Dependencies:
- Temporal workflows, Kubernetes operators, and Python workers.
- Env/config: see README for required secrets and endpoints.
