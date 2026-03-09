# PBS Restore Checklist (Sanitized Example)

1. **Select snapshot** from `demo-datastore` for the affected VM/container.
2. **Restore target**
   - Option A: Restore in-place with `start-after-restore: true`.
   - Option B: Restore to staging VM ID with isolated network to validate first boot.
3. **Validate services**
   - Prometheus: `curl http://localhost:9090/-/ready`
   - Grafana: `curl http://localhost:3000/api/health`
   - Loki: `curl http://localhost:3100/ready`
4. **Re-register exporters** if IP/hostname changed (use DNS CNAMEs to avoid rewiring dashboards).
5. **Run smoke tests**
   - Alert test fire via `amtool` using `alertmanager.yml` template values.
   - Query dashboards to confirm recording rules repopulate without errors.
6. **Document outcome** in the incident log with duration, blockers, and any manual fixes required.

> All endpoints and IDs are placeholders for demonstration purposes only.
