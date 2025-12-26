# Runbook — Project 4 (DevSecOps Pipeline)

## Overview

Production operations runbook for Project 4 DevSecOps Pipeline. This runbook covers security-first CI/CD operations including SBOM generation, vulnerability scanning, container image security, policy enforcement, incident response, and security compliance management.

**System Components:**
- GitHub Actions for CI/CD orchestration
- Trivy for container vulnerability scanning
- Syft for SBOM (Software Bill of Materials) generation
- OPA (Open Policy Agent) for policy enforcement
- Cosign for image signing and verification
- Container registry with security scanning (ECR, GCR, Harbor)
- Kubernetes admission controllers for runtime policy
- Security monitoring and alerting

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Security scan completion rate** | 99% | Successful vulnerability scans per build |
| **Critical vulnerability detection time** | < 5 minutes | Time from build → security alert |
| **Policy violation detection rate** | 100% | All policy violations caught pre-deployment |
| **SBOM generation success rate** | 99% | SBOM created for all deployments |
| **Image signing success rate** | 100% | All production images signed |
| **Security scan time** | < 5 minutes | Time for complete security scan |
| **False positive rate** | < 5% | Incorrectly flagged vulnerabilities |

---

## Dashboards & Alerts

### Dashboards

#### Security Overview Dashboard
```bash
# Check recent security scans
cd /home/user/Portfolio-Project/projects/4-devsecops
cat reports/security-scan-latest.json | jq '.Results[].Vulnerabilities | group_by(.Severity) | map({Severity: .[0].Severity, Count: length})'

# Check SBOM status
ls -lh sbom/*.json

# Check signed images
cosign verify --key cosign.pub <image-url>

# Check policy violations
opa test policies/ --verbose
```

#### Vulnerability Dashboard
- Total vulnerabilities by severity (Critical, High, Medium, Low)
- Trends over time
- Time to remediation
- Top vulnerable packages
- CVE details and patches available

#### Compliance Dashboard
- Policy compliance score
- SBOM coverage
- Image signing coverage
- Security gate pass/fail rate
- Audit trail

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Critical CVE in production image | Immediate | Emergency patch or rollback |
| **P0** | Unsigned image deployed to production | Immediate | Block deployment, investigate |
| **P0** | Policy violation in production | Immediate | Enforce policy, remediate |
| **P1** | High severity vulnerabilities (CVSS >7) | 4 hours | Patch and redeploy |
| **P1** | Security scan failed | 1 hour | Fix scan, unblock pipeline |
| **P2** | Medium severity vulnerabilities | 24 hours | Schedule patch |
| **P2** | SBOM generation failed | 2 hours | Fix SBOM generation |
| **P3** | Low severity vulnerabilities | 7 days | Review and patch |

---

## Standard Operations

### Live Deployment Publication (Manual)
```bash
# Create a deployment evidence folder
DEPLOY_DATE=$(date +%Y-%m-%d)
mkdir -p deployments/${DEPLOY_DATE}

# Trigger pipeline and capture logs
gh workflow run security-pipeline.yml
gh run watch --workflow security-pipeline.yml | tee deployments/${DEPLOY_DATE}/pipeline-run.log

# Capture security scan and SBOM summaries
cp reports/security-scan-latest.json deployments/${DEPLOY_DATE}/security-scan-summary.json
cp sbom/myapp-latest.json deployments/${DEPLOY_DATE}/sbom-summary.json

# Update the deployment record
sed -i.bak "s/Deployment date: .* (planned)/Deployment date: ${DEPLOY_DATE} (live)/" DEPLOYMENT_STATUS.md
```

### Security Scanning Operations

#### Run Vulnerability Scan
```bash
# Navigate to project directory
cd /home/user/Portfolio-Project/projects/4-devsecops

# Scan container image
trivy image --severity CRITICAL,HIGH myapp:latest

# Scan with full report
trivy image --format json --output reports/trivy-scan-$(date +%Y%m%d).json myapp:latest

# Scan filesystem for vulnerabilities
trivy fs --security-checks vuln,config .

# Scan for secrets
trivy fs --security-checks secret .

# Scan Kubernetes manifests
trivy config manifests/
```

