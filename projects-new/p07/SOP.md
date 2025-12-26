# Standard Operating Procedures (MLOps)

## SOP-01: Onboarding a New ML Project to Kubeflow/MLflow/Feast

### Purpose & Scope
Establish a new machine learning project with end-to-end infrastructure for training, tracking, feature management, and serving.

### Roles
- **Requestor:** Data scientist or ML engineer proposing new project
- **Reviewer:** ML platform engineer
- **Approver:** ML platform lead and security officer

### Preconditions
- [ ] Project proposal approved with business case
- [ ] Data sources identified and access granted
- [ ] Compute/storage budget allocated
- [ ] Namespace and resource quotas defined

### Procedure

#### Step 1: Create Namespace and RBAC
```bash
kubectl create namespace ml-<project-name>
kubectl create serviceaccount <project-name>-sa -n ml-<project-name>
kubectl apply -f rbac/<project-name>-rolebinding.yaml
```

#### Step 2: Provision MLflow Experiment
- Log into MLflow UI
- Create new experiment: `<project-name>-experiment`
- Set experiment tags: `team=<team>`, `env=dev`, `cost-center=<cc>`
- Document experiment ID in project README

#### Step 3: Define Features in Feast
```bash
cd feast/feature_repo
mkdir features/<project-name>
# Create feature definitions (Python files with FeatureView)
feast apply
feast materialize-incremental $(date -u +%Y-%m-%dT%H:%M:%S)
```

#### Step 4: Create Kubeflow Pipeline Template
- Copy pipeline template from `templates/training_pipeline_template.py`
- Customize components for project-specific data/model
- Add to project repo under `pipelines/<project-name>/`

#### Step 5: Configure CI/CD
- Add GitHub Actions workflow for pipeline linting and testing
- Set up image build and push to registry
- Configure secrets for MLflow, Feast, cloud storage

#### Step 6: Run Initial Training
- Submit pipeline with sample data
- Verify components execute successfully
- Check MLflow for logged metrics and artifacts

#### Step 7: Documentation & Handoff
- Update project README with setup instructions
- Add to ML platform inventory spreadsheet
- Schedule onboarding session with data science team

### Records
- Namespace creation ticket
- Experiment ID and feature view names
- CI/CD workflow links
- Training run logs

### Review Cadence
- Review onboarding process quarterly for improvements
- Audit project inventory monthly for inactive projects

---

## SOP-02: Model Approval and Promotion Workflow

### Purpose & Scope
Ensure models meet quality, security, and compliance standards before production deployment.

### Roles
- **Submitter:** Data scientist or ML engineer
- **Reviewer:** ML platform engineer and senior data scientist
- **Approver:** ML lead and compliance officer

### Preconditions
- [ ] Model registered in MLflow with "None" or "Staging" stage
- [ ] Evaluation metrics meet baseline thresholds
- [ ] Model card and documentation completed

### Procedure

#### Step 1: Submit Promotion Request
- Create promotion ticket (Jira/Linear) with template:
  - Model name and version
  - Training dataset version
  - Metrics comparison vs baseline
  - Risk assessment
  - Rollback plan
- Link to MLflow experiment and model registry entry

#### Step 2: Technical Review
- [ ] Verify evaluation metrics (accuracy, fairness, robustness)
- [ ] Check training/serving parity tests passed
- [ ] Review model card for completeness
- [ ] Validate data lineage and feature provenance
- [ ] Scan model artifact for security issues (pickle exploits, embedded secrets)

#### Step 3: Compliance Review
- [ ] Confirm no PII in model or training data (or proper anonymization)
- [ ] Verify bias/fairness analysis completed
- [ ] Check regulatory requirements met (GDPR, CCPA, etc.)
- [ ] Ensure audit trail complete (git commit, approvers, dataset version)

#### Step 4: Approval Decision
- **If approved:**
  - Transition model in MLflow: `Staging` → `Production`
  - Add approval metadata tags (approver name, date, ticket link)
  - Notify submitter and platform team
- **If rejected:**
  - Document reasons in ticket
  - Request additional work from submitter
  - Optionally transition to `Archived` if permanently rejected

#### Step 5: Deployment
- Follow deployment playbook (PLAYBOOK.md)
- Execute canary rollout
- Monitor for 24-48 hours
- Update inventory and changelog

### Records
- Promotion ticket with approval trail
- MLflow registry history (stage transitions)
- Model card and documentation versions
- Deployment logs and metrics

### Review Cadence
- Review approval process monthly
- Audit model registry quarterly for orphaned models

---

## SOP-03: Periodic Retraining and Drift Review

### Purpose & Scope
Maintain model freshness and performance through automated retraining triggered by schedule or drift detection.

