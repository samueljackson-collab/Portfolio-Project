# DevOps Engineer - Data Operations Systems
## T-Mobile Interview Prep (Quick Start Package)

**Company:** T-Mobile
**Compensation:** $48-56/hr (~$100-117K/year equivalent)
**Location:** Redmond, WA (On-site)
**Experience Required:** 3+ years DevOps Engineering

---

## 🎯 Role Overview

Build cloud-native data operations systems using Python, Go, Kubernetes, Snowflake, and Azure. Heavy focus on GitLab CI/CD pipelines, secure identity management (EntraID), and integrating with data science teams to deploy ML models.

**Key Differentiator:** This is a **DevOps + Data Engineering hybrid**—you need both container orchestration expertise AND data platform knowledge.

---

## 🔥 Top 10 Topics to Master (Priority Order)

### 1. **Kubernetes CLI & Operations** (🔴 CRITICAL)
**What:** Managing deployments via kubectl, understanding pods/services/deployments/statefulsets
**Why:** "Manage deployments and operations via Kubernetes CLI" is explicit requirement
**Study:** `kubectl` commands, pod lifecycle, troubleshooting crashloops, resource management
**Lab:** Deploy a Python microservice to local Kubernetes cluster

### 2. **Python Microservices** (🔴 CRITICAL)
**What:** Building REST APIs with Flask/FastAPI, containerizing with Docker, async programming
**Why:** "Architect and implement scalable microservices in Python"
**Study:** FastAPI, async/await, error handling, logging, 12-factor app principles
**Lab:** Build a REST API that queries Snowflake and exposes metrics

### 3. **GitLab CI/CD Pipelines** (🔴 CRITICAL)
**What:** .gitlab-ci.yml syntax, stages, jobs, artifacts, container registry integration
**Why:** "Design and maintain GitLab CI/CD pipelines" is core responsibility
**Study:** Pipeline stages, Docker build/push, testing automation, GitOps workflows
**Lab:** Create CI/CD pipeline that builds Docker image, runs tests, deploys to K8s

### 4. **Go Microservices** (🟡 HIGH)
**What:** Go syntax, goroutines, HTTP servers, database connections, error handling
**Why:** "High-level proficiency in Python and Go" required
**Study:** Go basics, net/http package, context, defer/panic/recover, testing
**Lab:** Build a simple Go API that processes data from SQS queue

### 5. **Snowflake Integration** (🟡 HIGH)
**What:** Snowflake connector for Python, SQL optimization, data loading patterns
**Why:** Role involves data operations systems—Snowflake is the data warehouse
**Study:** Snowflake architecture, Snowpark (Python in Snowflake), connectors, security
**Lab:** Python script that loads data to Snowflake and queries it

### 6. **Azure Services** (🟡 HIGH)
**What:** Azure Kubernetes Service (AKS), Azure Storage, Azure Functions, EntraID
**Why:** Primary cloud platform for this role
**Study:** AKS basics, Azure CLI, resource groups, identity & access management
**Lab:** Deploy application to AKS with EntraID authentication

### 7. **Azure EntraID (formerly Azure AD)** (🟡 HIGH)
**What:** OAuth2/OIDC flows, service principals, managed identities, RBAC
**Why:** "Implement secure authentication and authorization using EntraID"
**Study:** App registrations, API permissions, token acquisition, RBAC roles
**Lab:** Secure your Python API with EntraID authentication

### 8. **Helm & Jinja Templating** (🟡 MEDIUM)
**What:** Helm charts, values.yaml, templating with {{ .Values.x }}, Jinja2 in Python
**Why:** "Experience with Helm and Jinja-based templating within YAML files"
**Study:** Helm install/upgrade, creating charts, template functions
**Lab:** Create a Helm chart for your Python microservice

### 9. **AWS Services (S3, Lambda, SQS)** (🟡 MEDIUM)
**What:** S3 SDK (boto3), Lambda functions, SQS queue operations
**Why:** "Integrate with AWS services (e.g., S3, Lambda, SQS)"
**Study:** boto3 library, event-driven architecture, serverless patterns
**Lab:** Lambda function triggered by S3 upload that writes to SQS

