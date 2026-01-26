# Portfolio Projects - 90-Day Action Plan

## Week 1-2: Foundation & CI/CD (Immediate)

### Add GitHub Actions to Critical Projects
- [ ] Project 1 (AWS Infra): terraform plan/apply workflow
- [ ] Project 2 (Database): Debezium integration tests
- [ ] Project 3 (K8s CI/CD): ArgoCD deployment workflow
- [ ] Project 4 (DevSecOps): Security scanning pipeline
- [ ] Project 6 (MLOps): Experiment tracking workflow

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

---

## Week 3-4: Testing Framework

### Add pytest to all Python Projects
Projects: 2, 5, 6, 7, 8, 11, 12, 13, 14, 15, 16, 18, 19, 21, 22, 24

For each:
1. Create `tests/` directory
2. Add `conftest.py` with fixtures
3. Implement unit tests (minimum 70% coverage)
4. Add `pytest.ini` configuration

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

---

## Week 7-8: Monitoring & Observability

### Add prometheus/metrics support
- [ ] Project 1: CloudWatch metrics for infrastructure
- [ ] Project 6: MLflow tracking + Prometheus exporter
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

---

## Week 9-12: Infrastructure as Code

### Complete Missing Terraform/CDK Implementations
- [ ] Project 2: RDS + DMS infrastructure
- [ ] Project 3: EKS cluster + ArgoCD
- [ ] Project 4: Security tools infrastructure
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

---

## Priority Ranking by Impact

### Tier 1 (CRITICAL - Complete by Week 2)
1. **Project 1** - Already 80% complete, just needs tests
2. **Project 2** - Only 20 LOC, needs full implementation
3. **Project 4** - Security critical
4. **Project 22** - Needs runbook engine

### Tier 2 (HIGH - Complete by Week 6)
1. **Project 6** - MLOps, most complete after tier 1
2. **Project 7** - Serverless, needs Lambda tests
3. **Project 3** - K8s pipeline needs demo app
4. **Project 23** - Monitoring stack needed

### Tier 3 (MEDIUM - Complete by Week 12)
1. **Project 5** - Kafka/Flink implementation
2. **Project 8** - Add Docker + tests
3. **Project 9** - Add Terratest
4. **Project 10** - Expand Solidity tests

### Tier 4 (LOW - Ongoing)
1. Projects 11-21: Expand and complete
2. Projects 24-25: Polish and production-ready

---

## Quality Metrics to Track

### By Week 4
- [ ] All 25 projects have README (100% ✓ already done)
- [ ] 5+ projects have GitHub Actions
- [ ] 10+ projects have pytest coverage

### By Week 8
- [ ] All 25 projects have tests
- [ ] 12+ projects have GitHub Actions
- [ ] 8+ projects have Dockerfile

### By Week 12
- [ ] All 25 projects have CI/CD
- [ ] All 25 projects have >70% test coverage
- [ ] All 25 projects have monitoring
- [ ] 15+ projects have infrastructure code

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
| GitHub Actions Coverage | 0% | 100% |
| Test Coverage | 4% | 100% |
| Docker Support | 4% | 100% |
| Infrastructure Code | 28% | 80%+ |
| Documentation | 100% | 100% |
| Production-Ready | 8% | 50%+ |

---

## Notes

- Prioritize based on technology commonality (batch similar work)
- Use GitHub Actions template workflows to reduce setup time
- Create shared GitHub workflows in `.github/workflows/` root
- Implement local testing first (GitHub Actions second)
- Schedule weekly reviews to track progress

---

Generated: 2025-11-10