### Roles
- **System:** Automated scheduler (cron/Argo Events)
- **Reviewer:** ML engineer on-call
- **Approver:** ML lead (for major model changes)

### Preconditions
- [ ] Drift detection thresholds configured
- [ ] Retraining pipeline tested and validated
- [ ] Monitoring dashboards operational

### Procedure

#### Step 1: Drift Detection (Automated)
- Drift detector runs daily (configurable frequency)
- Compares recent prediction data vs reference distribution
- Calculates drift scores (KS test, PSI, KL divergence)
- Logs results to monitoring system

#### Step 2: Trigger Decision (Automated)
- **If drift score > threshold OR scheduled retrain date:**
  - Create retraining job ticket
  - Trigger Kubeflow pipeline with latest data
  - Notify ML team in Slack
- **Else:**
  - Log "no drift detected" and continue monitoring

#### Step 3: Retraining Execution (Automated)
- Pipeline runs with fresh data from past N days
- Model trained with same hyperparameters (or optionally tuned)
- Evaluation compares new model vs current production model
- Results logged to MLflow

#### Step 4: Human Review (Manual)
- ML engineer reviews retraining results:
  - [ ] Metrics improved or within acceptable degradation
  - [ ] No data quality issues detected
  - [ ] Feature distributions reasonable
  - [ ] Model complexity/size acceptable
- **Decision:**
  - **Auto-promote:** If metrics significantly better and low risk
  - **Manual approval:** If marginal improvement or new features added
  - **Reject:** If metrics worse or data issues found

#### Step 5: Promotion (Automated or Manual)
- Follow model promotion SOP (SOP-02)
- Deploy via playbook with canary testing
- Update drift reference dataset with recent data

### Records
- Drift detection logs and scores
- Retraining pipeline run IDs
- Review decisions and approval trail
- Deployment outcomes

### Review Cadence
- Review drift thresholds monthly based on false positive rate
- Audit retraining frequency quarterly for cost/benefit

---

## SOP-04: Secret and Credential Rotation for ML Services

### Purpose & Scope
Regularly rotate secrets (API keys, DB passwords, cloud credentials) used by ML platform components to reduce security risk.

### Roles
- **Executor:** Platform engineer or SRE
- **Reviewer:** Security engineer
- **Approver:** Security lead

### Preconditions
- [ ] Secret inventory documented (secret name, location, owning service)
- [ ] Rotation procedure tested in staging
- [ ] Downtime window approved (if required)

### Procedure

#### Step 1: Generate New Secret
- For AWS credentials: Create new IAM user or rotate access keys
- For DB passwords: Use cloud provider secret manager to generate
- For API tokens: Generate new token in provider UI
- **Important:** Do not delete old secret yet (rollback safety)

#### Step 2: Update Secret in Kubernetes
```bash
# Example: Rotate MLflow S3 credentials
kubectl create secret generic mlflow-secrets-new \
  --from-literal=AWS_ACCESS_KEY_ID=<new-key> \
  --from-literal=AWS_SECRET_ACCESS_KEY=<new-secret> \
  -n mlops --dry-run=client -o yaml | kubectl apply -f -

# Update deployment to use new secret
kubectl set env deployment/mlflow-server --from=secret/mlflow-secrets-new -n mlops
```

#### Step 3: Verify Service Health
- [ ] Check pods restarted successfully
- [ ] Verify connectivity to S3/DB/external service
- [ ] Run smoke test (e.g., MLflow tracking write/read)
- [ ] Monitor logs for auth errors

#### Step 4: Decommission Old Secret
- Wait 24-48 hours to ensure stability
- Delete old IAM user/key or revoke API token
- Remove old Kubernetes secret:
  ```bash
  kubectl delete secret mlflow-secrets-old -n mlops
  ```

#### Step 5: Update Documentation
- [ ] Update secret inventory with rotation date
- [ ] Log rotation in audit trail (compliance requirement)
- [ ] Update runbooks if secret path changed

### Records
- Secret rotation ticket with timestamps
- Service health checks and logs
- Audit trail entry

### Review Cadence
- Rotate secrets every 90 days (cloud credentials)
- Rotate DB passwords every 180 days
- Rotate API tokens on provider recommendation or breach

---

## SOP Appendix: Template Fields
Each SOP should include:
- **ID:** SOP-XX
- **Title:** Descriptive name
- **Purpose & Scope:** What and why
- **Roles:** Who performs, reviews, approves
- **Preconditions:** What must be true before starting
- **Procedure:** Step-by-step instructions with commands/examples
- **Records:** What to document
- **Review Cadence:** How often to update SOP
- **Revision History:** Date, author, changes