### 10. **Observability Stack** (🟡 MEDIUM)
**What:** Prometheus metrics (counters, gauges, histograms), Grafana dashboards, structured logging
**Why:** "Optimize system performance and reliability in production environments"
**Study:** Prometheus client libraries (Python/Go), PromQL queries, alert rules
**Lab:** Add Prometheus metrics to your Python API, visualize in Grafana

---

## 📚 Quick Reference Cheat Sheet

| Topic | Key Concepts | Interview Question Example |
|-------|-------------|---------------------------|
| **Kubernetes** | Pods, Services, Deployments, StatefulSets, ConfigMaps, Secrets | "How would you debug a CrashLoopBackOff pod?" |
| **Python** | FastAPI, async/await, type hints, Pydantic, pytest | "Design a REST API that handles 10K requests/sec. How do you ensure reliability?" |
| **GitLab CI/CD** | .gitlab-ci.yml, stages, artifacts, Docker registry, GitOps | "Walk me through a CI/CD pipeline for a microservice from code commit to production." |
| **Go** | Goroutines, channels, net/http, error handling, context | "Why would you choose Go over Python for a microservice? When wouldn't you?" |
| **Snowflake** | Virtual warehouses, tables, stages, Snowpark, connectors | "How would you optimize a slow-running Snowflake query?" |
| **Azure** | AKS, Storage, Functions, EntraID, RBAC | "Design secure access control for a microservice accessing Azure Storage." |
| **EntraID** | OAuth2, OIDC, service principals, managed identities | "Explain how a microservice authenticates to Azure services without storing secrets." |
| **Helm** | Charts, values.yaml, templates, releases | "How do you manage environment-specific configuration across dev/staging/prod using Helm?" |
| **AWS** | S3, Lambda, SQS, IAM, boto3 | "Design an event-driven data pipeline using S3, Lambda, and SQS." |
| **Observability** | Prometheus, Grafana, logging, tracing | "What metrics would you expose for a Python API? How would you alert on issues?" |

---

## 🧪 12 Essential Labs (2-Week Plan)

### Week 1: Foundations

**Lab 01: Local Kubernetes Setup (4 hours)**
- Install Docker Desktop or Minikube
- Deploy nginx, expose via Service, test with kubectl port-forward
- Create ConfigMap and Secret, mount in pod
- Debug a crashing pod (intentional error)
- **Evidence:** kubectl commands, pod YAML, screenshots

**Lab 02: Python FastAPI Microservice (6 hours)**
- Build REST API with FastAPI (GET /health, POST /data)
- Add Pydantic models for request/response validation
- Implement async endpoint that queries database
- Write pytest tests, achieve 80% coverage
- **Evidence:** Code, tests, Postman/curl screenshots

**Lab 03: Dockerize Python App (3 hours)**
- Write multi-stage Dockerfile for Python app
- Build image, run locally, verify functionality
- Optimize image size (<100MB)
- Push to Docker Hub or GitLab registry
- **Evidence:** Dockerfile, build logs, running container screenshot

**Lab 04: Deploy to Kubernetes (5 hours)**
- Write K8s manifests (Deployment, Service, Ingress)
- Deploy your Dockerized Python app to local K8s
- Configure liveness/readiness probes
- Test rolling update (change code, redeploy)
- **Evidence:** YAML files, kubectl get output, curl tests

**Lab 05: GitLab CI/CD Pipeline (6 hours)**
- Create .gitlab-ci.yml with stages: test, build, deploy
- Run pytest in CI
- Build Docker image, push to registry
- Deploy to K8s (use kubectl in CI job)
- **Evidence:** .gitlab-ci.yml, successful pipeline screenshot

### Week 2: Advanced

**Lab 06: Go Microservice Basics (5 hours)**
- Build simple Go HTTP server with /health endpoint
- Add middleware for logging and auth
- Connect to Postgres, implement CRUD operations
- Write Go tests
- **Evidence:** Go code, tests, running server screenshot

**Lab 07: Snowflake Integration (5 hours)**
- Sign up for Snowflake trial
- Create database, schema, table
- Python script to load CSV to Snowflake
- Query data, return results via API endpoint
- **Evidence:** Snowflake queries, Python code, API response

**Lab 08: Azure EntraID Authentication (6 hours)**
- Create Azure account (free tier)
- Register application in EntraID
- Secure Python API with EntraID (OAuth2)
- Test with Postman (acquire token, call API)
- **Evidence:** EntraID app registration, Python auth code, successful auth flow

