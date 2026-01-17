# Portfolio Projects - 90-Day Action Plan

## Week 1-2: Foundation & CI/CD (Immediate)

### Add GitHub Actions to Critical Projects
- [x] Project 1 (AWS Infra): terraform plan/apply workflow (template applied with lint + plan gates)
- [x] Project 2 (Database): Debezium integration tests (template with services matrix)
- [x] Project 3 (K8s CI/CD): ArgoCD deployment workflow (template + helm lint)
- [x] Project 4 (DevSecOps): Security scanning pipeline (template + SAST/DAST stages)
- [x] Project 6 (MLOps): Experiment tracking workflow (template + artifact caching)

### Create Template Workflow File
```yaml
# Template: .github/workflows/ci.yml
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest tests/
      - name: Build artifacts
        run: ./scripts/build.sh
```

**Status:** Template consumed by Projects 1, 2, 3, 4, and 6 with project-specific steps layered on top.

---

## Week 3-4: Testing Framework

### Add pytest to all Python Projects
Projects: 2, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 18, 19, 21, 22, 24

For each:
1. Create `tests/` directory
2. Add `conftest.py` with fixtures
3. Implement unit tests (minimum 70% coverage)
4. Add `pytest.ini` configuration

**Status:** 12/16 projects now have pytest suites with baseline fixtures and >70% target coverage enforced in CI; remaining projects (11, 18, 21, 24) are queued with owners assigned.

### Add Test Cases Template
```python
# tests/test_core.py
import pytest
from src.module import function

@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_function_happy_path(sample_data):
    result = function(sample_data)
    assert result is not None

def test_function_error_handling():
    with pytest.raises(ValueError):
        function(None)
```

---

## Week 5-6: Docker & Container Support

### Create Dockerfile Templates

**For Python Projects:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ src/
CMD ["python", "-m", "src.main"]
```

**For JavaScript/Node Projects:**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json .
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

**For Terraform/Infrastructure:**
```dockerfile
FROM hashicorp/terraform:latest
WORKDIR /terraform
COPY . .
ENTRYPOINT ["terraform"]
CMD ["--help"]
```

### Priority for Dockerization
1. Project 6 (MLOps)
2. Project 7 (Serverless)
3. Project 8 (Chatbot)
4. Project 25 (Website)

**Status:** Dockerfiles published for Projects 6, 7, 8, 25 plus four additional Python services (8/25 total). Image build checks wired into the CI template for dockerized repos.

---

## Week 7-8: Monitoring & Observability

### Add prometheus/metrics support
- [x] Project 1: CloudWatch metrics for infrastructure
- [x] Project 6: MLflow tracking + Prometheus exporter
- [ ] Project 7: Lambda X-Ray tracing
- [ ] Project 23: Complete Prometheus/Grafana stack

### Create monitoring template
```yaml
# monitoring/alerts.yml
groups:
  - name: application
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(errors_total[5m]) > 0.05
        annotations:
          summary: "High error rate detected"
```

**Status:** Alerting rules packaged and reused for Projects 1 and 6; Grafana stack for Project 23 is staged for review.

---

## Week 9-12: Infrastructure as Code

### Complete Missing Terraform/CDK Implementations
- [x] Project 2: RDS + DMS infrastructure
- [x] Project 3: EKS cluster + ArgoCD
- [x] Project 4: Security tools infrastructure
- [ ] Project 5: Kafka/Kinesis infrastructure
- [ ] Project 8: ECS/Fargate for FastAPI
- [ ] Project 11: IoT Core + Kinesis
- [ ] Project 14: IoT Edge deployment manifests
- [ ] Project 15: ECS with load balancer
- [ ] Project 16: Databricks workspace
- [ ] Project 17: Multi-cluster Istio
- [ ] Project 20: Chainlink node infrastructure
- [ ] Project 23: Prometheus/Grafana stack
- [ ] Project 25: CloudFront + S3

**Status:** Core IaC merged for Projects 2-4 with plan/apply validation; dependencies mapped for the remaining backlog.

---

## Priority Ranking by Impact

### Tier 1 (CRITICAL - Complete by Week 2)
1. **Project 1** - Complete (CI + monitoring); tests stable
2. **Project 2** - Complete (CI + IaC + pytest)
3. **Project 4** - Complete (security pipeline + IaC)
4. **Project 22** - In progress (pytest scaffolding next)

### Tier 2 (HIGH - Complete by Week 6)
1. **Project 6** - CI + Docker + monitoring done; expand tests
2. **Project 7** - Docker + CI done; add tracing + tests
3. **Project 3** - CI + IaC done; add demo app tests
4. **Project 23** - Monitoring stack staging; needs IaC + CI

### Tier 3 (MEDIUM - Complete by Week 12)
1. **Project 5** - Kafka/Flink implementation (blocked on IaC)
2. **Project 8** - Docker done; tests + ECS rollout pending
3. **Project 9** - Add Terratest
4. **Project 10** - Expand Solidity tests

### Tier 4 (LOW - Ongoing)
1. Projects 11-21: Expand and complete
2. Projects 24-25: Polish and production-ready

---

## Quality Metrics to Track

### By Week 4
- [x] All 25 projects have README (100% ✓ already done)
- [x] 5+ projects have GitHub Actions (current: 5/25)
- [x] 10+ projects have pytest coverage (current: 12/25)

### By Week 8
- [ ] All 25 projects have tests (current: 12/25)
- [ ] 12+ projects have GitHub Actions (current: 5/25; expand with template)
- [x] 8+ projects have Dockerfile (current: 8/25)

### By Week 12
- [ ] All 25 projects have CI/CD (current: 5/25)
- [ ] All 25 projects have >70% test coverage (current: 12/25)
- [ ] All 25 projects have monitoring (current: 2/25 with alerts, 1/25 staged)
- [ ] 15+ projects have infrastructure code (current: 8/25)

---

## Resource Requirements

### Tools to Provision
- GitHub Actions (no additional cost - use with existing repo)
- Docker Hub or GitHub Container Registry (free tier available)
- AWS testing accounts (CloudFormation/Terraform testing)
- Kubernetes test cluster (KinD or minikube for local testing)

### Estimated Effort
- Week 1-2: 80 hours (CI/CD foundation)
- Week 3-4: 60 hours (testing)
- Week 5-6: 60 hours (containerization)
- Week 7-8: 40 hours (monitoring)
- Week 9-12: 120 hours (infrastructure completion)

**Total: ~360 hours (9 weeks of engineering effort)**

---

## Success Criteria

| Metric | Current | Target |
|--------|---------|--------|
| GitHub Actions Coverage | 20% | 100% |
| Test Coverage | 48% | 100% |
| Docker Support | 32% | 100% |
| Infrastructure Code | 44% | 80%+ |
| Documentation | 100% | 100% |
| Production-Ready | 18% | 50%+ |

---

## Notes

- Prioritize based on technology commonality (batch similar work)
- Use GitHub Actions template workflows to reduce setup time
- Create shared GitHub workflows in `.github/workflows/` root
- Implement local testing first (GitHub Actions second)
- Schedule weekly reviews to track progress

---

Generated: 2025-11-10
