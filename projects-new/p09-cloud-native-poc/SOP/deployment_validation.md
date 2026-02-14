# Deployment Validation & Rollback SOP — P09 Cloud-Native POC

This SOP captures day-2 operational steps for validating deployments of the P09 cloud-native proof of concept. It mirrors the operational depth of P07/P08/P10 packs by pairing pre/post-deploy checks with actionable rollback guidance.

## Roles & prerequisites
- **Deployment lead:** Coordinates change window, owns go/no-go calls.
- **SRE on duty:** Executes validation scripts, monitors health dashboards.
- **App owner:** Confirms functional checks, feature flag behaviors, and customer-facing impact.
- **Prerequisites:** Recent database snapshot available, feature flags manageable per environment, and access to CI/CD logs and Kubernetes dashboard.

## Pre-deployment checks
- Change record approved with scope, version, and rollback plan linked.
- Confirm **backup/restore point** is fresh (DB snapshot or storage versioned state) and note the ID.
- Review **error budget** and outstanding Sev-1/Sev-2 incidents; block deploy if budgets are exhausted.
- Verify **cluster capacity** (CPU/memory/PodDisruptionBudgets) and **ingress certificates** are not expiring within 30 days.
- Validate **image provenance**: artifact digest matches the release manifest; security scan results show no critical vulnerabilities.
- Run **smoke test suite** in staging on the release candidate; ensure synthetic checks are green for 30 minutes.
- Announce maintenance window to stakeholders and set Slack/Teams status alerts.

## Deployment window (high level)
1. Freeze feature flags that should remain off during rollout (document toggles).
2. Deploy via CI/CD pipeline (rolling update or canary) with **maxUnavailable ≤ 1** and **maxSurge ≥ 1** for stateless services.
3. Monitor rollout in real time:
   - `kubectl rollout status deployment/<service> --namespace <env>`
   - `kubectl get events --namespace <env> --sort-by=.metadata.creationTimestamp | tail`
4. Capture deployment logs and artifact versions in the change record.

## Post-deployment validation (functional & SLO)
- **Health & readiness**
  - Pods are Ready=1/1 and no CrashLoopBackOff events in the last 15 minutes.
  - Liveness/readiness probes are succeeding; 5xx/latency SLIs remain within target.
- **Traffic & API checks**
  - Run synthetic API probes (login, CRUD workflow, and a read-only query) against the live environment.
  - Validate edge routing: `kubectl get ingress` hosts match expected DNS and TLS certificates are valid.
- **Data integrity**
  - Verify no schema drift: compare migrations applied vs. release manifest.
  - Sample critical tables/collections for row counts or checksum deltas against pre-deploy snapshot thresholds.
- **Observability signals**
  - Dashboards show stable error rate (<1%), latency (p95 within SLO), and saturated resources < 70%.
  - Alerts remain quiet for 30 minutes post-cutover; silence windows removed after validation.
- **User-facing validation**
  - Confirm feature flags set to intended states; run UI spot-checks for high-value journeys.
- Record results in the change log with timestamps and links to Grafana/Kibana traces.

## Rollback decision criteria
- Error rate sustained > 2x baseline for 5 minutes.
- p95 latency above SLO for 3 consecutive measurement intervals.
- Deployment fails health checks or readiness never stabilizes within 10 minutes.
- Critical functional test fails (authentication, payment/transaction, or data write path).

## Rollback steps
1. Halt new deployments and pause auto-promotions in the pipeline.
2. Trigger **`kubectl rollout undo deployment/<service> --to-revision=<prev>`** for stateless services; confirm revision number from rollout history.
3. For stateful components, redeploy the last known-good manifest and, if schema changes were applied, run **down migrations** or restore the latest snapshot.
4. Revert feature flags to pre-deploy state; disable any newly exposed endpoints at the ingress layer if needed.
5. Validate rollback:
   - Pods stable at previous version; health checks passing.
   - Repeat synthetic API probes and confirm dashboards return to baseline within 15 minutes.
6. Update incident/channel with rollback outcome, attach logs, and schedule a **blameless postmortem** before next deploy attempt.

## Post-rollback clean-up
- Remove temporary silences or maintenance mode flags.
- Create follow-up ticket for root cause analysis and corrective actions.
- Archive deployment and rollback logs in the runbook folder for auditability.

## References
- P07/P08/P10 runbooks for baseline operational patterns (rolling, canary, and multi-region playbooks).
- `RUNBOOK.md` in the P09 repo for service-specific troubleshooting and command examples.