**Lab 09: Helm Chart Creation (4 hours)**
- Create Helm chart for Python microservice
- Parameterize values (replicas, image tag, env vars)
- Install chart with different values for dev/prod
- Upgrade and rollback releases
- **Evidence:** Helm chart files, helm install output

**Lab 10: AWS S3 + Lambda Integration (4 hours)**
- Create S3 bucket, Lambda function (Python)
- Configure S3 event trigger (on file upload)
- Lambda processes file, writes to SQS or DynamoDB
- Test end-to-end flow
- **Evidence:** Lambda code, S3 event config, test execution logs

**Lab 11: Prometheus Metrics (4 hours)**
- Add Prometheus client library to Python API
- Expose /metrics endpoint with custom metrics (request count, latency, errors)
- Run Prometheus locally, scrape your API
- Create simple Grafana dashboard
- **Evidence:** Metrics code, Prometheus config, Grafana dashboard screenshot

**Lab 12: Complete GitOps Deployment (6 hours)**
- Combine Labs 1-11 into full stack
- GitLab CI/CD builds Docker image
- Updates Helm chart values
- Deploys to K8s automatically on git push
- Metrics visible in Grafana
- **Evidence:** End-to-end flow documentation, all components working

---

## 📅 2-Week Learning Path (Condensed)

### Week 1: DevOps Fundamentals
**Day 1-2:** Kubernetes basics + Lab 01
**Day 3:** Python FastAPI + Lab 02
**Day 4:** Docker + Lab 03
**Day 5:** K8s deployment + Lab 04
**Day 6:** GitLab CI/CD + Lab 05
**Day 7:** Review, document, catch up

### Week 2: Data Integration & Advanced Topics
**Day 8:** Go basics + Lab 06
**Day 9:** Snowflake integration + Lab 07
**Day 10:** Azure EntraID auth + Lab 08
**Day 11:** Helm charts + Lab 09
**Day 12:** AWS integration + Lab 10
**Day 13:** Observability + Lab 11
**Day 14:** GitOps capstone + Lab 12 + interview practice

---

## 🎤 Interview Warm-Up Questions

### Easy (2-3 min answers)
1. **What is Kubernetes and why would you use it?**
2. **Explain the difference between a Docker container and a Kubernetes pod.**
3. **What is GitOps?**
4. **What's the difference between a Deployment and a StatefulSet in Kubernetes?**
5. **How does OAuth2 work at a high level?**

### Medium (4-5 min answers)
6. **Design a CI/CD pipeline for a Python microservice. What stages would you include?**
7. **You have a pod that's stuck in CrashLoopBackOff. Walk me through your debugging process.**
8. **How would you implement authentication for a microservice using Azure EntraID?**
9. **Explain how you'd optimize a Snowflake query that's running slow.**
10. **What metrics would you expose from a Python API? How would you alert on issues?**

### Hard (6-8 min answers)
11. **Design a data pipeline that ingests files from S3, processes them, and loads to Snowflake. Include failure handling.**
12. **You're responsible for deploying a microservice to 3 environments (dev/staging/prod) with different configurations. How do you manage this with Helm?**
13. **A production pod is consuming 90% CPU. Walk me through investigating and resolving this.**
14. **Design a secure, scalable architecture for deploying ML models as microservices on Azure K8s.**
15. **Your GitLab CI/CD pipeline is taking 30 minutes to run. How would you optimize it?**

### Behavioral (STAR method)
16. **Tell me about a time you debugged a complex production issue. What was your approach?**
17. **Describe a time you improved the reliability of a system. What was the impact?**
18. **Tell me about a time you had to learn a new technology quickly for a project.**
19. **Describe a situation where you disagreed with a technical decision. How did you handle it?**
20. **Tell me about a time you mentored someone or shared knowledge with your team.**

---

## 🎥 Top Video Resources (Must-Watch)

### Kubernetes
1. **Kubernetes Tutorial for Beginners** - TechWorld with Nana (4 hours)
2. **Kubernetes Crash Course** - Freecodecamp (2 hours)
3. **kubectl Command Line Basics** - KodeKloud (30 min)

### Python
4. **FastAPI Tutorial** - Testdriven.io (series)
5. **Async Python for Beginners** - ArjanCodes (45 min)
6. **Building Microservices with Python** - Real Python (1 hour)

