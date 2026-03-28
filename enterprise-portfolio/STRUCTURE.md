# Enterprise Portfolio Structure

The repository is organized to keep documentation, automation, and deployable projects in predictable
locations. The top-level layout is illustrated below (non-executable files omitted for brevity).

```
enterprise-portfolio/
├── .github/workflows/deploy.yml
├── README.md
├── STRUCTURE.md
├── PROJECTS.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── ROADMAP.md
│   └── STRATEGY.md
├── monitoring/
│   ├── alerts/alerts.yaml
│   ├── grafana/dashboards/overview.json
│   └── prometheus/prometheus.yml
├── kubernetes/
│   ├── manifests/
│   │   ├── applications/sample-app.yaml
│   │   ├── argocd/
│   │   │   ├── applicationset.yaml
│   │   │   └── namespace.yaml
│   │   └── istio/gateway.yaml
│   ├── helm-charts/
│   │   ├── app-backend/
│   │   │   ├── Chart.yaml
│   │   │   └── values.yaml
│   │   ├── app-frontend/
│   │   │   ├── Chart.yaml
│   │   │   └── values.yaml
│   │   └── monitoring/
│   │       ├── Chart.yaml
│   │       └── values.yaml
│   └── operators/README.md
├── scripts/
│   ├── deploy-all.sh
│   ├── deploy-category.sh
│   ├── deploy-project.sh
│   ├── list-projects.sh
│   ├── portfolio-validator.py
│   ├── validate-deployment.sh
│   ├── monitoring/check-prometheus.sh
│   └── validation/schema-lint.sh
├── terraform/
│   ├── main.tf
│   ├── outputs.tf
│   ├── variables.tf
│   ├── environments/
│   │   ├── dev/terraform.tfvars
│   │   ├── staging/terraform.tfvars
│   │   └── prod/terraform.tfvars
│   ├── modules/
│   │   ├── eks/
│   │   │   ├── main.tf
│   │   │   ├── outputs.tf
│   │   │   └── variables.tf
│   │   ├── monitoring/
│   │   │   ├── main.tf
│   │   │   ├── outputs.tf
│   │   │   └── variables.tf
│   │   ├── network/
│   │   │   ├── main.tf
│   │   │   ├── outputs.tf
│   │   │   └── variables.tf
│   │   └── security/
│   │       ├── main.tf
│   │       ├── outputs.tf
│   │       └── variables.tf
│   └── state/README.md
└── projects/
    ├── cloud-infrastructure/
    │   ├── aws-landing-zone/
    │   ├── cost-optimization-engine/
    │   ├── disaster-recovery-automation/
    │   ├── multi-cloud-kubernetes/
    │   ├── network-hub-spoke/
    │   └── serverless-platform/
    ├── security-compliance/
    │   ├── cloud-security-posture/
    │   ├── compliance-as-code/
    │   ├── container-security/
    │   ├── secrets-management/
    │   ├── security-hub-automation/
    │   └── zero-trust-architecture/
    ├── devops-automation/
    │   ├── chatops-automation/
    │   ├── ci-cd-pipelines/
    │   ├── gitops-platform/
    │   ├── infrastructure-as-code/
    │   ├── monitoring-stack/
    │   └── self-service-platform/
    ├── full-stack-apps/
    │   ├── microservices-ecommerce/
    │   ├── mobile-backend/
    │   ├── react-enterprise-app/
    │   ├── real-time-dashboard/
    │   ├── serverless-api-gateway/
    │   └── websocket-platform/
    └── data-engineering/
        ├── bi-dashboard-platform/
        ├── data-governance/
        ├── data-lake-formation/
        ├── mlops-platform/
        ├── real-time-data-pipeline/
        └── streaming-analytics/
```

Every project directory contains a `README.md`, `deploy.sh`, `validate.sh`, a Terraform stub, and
optionally Kubernetes manifests and integration scripts. Projects can be enabled progressively without
breaking the overall automation because each script performs existence checks before running tools.

Use `PROJECTS.md` for detailed descriptions, owners, and deployment commands.