#### Generate SBOM
```bash
# Generate SBOM with Syft
syft myapp:latest -o json > sbom/myapp-$(date +%Y%m%d).json

# Generate SBOM in multiple formats
syft myapp:latest -o spdx-json > sbom/myapp-spdx.json
syft myapp:latest -o cyclonedx-json > sbom/myapp-cyclonedx.json

# Generate SBOM for filesystem
syft dir:. -o json > sbom/source-code-$(date +%Y%m%d).json

# Verify SBOM
cat sbom/myapp-$(date +%Y%m%d).json | jq '.artifacts | length'
cat sbom/myapp-$(date +%Y%m%d).json | jq '.artifacts[].name' | sort
```

#### Sign Container Images
```bash
# Generate signing key (one-time setup)
cosign generate-key-pair

# Sign image
cosign sign --key cosign.key myapp:latest

# Verify signed image
cosign verify --key cosign.pub myapp:latest

# Sign with additional metadata
cosign sign --key cosign.key \
  -a "git_sha=$(git rev-parse HEAD)" \
  -a "build_date=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  myapp:latest

# Attach SBOM to image
cosign attach sbom --sbom sbom/myapp-$(date +%Y%m%d).json myapp:latest
```

### Policy Enforcement

#### Test OPA Policies
```bash
# Test policy against input
cd /home/user/Portfolio-Project/projects/4-devsecops

# Test deployment policy
opa eval -d policies/ -i manifests/deployment.yaml \
  'data.kubernetes.admission.deny' \
  --format pretty

# Run policy tests
opa test policies/ -v

# Check policy coverage
opa test policies/ --coverage --format=json
```

#### Enforce Security Policies
```bash
# Check if deployment meets security requirements
cat > test-deployment.yaml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-app
spec:
  template:
    spec:
      containers:
      - name: app
        image: myapp:latest
        securityContext:
          runAsNonRoot: true
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
EOF

# Test against policies
opa eval -d policies/security.rego -i test-deployment.yaml 'data.kubernetes.admission.deny'

# Expected output: [] (empty means no violations)
```

#### Check Image for Policy Compliance
```bash
# Check image against security policy
cat > policy-check.sh << 'EOF'
#!/bin/bash
IMAGE=$1

echo "Checking image: $IMAGE"

# Check if image is signed
if ! cosign verify --key cosign.pub $IMAGE 2>/dev/null; then
  echo "FAIL: Image not signed"
  exit 1
fi

# Check for critical vulnerabilities
CRITICAL=$(trivy image --severity CRITICAL --format json $IMAGE | jq '.Results[].Vulnerabilities | length')
if [ "$CRITICAL" -gt 0 ]; then
  echo "FAIL: $CRITICAL critical vulnerabilities found"
  exit 1
fi

# Check if SBOM exists
if ! cosign verify-attestation --type spdx --key cosign.pub $IMAGE 2>/dev/null; then
  echo "FAIL: No SBOM attached"
  exit 1
fi

echo "PASS: Image meets security requirements"
EOF

chmod +x policy-check.sh
./policy-check.sh myapp:latest
```

### Security Gate Operations

#### Pre-Build Security Checks
```bash
# Check source code for secrets
trivy fs --security-checks secret .

# Check dependencies for vulnerabilities
trivy fs --security-checks vuln .

# Scan infrastructure as code
trivy config terraform/
trivy config manifests/

# Check for hardcoded credentials
grep -r "password\|secret\|api_key" --include="*.py" --include="*.js" .

# Run SAST (Static Application Security Testing)
# Using semgrep
semgrep --config auto .
```

#### Post-Build Security Checks
```bash
# Scan container image
trivy image --severity CRITICAL,HIGH myapp:latest

# Generate SBOM
syft myapp:latest -o json > sbom/myapp.json

# Sign image
cosign sign --key cosign.key myapp:latest

# Run container compliance checks
docker-bench-security

# Check image configuration
trivy image --security-checks config myapp:latest
```

#### Pre-Deployment Security Checks
```bash
# Verify image signature
cosign verify --key cosign.pub myapp:latest

# Check Kubernetes manifests
trivy config manifests/
kubesec scan manifests/deployment.yaml

# Check for policy violations
opa eval -d policies/ -i manifests/ 'data.kubernetes.admission.deny'

# Verify image hasn't been tampered with
cosign verify --key cosign.pub myapp:latest | jq
```

---

## Incident Response

### Detection

**Automated Detection:**
- Critical CVE alerts from Trivy scans
- Policy violation alerts from OPA
- Unsigned image deployment attempts
- Security scan failures in CI/CD

