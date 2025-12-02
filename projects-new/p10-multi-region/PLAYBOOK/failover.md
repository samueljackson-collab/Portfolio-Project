# Playbook: Initiate Controlled Failover

1. **Notify** stakeholders and freeze writes on primary.
2. **Trigger** failover by setting health check to fail via `jobs/toggle_primary.sh down`.
3. **Validate** secondary receives traffic; monitor `consumer/validate.py` metrics.
4. **Promote** secondary DB (simulated) and enable writes.
5. **Document** results in `REPORT_TEMPLATES/failover_report.md`.
