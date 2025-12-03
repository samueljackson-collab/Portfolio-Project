# Incident Playbook — P10

## Playbook: Primary Region Outage
1. **Detect:** CloudWatch/Route53 alarm `p10_primary_unhealthy` triggers.
2. **Contain:** Confirm user impact; pause deploys.
3. **Remediate:**
   - Run `make failover` to update Route 53 records to secondary.
   - Trigger Lambda cache warm via `aws lambda invoke ... warm-cache`.
4. **Verify:**
   - Health checks green in secondary; app smoke tests pass.
   - Monitor replica lag until <5s.
5. **Communicate:** Notify stakeholders; update status page.
6. **Post-Action:** File drill report and schedule failback when primary stable.
