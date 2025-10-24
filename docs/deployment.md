# Deployment Guide

This guide covers environment preparation, infrastructure provisioning, application deployment, rollback, and monitoring for the portfolio monorepo.

## Environments
- **Development**: Single-AZ, cost-efficient configuration.
- **Staging**: Mirrors production topology with Multi-AZ RDS and ASG scaling.
- **Production**: Hardened configuration with blue/green deployment workflow.

## Infrastructure Provisioning
1. Navigate to desired environment directory (e.g., `infra/environments/staging`).
2. Configure AWS credentials via environment variables or profiles.
3. Initialize Terraform:
   ```bash
   terraform init
   ```
4. Review plan:
   ```bash
   terraform plan -out plan.tfplan
   ```
5. Apply changes:
   ```bash
   terraform apply plan.tfplan
   ```

### Remote State
Each environment uses an S3 backend with DynamoDB locking defined in `backend.tf`. Ensure S3 bucket and DynamoDB table exist prior to first run.

## Application Deployment
### Backend
- Build Docker image: `docker build -t portfolio-backend ./backend`.
- Push to registry: `docker tag` and `docker push` to container registry (GHCR/AWS ECR).
- Update ECS/Kubernetes (future) or redeploy EC2 instances via Terraform `taint` and `apply`.
- Run Alembic migrations: `alembic upgrade head` with environment variables set.

### Frontend
- Build static assets: `npm run build`.
- Sync artifacts to S3 bucket defined in `storage` module using `aws s3 sync dist/ s3://bucket-name`.
- Invalidate CloudFront distribution to refresh caches.

### Monitoring
- Deploy metrics exporter container alongside backend or as standalone service.
- Update Prometheus scrape config if endpoint changes.
- Import/Update Grafana dashboard JSON.

## CI/CD Release Workflow
1. Create release branch and merge into `main` once validated.
2. Tag release `vX.Y.Z` and push to GitHub.
3. `release.yml` workflow builds/test images, deploys to staging, and pauses for approval.
4. After manual approval, workflow applies production Terraform and executes blue/green checks.
5. Monitor Grafana and CloudWatch for anomalies for at least 30 minutes post-deploy.

## Rollback Procedures
- **Infrastructure**: Run `terraform apply` with previous state file or use `terraform destroy` for specific resources if necessary.
- **Backend**: Redeploy previous container image tag via Terraform variable override or manual update.
- **Database**: Restore from automated snapshots defined in `storage` module; run point-in-time recovery if needed.
- **Frontend**: Re-sync previous build artifacts from artifact storage.

## Disaster Recovery
- Daily automated snapshots for RDS with 7-day retention.
- S3 versioning enabled for static asset bucket.
- Cross-region replication optional for production configuration.
- Document recovery steps and validate quarterly using tabletop exercises.

## Monitoring and Alerts
- Prometheus alerts on high error rate (>1%), elevated latency (p95 > 500ms), and low active users.
- Grafana dashboards provide visibility into request rate, latency, errors, and infrastructure metrics.
- Future work includes integrating Alertmanager with Slack/PagerDuty.

## Security Considerations
- Store secrets in AWS SSM Parameter Store or Secrets Manager; never commit `.env` files.
- Enforce TLS for all external endpoints; rotate certificates regularly.
- Use AWS IAM roles with least privilege for compute resources.
- Run scheduled security scans via `security.yml` workflow.

## Post-Deployment Checklist
- [ ] Terraform state committed and locked released.
- [ ] Grafana dashboards updated with new metrics.
- [ ] Status board refreshed using `python tools/update_status.py`.
- [ ] Changelog entries added and release tagged.