### GitLab CI/CD
7. **GitLab CI/CD Tutorial** - GitLab official (1 hour)
8. **GitOps Explained** - DevOps Toolkit (30 min)

### Go
9. **Go Tutorial for Beginners** - TechWorld with Nana (3 hours)
10. **Building HTTP Services in Go** - Gopher Academy (1 hour)

### Snowflake
11. **Snowflake Fundamentals** - Snowflake official (2 hours)
12. **Snowpark Python Tutorial** - Snowflake Summit (45 min)

### Azure
13. **Azure Kubernetes Service (AKS) Tutorial** - Adam the Automator (1 hour)
14. **Azure Active Directory (EntraID) for Developers** - Microsoft (1 hour)

---

## 📂 Your Relevant Portfolio Projects

Map your existing work to interview talking points:

| Your Project | Interview Question | Talking Point |
|--------------|-------------------|---------------|
| `projects/p18-k8s-cicd/` | "Tell me about your Kubernetes experience" | "I built a complete K8s CI/CD pipeline that..." |
| `projects/07-aiml-automation/` | "Experience with Python for data manipulation?" | "I automated data processing workflows using Python with..." |
| `projects/p09-cloud-native-poc/` | "Built cloud-native applications?" | "I designed a cloud-native application using microservices..." |
| `projects/06-homelab/PRJ-HOME-002/` | "Experience with containerization?" | "In my homelab, I run a Kubernetes cluster with..." |
| `projects/p12-data-pipeline/` | "Worked with data pipelines?" | "I built an end-to-end data pipeline that ingests..." |

---

## ✅ Pre-Interview Checklist

**Technical Prep:**
- [ ] Completed 8+ labs with documented evidence
- [ ] Can explain Kubernetes architecture from memory
- [ ] Can write a FastAPI endpoint from scratch in 10 minutes
- [ ] Can write a .gitlab-ci.yml file from memory
- [ ] Know Go basics (even if not expert)
- [ ] Understand Snowflake architecture and use cases
- [ ] Can explain OAuth2/OIDC flow clearly
- [ ] Know Prometheus metrics types and when to use each

**Portfolio Prep:**
- [ ] Portfolio cleanup (README files, screenshots, code comments)
- [ ] Mapped portfolio projects to role requirements
- [ ] Prepared to screen-share and walk through projects
- [ ] Have code examples ready (Python API, Dockerfile, CI/CD pipeline)

**Behavioral Prep:**
- [ ] Prepared 5-7 STAR method stories
- [ ] Practiced answering behavioral questions aloud
- [ ] Ready to discuss learning new tech quickly (Go, Snowflake, Helm)
- [ ] Can articulate "why T-Mobile" and "why this role"

**Logistics:**
- [ ] Resume updated with relevant keywords (Kubernetes, Python, Go, GitLab CI/CD, Snowflake)
- [ ] LinkedIn profile matches resume
- [ ] Questions prepared for interviewer (5-7 thoughtful questions)
- [ ] Interview environment set up (if virtual: quiet room, good lighting, backup device)

---

## 💪 You've Got This!

**Your Strengths for This Role:**
- ✅ Cloud architecture experience (projects p01, p09, p02)
- ✅ Python automation (projects 07, p12, p18)
- ✅ CI/CD experience (projects p18, 01-sde-devops)
- ✅ Data processing (projects p12, 16, 5, 7)
- ✅ Homelab shows initiative and passion (06-homelab)

**What You're Learning in 2 Weeks:**
- ⏳ Kubernetes hands-on (labs build this)
- ⏳ GitLab CI/CD specifics (labs build this)
- ⏳ Go basics (quick to learn with Python background)
- ⏳ Snowflake platform (focused study)
- ⏳ Azure specifics (transferable from AWS knowledge)

**Remember:** You don't need to be an expert in everything. Show you can learn quickly, solve problems systematically, and communicate clearly.

---

**Next Steps:**
1. **Today:** Read this README fully, watch Kubernetes tutorial (1 hour), start Lab 01
2. **This Week:** Complete Labs 01-05, study cheat sheet, watch key videos
3. **Next Week:** Complete Labs 06-12, practice interview questions, polish portfolio
4. **Before Interview:** Full mock interview, review checklist, get good sleep

**Good luck! 🚀**

---

**Last Updated:** 2025-11-10
**Status:** Starter package ready - begin immediately!
