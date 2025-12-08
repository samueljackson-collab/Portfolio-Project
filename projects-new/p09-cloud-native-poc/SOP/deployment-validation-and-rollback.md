# Cloud-Native PoC Deployment Validation & Rollback SOP

## Purpose
Ensure each deployment of the cloud-native PoC is validated quickly with clear rollback guidance to minimize downtime.

## Preconditions
- CI pipeline green (linting, unit/integration tests).
- Target namespace reachable and service account authorized for deployments and rollouts.
- Current release artifact tagged and stored in the registry.

## Validation Steps
1. **Prepare context**
   - Confirm target environment: `kubectl config current-context`.
   - Export variables:
     ```bash
     export APP_NAMESPACE=poc-cloud-native
     export APP_NAME=portfolio-web
     ```
2. **Deploy candidate**
   - Apply manifests: `kubectl apply -f deploy/manifests/ -n "$APP_NAMESPACE"`.
3. **Check rollout health**
   - Watch rollout: `kubectl rollout status deploy/$APP_NAME -n "$APP_NAMESPACE" --timeout=3m`.
   - Confirm pods ready: `kubectl get pods -n "$APP_NAMESPACE" -l app=$APP_NAME`.
   - Verify service endpoints: `kubectl get endpoints $APP_NAME -n "$APP_NAMESPACE"`.
4. **Smoke test**
   - Port-forward and probe: `kubectl port-forward svc/$APP_NAME 8080:80 -n "$APP_NAMESPACE" &`
   - Run health check: `curl -f http://127.0.0.1:8080/healthz`.
   - Run key user journey: `curl -f http://127.0.0.1:8080/api/version`.
5. **Observability gates**
   - Confirm no new critical alerts in the last 10 minutes.
   - Check latency/error-rate dashboards to ensure golden signals remain within SLO.
6. **Post-deploy validation**
   - Annotate deployment with build ID and validation status.
   - Log results in the release checklist.

## Rollback Steps
1. **Initiate rollback**
   - Command: `kubectl rollout undo deploy/$APP_NAME -n "$APP_NAMESPACE" --to-revision=<previous>`.
2. **Verify rollback completion**
   - `kubectl rollout status deploy/$APP_NAME -n "$APP_NAMESPACE" --timeout=2m`.
   - Ensure pods match previous image tag.
3. **Traffic validation**
   - Re-run the smoke tests above.
   - Confirm alerts clear; acknowledge any still firing.
4. **Record outcome**
   - Update incident notes with the reason for rollback and metrics observed.
   - Open follow-up ticket for root-cause analysis and test coverage gaps.

## Escalation Matrix
- **Primary:** Cloud platform engineer on-call (PagerDuty: `cloud-native-poc-primary`).
- **Secondary:** SRE lead (`sre-lead@portfolio.internal`).
- **Tertiary:** Engineering manager for cloud-native initiatives.

## Success Criteria
- Rollout reaches `Available` within the timeout.
- Health check and API version endpoints return HTTP 200.
- No increase in error rate or latency beyond SLO thresholds after deployment or rollback.
