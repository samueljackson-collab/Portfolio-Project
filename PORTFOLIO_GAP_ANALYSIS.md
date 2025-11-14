# Portfolio Gap Analysis

This document highlights outstanding operational and documentation gaps for the monitoring and deployment tooling introduced in the latest iteration.

## Observability Enhancements

### Prometheus Configuration Hygiene

> Requires [`yq`](https://mikefarah.gitbook.io/yq/) to be installed locally.

Instead of appending scrape jobs with `cat >> config/prometheus.yml`, use an idempotent update to avoid duplicate jobs:

```bash
cd projects/p04-ops-monitoring
if ! yq '.scrape_configs[] | select(.job_name == "backend-api")' config/prometheus.yml >/dev/null; then
  yq -i '.scrape_configs += [{"job_name":"backend-api","scrape_interval":"10s","metrics_path":"/metrics","static_configs":[{"targets":["host.docker.internal:8000"],"labels":{"service":"backend","environment":"dev"}}]}]' config/prometheus.yml
fi
make reload-prometheus
```

This command safely appends the job only if it does not exist and immediately reloads Prometheus using the dedicated Makefile target.

### Service Startup Guidance

Start each service in its own terminal window to keep logs visible and make shutdown straightforward:

1. **Monitoring stack** – `cd projects/p04-ops-monitoring && make run`
2. **Backend API** – `cd backend && uvicorn app.main:app --reload`
3. **Frontend** – `cd frontend && npm run dev -- --host`

Avoid backgrounding processes with `&`; long-running services are easier to manage with explicit terminals.

## Cloud Access

### AWS Credentials

Exporting raw credentials leaves them in shell history. Configure an AWS CLI profile instead:

```bash
aws configure --profile portfolio-dev
export AWS_PROFILE=portfolio-dev
export AWS_REGION=us-east-1
```

Use the profile when running Terraform or deployment scripts so keys remain encrypted in the AWS CLI config files.

## Next Steps

- [ ] Document how to rotate the Alertmanager webhook URLs when moving beyond local testing.
- [ ] Add Prometheus metrics to the frontend before enabling its scrape job (currently commented out in `config/prometheus.yml`).
- [ ] Continue replacing ad-hoc shell exports with `.env` files or credential helpers across remaining docs.
