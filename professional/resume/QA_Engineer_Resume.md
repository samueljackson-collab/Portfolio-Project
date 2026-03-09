# Samuel Jackson
**QA Engineer & Test Automation Specialist**

📍 Seattle, WA | 📧 samuel.jackson@example.com | 📞 (555) 123-4567
🔗 [GitHub](https://github.com/samueljackson-collab) | 🔗 [Portfolio](https://samueljackson.dev)

---

## Professional Summary

Quality-focused engineer with hands-on experience designing and executing test strategies across infrastructure, APIs, and web applications. Combines a systems engineering background with a methodical approach to uncovering defects early in the development lifecycle. Proven ability to build automated test suites, define coverage standards, and integrate quality gates into CI/CD pipelines. Passionate about building confidence in software through repeatable, evidence-based testing.

---

## Technical Skills

**Testing Frameworks:** pytest, Vitest, Playwright, React Testing Library, pytest-asyncio
**API Testing:** Postman, Newman, httpx, requests, REST/JSON schema validation
**Performance Testing:** Locust, pytest-benchmark, load profiling
**Test Management:** pytest-html, Allure, coverage.py, pytest-cov
**CI/CD & Automation:** GitHub Actions, Docker, Bash scripting, pre-commit hooks
**Languages:** Python, TypeScript, Bash
**Infrastructure Under Test:** AWS (RDS, EC2, S3), Kubernetes, Docker, PostgreSQL
**Observability:** Prometheus, Grafana, Loki (log-driven defect investigation)
**Version Control:** Git, GitHub, branch strategies and PR workflows

---

## Professional Experience

### Desktop Support Technician — 3DM, Redmond, WA
**February 2025 – Present**

- Validate enterprise application behavior and document reproducible defect steps for escalation
- Test and verify network connectivity fixes before closing tickets, preventing regression
- Maintain internal knowledge base with accurate, step-by-step resolution procedures
- Coordinate with vendors on software defect tracking and patch validation

### Freelance IT & Web Manager — Self-Employed
**2015 – 2022**

- Performed manual and scripted acceptance testing for 5+ client websites before launches
- Validated database migrations with before/after record counts and data integrity checks
- Executed regression testing after WordPress/WooCommerce plugin updates to prevent site breakage
- Documented bug reports with reproducible steps, environment details, and severity ratings

**Quality Highlights:**
- **Zero-downtime migrations:** Validated 3 database migrations with 100% data integrity verification
- **Plugin regression testing:** Maintained test checklists for 15+ WooCommerce plugin updates
- **Booking system QA:** Executed functional tests for availability logic, pricing rules, and booking flows

---

## Testing Portfolio & Projects

### API Test Suite — P08 API Testing Framework
*Test Engineering | Python, pytest, Postman/Newman | 2024*

- Designed and implemented comprehensive API test suite covering authentication, orders, and edge cases
- Built test fixtures with reusable conftest.py patterns for clean test isolation
- Integrated Newman collections for contract-level API validation
- Configured pytest-cov with 80%+ coverage enforcement in CI/CD pipeline
- Implemented performance baseline tests with Locust for API load profiling
- **Technologies:** pytest, httpx, pytest-asyncio, Newman, Locust, pytest-html

**Evidence:** [Test Suite](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects-new/p08-api-testing/tests)

**Key Test Coverage:**
- Authentication flows: register, login, token refresh, invalid credential handling
- Order lifecycle: create, retrieve, update, cancel, pagination, filtering
- Error handling: 400/401/403/404/500 response code validation
- Contract testing: JSON schema validation for all response payloads
- Performance: baseline latency SLOs enforced in CI

---

### Frontend Test Suite — Portfolio Web Application
*QA Engineering | Vitest, Playwright, React Testing Library | 2024*

- Wrote unit tests for React components covering rendering, props, and state behavior
- Built Playwright E2E tests covering critical user journeys (login, navigation, data display)
- Configured Vitest with coverage thresholds enforced per module
- Integrated test runs into GitHub Actions CI pipeline for automated quality gates
- **Technologies:** Vitest, Playwright, React Testing Library, GitHub Actions

**Evidence:** [Frontend Tests](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/frontend/src/__tests__)

**Test Scenarios Covered:**
- User authentication flow (registration, login, session persistence)
- Portfolio content rendering with mock API responses
- Photo gallery upload and calendar view interactions
- Cross-browser validation (Chromium, Firefox, WebKit)

---

### Infrastructure Validation — Terraform & AWS Modules
*Infrastructure QA | pytest, tfsec, GitHub Actions | 2024*

- Implemented validation tests for Terraform modules verifying resource configurations
- Integrated tfsec security scanning to catch misconfigurations before deployment
- Built smoke tests validating AWS RDS connectivity, security groups, and backup configs
- Enforced plan/validate/lint gate in GitHub Actions before any infrastructure merge
- **Technologies:** Terraform, tfsec, pytest, GitHub Actions, AWS CLI

**Evidence:** [Terraform Tests](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/01-sde-devops/PRJ-SDE-001)

---

### Observability & Alert Validation — Monitoring Stack
*QA for Infrastructure | PromQL, Alertmanager | 2024*

- Validated Prometheus alert rules by simulating failure conditions and verifying notification routing
- Tested Loki log ingestion with structured log samples to verify query accuracy
- Documented alert rule test cases with expected trigger conditions and resolution paths
- Verified Grafana dashboard queries against known metric baselines
- **Technologies:** Prometheus, Grafana, Loki, Alertmanager, Docker Compose

**Evidence:** [Monitoring Stack](https://github.com/samueljackson-collab/Portfolio-Project/tree/main/projects/01-sde-devops/PRJ-SDE-002/assets)

---

## Test Strategy Approach

### Testing Pyramid Applied

```
          /\
         /E2E\          Playwright (critical paths)
        /------\
       / Integr.\       httpx + pytest (API contracts)
      /----------\
     /   Unit     \     Vitest, pytest (component & logic)
    /--------------\
```

**My QA Philosophy:**
- Shift-left: Catch defects in unit/integration before reaching E2E
- Evidence-first: Every test suite produces HTML reports and coverage artifacts
- Automation-first: Manual tests are a last resort for exploratory edge cases
- Definition of done: Feature is not done until tests pass in CI

---

## Education

**Bachelor of Science in Information Systems**
Colorado State University | 2016 – 2024

**Relevant Coursework:** Software Testing & Quality Assurance, Database Management, Web Development, Network Security

---

## Certifications & Training

- **ISTQB Foundation Level** *(study in progress)*
- **AWS Certified Cloud Practitioner** *(planned — context for infrastructure testing)*
- **Python for Test Automation** *(self-study, pytest documentation and courses)*

---

## Key Achievements

- **Zero-defect releases:** Maintained 100% regression test pass rate across 3 client production deployments
- **80%+ coverage:** Enforced minimum coverage thresholds in CI for frontend and backend projects
- **Automated regression:** Replaced manual checklist with Playwright E2E suite, reducing release validation time by 70%
- **Infrastructure QA:** Validated Terraform modules across dev/staging/prod environments before deployment

---

## What I Bring to QA

- **Systems Context:** Understanding how infrastructure behaves under failure helps me write realistic test scenarios
- **Test-Driven Mindset:** Write tests before or alongside code, not as an afterthought
- **Automation Advocacy:** Every repeatable test becomes a candidate for automation
- **Clear Documentation:** Bug reports and test plans others can follow without explanation
- **Cross-Domain Coverage:** Comfortable testing APIs, frontends, databases, and infrastructure configs
