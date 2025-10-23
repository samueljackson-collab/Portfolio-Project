# P09 · Full-Stack Cloud Application — Product & Engineering Handbook

## 1. Executive Overview
- Customer portal delivering analytics, billing insights, and support tools.  
- Multi-tenant SaaS with RBAC and audit logging.  
- Target uptime 99.9%, p95 latency < 200 ms.  

## 2. Architecture
- **Frontend:** React + TypeScript (Vite), component library (Chakra UI), state management via React Query.  
- **Backend:** FastAPI with async SQLAlchemy, Redis cache, Celery worker for async jobs.  
- **Data:** PostgreSQL (RDS) with migration history (Alembic), S3 for document uploads.  
- **Deployment:** GitHub Actions → ECR/ECS Fargate; infrastructure defined via Terraform modules (reusing P01 network/storage).  
- **Observability:** OpenTelemetry instrumentation, Grafana dashboards, Loki log aggregation, Sentry for error tracking.  

## 3. Domain Model
- **Tenant** ↔ **User** (many-to-many).  
- **UsageMetric** aggregated hourly, accessible via analytics API.  
- **Invoice** generated monthly, integrates with Stripe (webhooks).  

## 4. API Design
- RESTful endpoints under `/api/v1`.  
- OAuth2 password + JWT access/refresh tokens.  
- Rate limiting via API Gateway usage plans.  
- OpenAPI schema published via CI to docs site.  

## 5. Frontend UX
- Dashboard with usage graphs, invoice list, support ticket widget.  
- Responsive grid layout supporting desktop/tablet/mobile.  
- Light/dark theme toggle persisted per user.  

## 6. Security
- Enforce MFA, device trust, and session expiration.  
- Secrets stored in AWS Secrets Manager; CI uses OIDC to assume deployment role.  
- Static code analysis: `bandit`, `mypy`, `eslint`, `depcheck`.  

## 7. Testing Strategy
- **Backend:** pytest with fixtures, coverage > 85%.  
- **Frontend:** React Testing Library, snapshot tests.  
- **API Contracts:** Schemathesis for fuzzing.  
- **E2E:** Playwright flows executed nightly.  

## 8. Deployment Workflow
1. Feature branch merged → GitHub Actions pipeline executes lint/test/build.  
2. Docker images tagged with git SHA, pushed to ECR.  
3. Terraform plan posted for infrastructure changes; manual approval required.  
4. ECS deploy triggered via blue/green (CodeDeploy).  
5. Post-deploy smoke tests run using k6/Playwright.  

## 9. Cost Management
- Use Savings Plans for Fargate, Aurora Serverless v2 for PostgreSQL.  
- Budget alerts for monthly spend > $450.  
- CloudFront caching reduces egress costs by 25%.  

## 10. Roadmap
- Add GraphQL gateway for partner integrations.  
- Build customer usage anomaly detection service.  
- Launch public status page with historical uptime data.  