**Manual Detection:**
```bash
# Check for critical vulnerabilities
trivy image --severity CRITICAL myapp:latest

# Check recent security scan reports
ls -lh reports/trivy-scan-*.json
cat reports/trivy-scan-latest.json | jq '.Results[].Vulnerabilities[] | select(.Severity=="CRITICAL")'

# Check for unsigned images in production
kubectl get pods -n production -o json | \
  jq '.items[].spec.containers[].image' | \
  xargs -I {} cosign verify --key cosign.pub {}

# Check policy violations
opa eval -d policies/ -i manifests/ 'data.kubernetes.admission.deny'
```

### Triage

#### Severity Classification

### P0: Critical Security Incident
- Critical CVE (CVSS >9) in production
- Active exploit detected
- Unsigned image deployed to production
- Security policy bypass detected
- Credentials leaked in code or logs

### P1: High Security Risk
- High severity CVE (CVSS 7-9) in production
- Multiple medium vulnerabilities
- SBOM missing for production deployment
- Security scan failed, deployment blocked
- Policy violation in production

### P2: Medium Security Risk
- Medium severity vulnerabilities
- SBOM generation failed
- Non-critical policy warnings
- Security scan delays

### P3: Low Security Risk
- Low severity vulnerabilities
- Minor compliance issues
- Security scan performance issues

### Incident Response Procedures

#### P0: Critical CVE in Production Image

**Immediate Actions (0-15 minutes):**
```bash
# 1. Identify affected images and deployments
trivy image --severity CRITICAL myapp:v1.2.3

# 2. Document CVE details
trivy image --format json myapp:v1.2.3 | \
  jq '.Results[].Vulnerabilities[] | select(.Severity=="CRITICAL")' > incident-cve-$(date +%Y%m%d-%H%M).json

# 3. Assess impact
cat incident-cve-$(date +%Y%m%d-%H%M).json | jq -r '.Title, .Description, .PrimaryURL'

# 4. Check if exploit is public
# Review CVE details and check exploit-db.com

# 5. Notify security team
echo "P0: Critical CVE detected in production" | mail -s "Security Alert" security-team@example.com
```

**Mitigation (15-60 minutes):**
```bash
# Option 1: Update vulnerable package
# Update Dockerfile
echo "RUN apt-get update && apt-get upgrade -y <vulnerable-package>" >> Dockerfile

# Rebuild and scan
docker build -t myapp:v1.2.4-security .
trivy image --severity CRITICAL myapp:v1.2.4-security

# If clean, deploy
docker push myapp:v1.2.4-security
kubectl set image deployment/myapp app=myapp:v1.2.4-security -n production

# Option 2: Rollback to known good version
kubectl rollout undo deployment/myapp -n production

# Option 3: Apply temporary mitigation
# If patch not available, implement workaround (firewall rules, disable feature, etc.)

# Verify mitigation
kubectl get pods -n production -l app=myapp
trivy image --severity CRITICAL $(kubectl get deployment myapp -n production -o jsonpath='{.spec.template.spec.containers[0].image}')
```

**Investigation (1-4 hours):**
```bash
# Check when vulnerable image was deployed
kubectl rollout history deployment/myapp -n production

# Check if exploit attempts in logs
kubectl logs -l app=myapp -n production --since=24h | grep -i "exploit\|attack\|suspicious"

# Check for indicators of compromise
# Review application logs, network logs, system logs

# Generate incident report
cat > incidents/cve-incident-$(date +%Y%m%d).md << 'EOF'
# Critical CVE Incident Report

**Date:** $(date)
**CVE:** CVE-XXXX-XXXXX
**CVSS Score:** X.X
**Affected Image:** myapp:v1.2.3

## Timeline
- HH:MM: CVE detected in scan
- HH:MM: Security team notified
- HH:MM: Patch deployed
- HH:MM: Verification complete

## Impact
- Production services affected: [list]
- Exploit available: Yes/No
- Evidence of exploitation: None found

## Remediation
- Updated package X from version Y to Z
- Redeployed with image myapp:v1.2.4-security

## Action Items
- [ ] Review vulnerability scanning frequency
- [ ] Add CVE to watchlist
- [ ] Update base images

EOF
```

#### P0: Unsigned Image Deployed to Production

