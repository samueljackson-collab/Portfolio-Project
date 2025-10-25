# Requirements Traceability

| Requirement | Implementation |
|-------------|----------------|
| Backend must expose `/health` | `projects/backend/app/routes/health.py` |
| Frontend must consume API | `projects/frontend/src/api/client.ts`, `projects/frontend/src/components/HealthStatus.tsx` |
| Automated testing | `projects/backend/tests`, `projects/frontend/src/__tests__` |
| Infrastructure as Code | `tools/terraform`, `tools/cloudformation`, `tools/k8s` |
| CI/CD enforcement | `.github/workflows/ci.yml` |
| Documentation | `docs/` directory |
