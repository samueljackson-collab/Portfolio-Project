# Orchestration Runbook

## Scope
- Terraform environments: `infrastructure/terraform/environments/{staging,production}`
- Ansible inventories and roles: `infrastructure/ansible`
- API surface: `backend/app/routers/orchestration.py`
- Frontend console: `frontend/src/pages/OrchestrationConsole.tsx`
- Observability: `observability/otel-collector.yaml`, `observability/grafana-dashboard.json`

## Deploy steps
1. **Plan infrastructure**
   - `cd infrastructure/terraform/environments/staging`
   - `terraform init -backend=false`
   - `terraform plan -var db_password=$STAGING_DB_PASSWORD`
2. **Apply and release**
   - `terraform apply -auto-approve`
   - Confirm ALB DNS from outputs and update DNS if needed.
3. **Configure servers**
   - `ansible-playbook -i infrastructure/ansible/inventory/hosts.yml infrastructure/ansible/playbooks/site.yml -e target=staging`
4. **Promote**
   - Re-run steps in `production` directory with production secrets.
   - Trigger API dry-run: `curl -X POST /orchestration/deploy -d '{"environment":"production","artifact_version":"latest","dry_run":true}'`

## Observability
- Collector pipeline: `observability/otel-collector.yaml`
- Prometheus scrape target for Grafana: `otel-collector:8889`
- Dashboard JSON: `observability/grafana-dashboard.json`
- K8s service endpoints exposed in `deployments/k8s/platform.yaml`

## Rollback
- `terraform apply` with previous state file to revert infra.
- `ansible-playbook ... --tags rollback` (future tag) to redeploy prior compose images.
- For console/API regression, roll back `artifact_version` via `/orchestration/deploy` with the last known good tag.