**Immediate Actions (0-5 minutes):**
```bash
# 1. Identify unsigned image
kubectl get pods -n production -o json | \
  jq -r '.items[].spec.containers[].image' | \
  while read image; do
    echo "Checking $image"
    if ! cosign verify --key cosign.pub $image 2>/dev/null; then
      echo "UNSIGNED: $image"
    fi
  done

# 2. Block deployment
kubectl scale deployment <deployment-name> --replicas=0 -n production

# 3. Notify security team
echo "P0: Unsigned image deployed to production" | mail -s "Security Policy Violation" security-team@example.com

# 4. Investigate deployment
kubectl describe deployment <deployment-name> -n production
kubectl get events -n production --sort-by='.lastTimestamp' | head -20
```

**Resolution (5-30 minutes):**
```bash
# 1. Sign the image if it's legitimate
cosign sign --key cosign.key <unsigned-image>

# 2. Verify signature
cosign verify --key cosign.pub <signed-image>

# 3. Redeploy with signed image
kubectl scale deployment <deployment-name> --replicas=3 -n production

# 4. Implement admission controller to prevent unsigned images
cat > policies/image-signature-policy.yaml << 'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: image-policy
spec:
  containers:
  - name: policy-controller
    image: policy-controller:latest
    env:
    - name: REQUIRE_IMAGE_SIGNATURE
      value: "true"
EOF

kubectl apply -f policies/image-signature-policy.yaml
```

#### P1: High Severity CVE Detected

**Investigation (0-15 minutes):**
```bash
# Scan image for high severity vulnerabilities
trivy image --severity HIGH myapp:latest

# Export detailed report
trivy image --severity HIGH --format json --output reports/high-cve-$(date +%Y%m%d).json myapp:latest

# Review CVE details
cat reports/high-cve-$(date +%Y%m%d).json | jq '.Results[].Vulnerabilities[] | {Title: .Title, CVSS: .CVSS, FixedVersion: .FixedVersion}'

# Check if fix available
cat reports/high-cve-$(date +%Y%m%d).json | jq '.Results[].Vulnerabilities[] | select(.FixedVersion != "")'
```

**Remediation (1-4 hours):**
```bash
# Update dependencies
# For Python
pip install --upgrade <vulnerable-package>
pip freeze > requirements.txt

# For Node.js
npm audit fix
npm update

# For system packages
# Update Dockerfile
RUN apt-get update && apt-get upgrade -y

# Rebuild and test
docker build -t myapp:patched .
trivy image --severity HIGH myapp:patched

# Deploy patch
docker push myapp:patched
kubectl set image deployment/myapp app=myapp:patched -n production
```

#### P1: Security Scan Failed

**Investigation:**
```bash
# Check GitHub Actions logs
gh run list --workflow=security-scan.yaml --status failure

# View failed run details
gh run view <run-id> --log

# Common issues:
# - Trivy database update failed
# - Network connectivity issues
# - Scanner timeout
# - Image registry authentication failure
```

**Resolution:**
```bash
# Update Trivy database manually
trivy image --download-db-only

# Test scan locally
trivy image myapp:latest

# Update GitHub Actions workflow if needed
cd /home/user/Portfolio-Project/projects/4-devsecops
vi .github/workflows/security-scan.yaml

# Rerun workflow
gh run rerun <run-id>
```

#### P2: SBOM Generation Failed

**Investigation:**
```bash
# Check SBOM generation
syft myapp:latest -o json

# Check for errors
syft myapp:latest -o json --verbose 2>&1 | grep ERROR

# Common issues:
# - Image layers not accessible
# - Unsupported package format
# - Syft version outdated
```

**Resolution:**
```bash
# Update Syft
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

# Generate SBOM with verbose output
syft myapp:latest -o json --verbose > sbom/myapp.json

# Verify SBOM
cat sbom/myapp.json | jq '.artifacts | length'

# Attach to image
cosign attach sbom --sbom sbom/myapp.json myapp:latest
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/security-incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Security Incident Report

**Date:** $(date)
**Severity:** P0/P1/P2
**Type:** CVE / Policy Violation / Unsigned Image
**Duration:** XX minutes

## Timeline
- HH:MM: Security issue detected
- HH:MM: Investigation started
- HH:MM: Root cause identified
- HH:MM: Patch applied
- HH:MM: Verification complete

## Root Cause
[Description of vulnerability or security issue]

## Impact
- Affected services: [list]
- Data exposed: None
- Exploitation detected: No

## Remediation
[Description of fix]

## Action Items
- [ ] Update security scanning policies
- [ ] Improve vulnerability detection
- [ ] Add monitoring for similar issues
- [ ] Update security training

EOF

# Update security metrics
echo "$(date),P1,CVE,60" >> metrics/security-incidents.csv

# Review and update security policies
```

