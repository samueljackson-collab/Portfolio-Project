# Playbook Phase 8 — Decommission

**Version**: 2.1 | **Owner**: IT Operations / Asset Management | **Last Updated**: 2026-01-10

---

## 1. Purpose

Defines the process for safely retiring IT services, ensuring data is preserved or destroyed
per policy, dependencies are updated, and assets are reclaimed.

---

## 2. Decommission Triggers

- Service end-of-life (vendor announcement or internal decision)
- Replacement service fully operational and validated
- Usage below threshold (< 5 active users / < 1% of traffic) for 90 days
- Cost-benefit analysis negative (cost exceeds business value)
- Compliance requirement (data retention period expired)

---

## 3. Pre-Decommission Checklist

### 3.1 Discovery and Impact

- [ ] Identify all consumers of the service (API clients, integrations, users)
- [ ] Map all upstream and downstream dependencies (CMDB check)
- [ ] Confirm replacement service is operational and consumers migrated
- [ ] Notify all stakeholders minimum 30 days before decommission date
- [ ] Update documentation index to reflect planned removal

### 3.2 Data Handling

| Data Type | Action | Retention Period | Verification |
|-----------|--------|-----------------|-------------|
| Customer PII | Archive encrypted + delete from service | Per data policy | DPO sign-off |
| Business data | Archive to cold storage | 7 years | Manager sign-off |
| Logs | Archive to SIEM / cold storage | 1 year | Compliance sign-off |
| Backups | Retain for retention period then delete | Per backup policy | IT sign-off |
| Secrets / keys | Rotate downstream, then revoke | Immediate | SecOps sign-off |

---

## 4. Decommission Execution Steps

```bash
# 1. Final backup before decommission
pg_dump -h DB_HOST -U DB_USER -d DB_NAME -F c \
  -f /archives/$(date +%Y%m%d)-SERVICENAME-final-backup.dump

# 2. Remove from load balancer / service mesh
kubectl delete ingress SERVICE-ingress --namespace=NAMESPACE

# 3. Scale deployment to zero (soft decommission — 7-day hold)
kubectl scale deployment/SERVICE --replicas=0 --namespace=NAMESPACE

# 4. Remove DNS record
# Update Route53 / internal DNS

# 5. After 7-day hold — delete resources
kubectl delete deployment/SERVICE --namespace=NAMESPACE
kubectl delete service/SERVICE --namespace=NAMESPACE
kubectl delete configmap/SERVICE-config --namespace=NAMESPACE

# 6. Decommission cloud resources
terraform destroy -target=module.SERVICE_NAME

# 7. Revoke service account / API keys
# Revoke in secrets manager, rotate downstream

# 8. Archive repository (GitHub: Settings → Archive repository)
```

---

## 5. Post-Decommission Checklist

- [ ] Service removed from monitoring and alerting
- [ ] Dashboards updated or archived
- [ ] DNS records removed
- [ ] SSL certificates revoked
- [ ] Service account and API keys revoked
- [ ] CMDB updated — service status set to "Decommissioned"
- [ ] Documentation updated (mark as retired in service catalogue)
- [ ] Final backup confirmed stored in cold archive
- [ ] Cost center updated — resources deallocated
- [ ] Stakeholder communication sent confirming decommission complete

---

## 6. Decommission Record Template

```yaml
service_name: "example-service"
decommission_date: "2026-03-01"
reason: "Replaced by new-service v2.0"
decommissioned_by: "IT Operations"
approved_by: "IT Director"

data_disposition:
  customer_pii: "Deleted per policy — DPO sign-off: 2026-02-28"
  business_data: "Archived to S3 Glacier — ref: archive-2026-0301"
  logs: "Archived to SIEM — retained until 2027-03-01"

infrastructure_removed:
  - "ECS service: example-service-prod"
  - "RDS instance: example-service-db (final snapshot retained)"
  - "CloudFront distribution: E1EXAMPLE"

accounts_revoked:
  - "IAM role: example-service-role"
  - "API key: rotated in Secrets Manager"

final_backup: "s3://archives/20260301-example-service-final.dump"
cmdb_updated: true
```