---

## Monitoring & Troubleshooting

### Essential Troubleshooting Commands

#### Vulnerability Scanning Issues
```bash
# Test Trivy installation
trivy --version

# Update vulnerability database
trivy image --download-db-only

# Scan with verbose output
trivy image --severity CRITICAL,HIGH --format json myapp:latest 2>&1 | tee scan-debug.log

# Clear Trivy cache
trivy image --clear-cache

# Scan specific layers
trivy image --format json myapp:latest | jq '.Results[].Target'
```

#### SBOM Issues
```bash
# Generate SBOM with debug output
syft myapp:latest -vv

# Check Syft version
syft version

# List all packages found
syft myapp:latest -o table

# Compare SBOM formats
syft myapp:latest -o json > sbom.json
syft myapp:latest -o spdx-json > sbom-spdx.json
syft myapp:latest -o cyclonedx-json > sbom-cyclonedx.json
```

#### Image Signing Issues
```bash
# Verify Cosign installation
cosign version

# Generate new key pair if needed
cosign generate-key-pair

# Sign with verbose output
cosign sign --key cosign.key myapp:latest --verbose

# Verify signature
cosign verify --key cosign.pub myapp:latest

# Check signature metadata
cosign verify --key cosign.pub myapp:latest | jq

# Troubleshoot registry authentication
docker login <registry>
cosign login <registry>
```

#### Policy Enforcement Issues
```bash
# Test OPA installation
opa version

# Validate policy syntax
opa check policies/

# Test policy evaluation
opa eval -d policies/ -i test-input.json 'data.kubernetes.admission.deny' --explain full

# Debug policy rules
opa test policies/ -v --explain full

# Check policy coverage
opa test policies/ --coverage
```

### Common Issues & Solutions

#### Issue: Trivy Scan Timeout

**Symptoms:**
- Scan takes >10 minutes
- Scan fails with timeout error

**Diagnosis:**
```bash
# Check image size
docker images myapp:latest

# Check layer count
docker history myapp:latest | wc -l
```

**Solution:**
```bash
# Increase timeout in GitHub Actions
# In .github/workflows/security-scan.yaml
- name: Scan image
  run: trivy image --timeout 15m myapp:latest

# Use multi-stage build to reduce image size
# Optimize Dockerfile

# Use Trivy in client-server mode for faster scans
trivy server --listen 0.0.0.0:8080
trivy client --remote http://localhost:8080 myapp:latest
```

---

#### Issue: False Positive Vulnerabilities

**Symptoms:**
- CVE reported but not applicable
- Package not actually used at runtime

**Solution:**
```bash
# Create Trivy ignore file
cat > .trivyignore << 'EOF'
# Vulnerability in dev dependency
CVE-2023-12345

# Not exploitable in this context
CVE-2023-67890
EOF

# Run scan with ignore file
trivy image --ignorefile .trivyignore myapp:latest

# Document why ignoring in comments
```

---

#### Issue: SBOM Missing Dependencies

**Symptoms:**
- SBOM shows fewer packages than expected
- Known dependencies not listed

**Diagnosis:**
```bash
# Check what Syft detects
syft myapp:latest -o table

# Check specific package manager
syft myapp:latest -o json | jq '.artifacts[] | select(.type=="python")'
```

**Solution:**
```bash
# Ensure package manager files are in image
# For Python, include requirements.txt
# For Node.js, include package-lock.json
# For Go, include go.mod and go.sum

# Generate SBOM from multiple sources
syft dir:. -o json > sbom-source.json
syft myapp:latest -o json > sbom-image.json

# Merge SBOMs if needed
jq -s '.[0].artifacts + .[1].artifacts | unique_by(.name)' sbom-source.json sbom-image.json > sbom-complete.json
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 0 seconds (all security artifacts in Git)
- **RTO** (Recovery Time Objective): 10 minutes (regenerate security artifacts)

### Backup Strategy

#### Security Artifacts Backup
```bash
# Backup signing keys (CRITICAL - store securely)
cp cosign.key backups/cosign.key-$(date +%Y%m%d)
cp cosign.pub backups/cosign.pub-$(date +%Y%m%d)

# Encrypt and store in secure location
gpg --encrypt --recipient security-team@example.com backups/cosign.key-$(date +%Y%m%d)

# Backup SBOM files
mkdir -p backups/sbom
cp sbom/*.json backups/sbom/

# Backup security scan reports
mkdir -p backups/reports
cp reports/*.json backups/reports/

# Backup policies
git add policies/
git commit -m "backup: security policies $(date +%Y-%m-%d)"
git push
```

#### Recovery Procedures
```bash
# Restore signing keys
gpg --decrypt backups/cosign.key-20251110.gpg > cosign.key
chmod 600 cosign.key

# Regenerate SBOM for all images
for tag in v1.0.0 v1.1.0 v1.2.0; do
  syft myapp:$tag -o json > sbom/myapp-$tag.json
  cosign attach sbom --sbom sbom/myapp-$tag.json myapp:$tag
done

# Re-sign all production images
for tag in v1.0.0 v1.1.0 v1.2.0; do
  cosign sign --key cosign.key myapp:$tag
done

# Verify recovery
cosign verify --key cosign.pub myapp:v1.2.0
```

---

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks
```bash
# Run security scans on latest images
trivy image --severity CRITICAL,HIGH $(docker images --format "{{.Repository}}:{{.Tag}}" | head -5)

# Check for new CVEs
trivy image --download-db-only

# Review security alerts
cat reports/trivy-scan-latest.json | jq '.Results[].Vulnerabilities[] | select(.Severity=="CRITICAL" or .Severity=="HIGH")'

# Verify image signatures
kubectl get pods -n production -o jsonpath='{.items[*].spec.containers[*].image}' | \
  tr ' ' '\n' | sort -u | \
  xargs -I {} cosign verify --key cosign.pub {}
```

#### Weekly Tasks
```bash
# Generate security report
cat > reports/weekly-security-$(date +%Y%m%d).md << 'EOF'
# Weekly Security Report

## Vulnerability Summary
$(trivy image myapp:latest --format json | jq '.Results[].Vulnerabilities | group_by(.Severity) | map({Severity: .[0].Severity, Count: length})')

## SBOM Status
- SBOM files generated: $(ls sbom/*.json | wc -l)
- Total packages: $(cat sbom/myapp-latest.json | jq '.artifacts | length')

## Compliance
- Signed images: $(find signed-images.txt | wc -l)
- Policy violations: 0

EOF

# Update vulnerability database
trivy image --download-db-only

# Review and update security policies
opa test policies/ -v

# Archive old security reports
mkdir -p archives/$(date +%Y-%m)
mv reports/trivy-scan-*.json archives/$(date +%Y-%m)/ 2>/dev/null || true
```

#### Monthly Tasks
```bash
# Update security tools
# Update Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin latest

# Update Syft
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

# Update Cosign
curl -sL https://github.com/sigstore/cosign/releases/latest/download/cosign-linux-amd64 -o /usr/local/bin/cosign
chmod +x /usr/local/bin/cosign

# Review security policies
cd /home/user/Portfolio-Project/projects/4-devsecops
git diff HEAD~30 policies/

# Conduct security audit
trivy repo --security-checks vuln,secret,config .

# Generate monthly security report
```

---

## Quick Reference Card

### Most Common Operations

```bash
# Scan image for vulnerabilities
trivy image --severity CRITICAL,HIGH myapp:latest

# Generate SBOM
syft myapp:latest -o json > sbom/myapp.json

# Sign image
cosign sign --key cosign.key myapp:latest

# Verify signature
cosign verify --key cosign.pub myapp:latest

# Check policies
opa eval -d policies/ -i manifests/ 'data.kubernetes.admission.deny'

# Run full security pipeline
trivy image myapp:latest && \
syft myapp:latest -o json > sbom/myapp.json && \
cosign sign --key cosign.key myapp:latest && \
cosign verify --key cosign.pub myapp:latest
```

### Emergency Response

```bash
# P0: Critical CVE - immediate scan
trivy image --severity CRITICAL myapp:v1.2.3
kubectl set image deployment/myapp app=myapp:v1.2.4-patched -n production

# P0: Unsigned image - block deployment
kubectl scale deployment <name> --replicas=0 -n production
cosign sign --key cosign.key <image>

# P1: High CVE - update dependencies
docker build -t myapp:patched .
trivy image myapp:patched
docker push myapp:patched

# Check all production images for issues
kubectl get pods -n production -o jsonpath='{.items[*].spec.containers[*].image}' | tr ' ' '\n' | sort -u | xargs -I {} trivy image --severity CRITICAL {}
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Security Engineering Team
- **Review Schedule:** Monthly or after security incidents
- **Feedback:** Create issue or submit PR with updates
