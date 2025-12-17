# Runbook — P16 (Zero-Trust Cloud Architecture)

## Overview

Production operations runbook for zero-trust security architecture. This runbook covers certificate management, JWT policy enforcement, network micro-segmentation, and incident response for zero-trust network operations.

**System Components:**
- mTLS certificate infrastructure
- JWT authentication and authorization policies
- API Gateway with token validation
- Network micro-segmentation
- Secret Vault (HashiCorp Vault)
- Identity Provider (IAM/OAuth2)
- Security monitoring and threat detection

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Certificate validity** | 100% valid, no expired certs | Automated cert expiration checks |
| **JWT validation success rate** | 99.9% | API Gateway validation metrics |
| **mTLS handshake success rate** | 99.5% | Service-to-service connection metrics |
| **Authentication latency** | < 100ms p95 | JWT validation duration |
| **Secret rotation compliance** | 100% rotated within 90 days | Vault secret age tracking |
| **Zero-trust policy violations** | Zero unauthorized access attempts | Security monitoring alerts |

---

## Dashboards & Alerts

### Dashboards

#### Certificate Health Dashboard
```bash
# Check certificate expiration status
make verify-certs

# List all certificates and expiration dates
find ${CA_CERT_PATH} -name "*.crt" -type f -exec openssl x509 -in {} -noout -subject -dates \; | \
  awk '/subject=/{cert=$0} /notAfter/{print cert" | Expires: "$0}'

# Check certificates expiring in next 30 days
for cert in ${CA_CERT_PATH}/*.crt; do
  EXPIRY=$(openssl x509 -in $cert -noout -enddate | cut -d= -f2)
  EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s)
  NOW_EPOCH=$(date +%s)
  DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))
  if [ $DAYS_LEFT -lt 30 ]; then
    echo "WARNING: $cert expires in $DAYS_LEFT days"
  fi
done
```

#### Authentication Dashboard
```bash
# Monitor JWT validation metrics
curl -s ${GATEWAY_URL}/metrics | grep jwt_validation_total

# Check failed authentication attempts
curl -s ${GATEWAY_URL}/metrics | grep auth_failures_total

# Review active sessions
curl -s ${GATEWAY_URL}/api/sessions | jq '.active_sessions'
```

#### mTLS Connection Dashboard
```bash
# Verify mTLS connections between services
make verify-mtls

# Test service-to-service connection
openssl s_client -connect service-a:443 \
  -cert ${CA_CERT_PATH}/client.crt \
  -key ${CA_CERT_PATH}/client.key \
  -CAfile ${CA_CERT_PATH}/ca.crt

# Check TLS version enforcement
nmap --script ssl-enum-ciphers -p 443 service-a
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Certificate expired | Immediate | Emergency cert renewal |
| **P0** | Zero-trust policy breach | Immediate | Isolate service, investigate |
| **P1** | Certificate expiring < 7 days | 1 hour | Renew certificates |
| **P1** | JWT validation failures > 5% | 15 minutes | Investigate auth service |
| **P2** | mTLS handshake failures | 30 minutes | Check cert trust chain |
| **P2** | Unauthorized access attempts | 1 hour | Review security logs |
| **P3** | Secret age > 60 days | 24 hours | Schedule secret rotation |

#### Alert Queries

```bash
# Check for expired certificates
EXPIRED=0
for cert in ${CA_CERT_PATH}/*.crt; do
  if ! openssl x509 -in $cert -noout -checkend 0 2>/dev/null; then
    echo "ALERT: Expired certificate: $cert"
    EXPIRED=1
  fi
done
exit $EXPIRED

# Monitor JWT validation failures
FAILURE_RATE=$(curl -s ${GATEWAY_URL}/metrics | \
  awk '/jwt_validation_failures_total/{failures=$2} /jwt_validation_total/{total=$2} END{print (failures/total)*100}')
if [ $(echo "$FAILURE_RATE > 5" | bc) -eq 1 ]; then
  echo "ALERT: JWT validation failure rate: ${FAILURE_RATE}%"
fi

# Check for policy violations
if [ $(journalctl -u zero-trust-monitor -n 1000 | grep -c "POLICY_VIOLATION") -gt 0 ]; then
  echo "ALERT: Zero-trust policy violations detected"
  journalctl -u zero-trust-monitor | grep "POLICY_VIOLATION" | tail -10
fi
```

---

## Standard Operations

### Certificate Management

#### Generate New Certificates
```bash
# Initialize CA if not exists
make setup

# Generate CA certificate
make generate-ca

# Generate service certificates
make generate-certs SERVICE=service-a

# Generate client certificates
./scripts/generate-client-cert.sh client-name

# Verify certificate chain
openssl verify -CAfile ${CA_CERT_PATH}/ca.crt ${CA_CERT_PATH}/service-a.crt
```

#### Renew Certificates
```bash
# Check which certificates need renewal
./scripts/check-cert-expiry.sh

# Renew service certificate
./scripts/renew-cert.sh service-a

# Distribute renewed certificates
make deploy-certs SERVICE=service-a

# Verify new certificate is active
openssl s_client -connect service-a:443 -showcerts | \
  openssl x509 -noout -dates
```

#### Revoke Certificates
```bash
# Revoke compromised certificate
openssl ca -revoke ${CA_CERT_PATH}/compromised.crt \
  -keyfile ${CA_CERT_PATH}/ca.key \
  -cert ${CA_CERT_PATH}/ca.crt

# Generate updated CRL (Certificate Revocation List)
openssl ca -gencrl -out ${CA_CERT_PATH}/ca.crl \
  -keyfile ${CA_CERT_PATH}/ca.key \
  -cert ${CA_CERT_PATH}/ca.crt

# Distribute CRL to all services
make deploy-crl
```

### JWT Policy Management

#### Deploy JWT Policies
```bash
# Validate JWT policy syntax
./scripts/validate-jwt-policy.sh policies/api-access.json

# Test policy locally
./scripts/test-jwt-policy.sh policies/api-access.json test-token.jwt

# Deploy policy to API Gateway
make deploy-policies POLICY=policies/api-access.json

# Verify policy is active
curl -H "Authorization: Bearer $TEST_TOKEN" ${GATEWAY_URL}/api/test
```

#### Update JWT Signing Keys
```bash
# Generate new JWT signing key
openssl rand -base64 64 > ${JWT_SECRET_PATH}/jwt-secret-new.key

# Update Vault with new key
vault kv put secret/jwt signing_key=@${JWT_SECRET_PATH}/jwt-secret-new.key

# Update Gateway configuration
kubectl set env deployment/api-gateway JWT_SECRET_VERSION=v2

# Monitor for validation errors
kubectl logs -f deployment/api-gateway | grep "jwt_validation"

# Rotate old key after validation (24-48 hour grace period)
vault kv delete secret/jwt/old
```

#### Revoke JWT Tokens
```bash
# Add token to revocation list
curl -X POST ${GATEWAY_URL}/api/admin/tokens/revoke \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"jti": "compromised-token-id"}'

# Verify token is revoked
curl -H "Authorization: Bearer $REVOKED_TOKEN" ${GATEWAY_URL}/api/test
# Expected: 401 Unauthorized

# Bulk revoke tokens for user
./scripts/revoke-user-tokens.sh user@example.com
```

### Network Segmentation Operations

#### Verify Network Policies
```bash
# Check network segmentation rules
kubectl get networkpolicies -A

# Test inter-service connectivity (should succeed with mTLS)
kubectl exec -it service-a -- curl https://service-b:443 \
  --cert /certs/client.crt \
  --key /certs/client.key \
  --cacert /certs/ca.crt

# Test blocked connections (should fail)
kubectl exec -it service-a -- curl http://service-b:80
# Expected: Connection refused or timeout
```

#### Update Network Policies
```bash
# Edit network policy
kubectl edit networkpolicy service-a-policy -n default

# Apply new policy
kubectl apply -f policies/network/service-a-policy.yaml

# Verify policy is active
kubectl describe networkpolicy service-a-policy -n default

# Test connectivity after policy change
make test-connectivity
```

### Secret Management

#### Rotate Secrets in Vault
```bash
# Check secret age
vault kv metadata get secret/app-config

# Rotate database credentials
./scripts/rotate-db-secret.sh production

# Rotate API keys
vault kv put secret/api-keys \
  service_a_key=$(openssl rand -base64 32) \
  service_b_key=$(openssl rand -base64 32)

# Verify applications pick up new secrets
kubectl rollout restart deployment/service-a
kubectl rollout status deployment/service-a
```

#### Backup Vault State
```bash
# Create Vault snapshot
vault operator raft snapshot save vault-backup-$(date +%Y%m%d).snap

# Verify snapshot
vault operator raft snapshot inspect vault-backup-*.snap

# Store snapshot securely
aws s3 cp vault-backup-*.snap s3://vault-backups/$(date +%Y/%m/%d)/
```

---

## Incident Response

### Detection

**Automated Detection:**
- Certificate expiration alerts
- JWT validation failure metrics
- mTLS handshake failures
- Network policy violations
- Vault audit log anomalies

**Manual Detection:**
```bash
# Check security monitoring dashboard
./scripts/security-dashboard.sh

# Review Vault audit logs
vault audit list
vault read sys/audit-hash/file data=suspicious-token

# Check for authentication anomalies
journalctl -u api-gateway | grep -i "authentication\|unauthorized" | tail -50

# Review network traffic
tcpdump -i any -n "port 443" -c 100 | grep -v "TLS"
```

### Triage

#### Severity Classification

### P0: Critical Security Breach
- Expired CA certificate (all mTLS broken)
- Zero-trust policy bypass confirmed
- Vault unsealed by unauthorized entity
- Mass token compromise

### P1: Security Degradation
- Service certificate expired
- JWT validation failures > 10%
- Unauthorized access attempts detected
- Secret rotation overdue > 90 days

### P2: Security Warning
- Certificate expiring < 7 days
- mTLS handshake failures < 5%
- Network policy misconfiguration
- Audit log anomalies

### P3: Informational
- Certificate expiring < 30 days
- Single failed authentication attempt
- Secret age > 60 days

### Incident Response Procedures

#### P0: Expired CA Certificate

**Immediate Actions (0-5 minutes):**
```bash
# 1. Confirm CA certificate status
openssl x509 -in ${CA_CERT_PATH}/ca.crt -noout -dates
openssl x509 -in ${CA_CERT_PATH}/ca.crt -noout -checkend 0 || echo "EXPIRED"

# 2. Emergency: Generate new CA (CRITICAL - impacts all services)
./scripts/emergency-ca-renewal.sh

# 3. Generate new service certificates
for service in service-a service-b service-c; do
  ./scripts/generate-service-cert.sh $service
done

# 4. Deploy new certificates (rolling update)
make deploy-certs-emergency

# 5. Notify all teams
./scripts/notify-incident.sh "P0: CA certificate expired - emergency renewal in progress"
```

**Investigation (5-30 minutes):**
```bash
# Identify why certificate expiration was missed
grep "certificate_expiry_check" /var/log/monitoring/*.log | tail -100

# Check monitoring system
systemctl status cert-monitor

# Review alert configuration
cat /etc/alertmanager/config.yml | grep certificate
```

**Prevention:**
```bash
# Implement 30-day warning alerts
# Implement 7-day critical alerts
# Add monitoring system health checks
# Document CA renewal procedure in advance
```

#### P0: Zero-Trust Policy Breach

**Immediate Actions (0-5 minutes):**
```bash
# 1. Identify breach source
journalctl -u zero-trust-monitor -n 500 | grep "POLICY_VIOLATION\|UNAUTHORIZED"

# 2. Isolate compromised service
kubectl scale deployment/compromised-service --replicas=0

# 3. Block suspicious IPs at gateway
./scripts/block-ip.sh 192.168.1.100

# 4. Revoke suspicious tokens
./scripts/emergency-token-revoke.sh

# 5. Enable enhanced logging
kubectl patch deployment/api-gateway -p '{"spec":{"template":{"spec":{"containers":[{"name":"gateway","env":[{"name":"LOG_LEVEL","value":"DEBUG"}]}]}}}}'
```

**Investigation (5-60 minutes):**
```bash
# Review authentication logs
kubectl logs deployment/api-gateway --tail=1000 | grep "authentication"

# Check network traffic patterns
./scripts/analyze-network-traffic.sh --since="1 hour ago"

# Review Vault access logs
vault audit -format=json | jq 'select(.type=="response" and .error != null)'

# Identify attack vector
./scripts/threat-analysis.sh --incident-id=$INCIDENT_ID
```

**Remediation:**
```bash
# Patch vulnerability
git apply patches/security-fix.patch
make deploy-policies

# Reset all secrets
./scripts/rotate-all-secrets.sh

# Re-issue all certificates (if compromised)
./scripts/reissue-all-certs.sh

# Update network policies
kubectl apply -f policies/network/tightened-policies.yaml
```

#### P1: JWT Validation Failures

**Investigation:**
```bash
# Check JWT validation metrics
curl -s ${GATEWAY_URL}/metrics | grep jwt_validation

# Sample failed requests
kubectl logs deployment/api-gateway | grep "jwt_validation_failed" | tail -50

# Test JWT validation manually
JWT_TOKEN="<token>"
echo $JWT_TOKEN | cut -d. -f2 | base64 -d | jq .

# Verify token signature
./scripts/verify-jwt.sh $JWT_TOKEN
```

**Common Causes & Fixes:**

**Clock Skew:**
```bash
# Check time synchronization
ntpq -p
timedatectl status

# Fix: Synchronize clocks
sudo ntpdate -s time.nist.gov
```

**Expired Tokens:**
```bash
# Check token expiration
./scripts/check-jwt-expiry.sh $JWT_TOKEN

# Fix: Issue new token
./scripts/issue-jwt.sh --user=user@example.com --duration=3600
```

**Invalid Signature:**
```bash
# Verify JWT secret is correct
vault kv get secret/jwt

# Fix: Update Gateway with correct secret
kubectl set env deployment/api-gateway JWT_SECRET=$(vault kv get -field=signing_key secret/jwt)
kubectl rollout restart deployment/api-gateway
```

#### P2: mTLS Handshake Failures

**Investigation:**
```bash
# Test mTLS connection manually
openssl s_client -connect service-a:443 \
  -cert ${CA_CERT_PATH}/client.crt \
  -key ${CA_CERT_PATH}/client.key \
  -CAfile ${CA_CERT_PATH}/ca.crt \
  -showcerts

# Check certificate validity
openssl verify -CAfile ${CA_CERT_PATH}/ca.crt ${CA_CERT_PATH}/service-a.crt

# Review TLS logs
kubectl logs deployment/service-a | grep -i "tls\|ssl\|certificate"
```

**Common Issues:**

**Certificate Mismatch:**
```bash
# Check certificate CN matches service name
openssl x509 -in ${CA_CERT_PATH}/service-a.crt -noout -subject

# Regenerate certificate with correct CN
./scripts/generate-service-cert.sh service-a --cn=service-a.default.svc.cluster.local
```

**Trust Chain Broken:**
```bash
# Verify CA certificate is distributed
kubectl get secret tls-ca-cert -n default -o jsonpath='{.data.ca\.crt}' | base64 -d | \
  openssl x509 -noout -subject

# Redeploy CA certificate
make deploy-ca-cert
kubectl rollout restart deployment/service-a
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/incident-$(date +%Y%m%d-%H%M).md << EOF
# Security Incident Report

**Date:** $(date)
**Severity:** P0
**Duration:** 45 minutes
**Affected Components:** Zero-trust authentication

## Timeline
- 14:00: JWT validation failures detected
- 14:05: Identified expired JWT signing key
- 14:15: Rotated JWT secret in Vault
- 14:20: Restarted API Gateway
- 14:45: Service restored, validation success rate 99.9%

## Root Cause
JWT signing key expired due to missed rotation schedule

## Action Items
- [ ] Implement automated secret rotation
- [ ] Add secret age monitoring
- [ ] Update runbook with secret rotation procedure
- [ ] Conduct security training on secret management

EOF

# Update threat model
./scripts/update-threat-model.sh --incident=$INCIDENT_ID

# Review and update security policies
make review-policies
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: Certificate Validation Failed

**Symptoms:**
```bash
$ curl https://service-a:443
curl: (60) SSL certificate problem: unable to get local issuer certificate
```

**Diagnosis:**
```bash
# Check certificate chain
openssl s_client -connect service-a:443 -showcerts

# Verify CA certificate
openssl verify -CAfile ${CA_CERT_PATH}/ca.crt ${CA_CERT_PATH}/service-a.crt
```

**Solution:**
```bash
# Update CA certificate bundle
cat ${CA_CERT_PATH}/ca.crt >> /etc/ssl/certs/ca-certificates.crt
update-ca-certificates

# Or specify CA explicitly
curl --cacert ${CA_CERT_PATH}/ca.crt https://service-a:443
```

---

#### Issue: JWT Token Rejected

**Symptoms:**
```bash
$ curl -H "Authorization: Bearer $TOKEN" ${GATEWAY_URL}/api/test
{"error": "invalid token"}
```

**Diagnosis:**
```bash
# Decode JWT
echo $TOKEN | cut -d. -f2 | base64 -d | jq .

# Check expiration
EXP=$(echo $TOKEN | cut -d. -f2 | base64 -d | jq -r .exp)
NOW=$(date +%s)
echo "Token expired: $([ $EXP -lt $NOW ] && echo YES || echo NO)"

# Verify signature
./scripts/verify-jwt-signature.sh $TOKEN
```

**Solution:**
```bash
# Issue new token
NEW_TOKEN=$(./scripts/issue-jwt.sh --user=user@example.com --duration=3600)

# Test with new token
curl -H "Authorization: Bearer $NEW_TOKEN" ${GATEWAY_URL}/api/test
```

---

#### Issue: Service Cannot Connect (mTLS)

**Symptoms:**
- Service-to-service calls failing
- "TLS handshake failed" errors

**Diagnosis:**
```bash
# Test connection manually
openssl s_client -connect service-b:443 \
  -cert ${CA_CERT_PATH}/service-a.crt \
  -key ${CA_CERT_PATH}/service-a.key \
  -CAfile ${CA_CERT_PATH}/ca.crt

# Check certificates are mounted
kubectl exec deployment/service-a -- ls -la /certs/

# Verify certificate matches key
openssl x509 -noout -modulus -in ${CA_CERT_PATH}/service-a.crt | openssl md5
openssl rsa -noout -modulus -in ${CA_CERT_PATH}/service-a.key | openssl md5
```

**Solution:**
```bash
# Regenerate service certificate
./scripts/generate-service-cert.sh service-a

# Redeploy certificate to Kubernetes
kubectl create secret tls service-a-tls \
  --cert=${CA_CERT_PATH}/service-a.crt \
  --key=${CA_CERT_PATH}/service-a.key \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart service
kubectl rollout restart deployment/service-a
```

---

#### Issue: Vault Sealed

**Symptoms:**
```bash
$ vault status
Error checking seal status: Error making API request.
URL: GET https://vault:8200/v1/sys/seal-status
Code: 503. Errors: Vault is sealed
```

**Solution:**
```bash
# Unseal Vault (requires 3 of 5 unseal keys)
vault operator unseal $UNSEAL_KEY_1
vault operator unseal $UNSEAL_KEY_2
vault operator unseal $UNSEAL_KEY_3

# Verify Vault is unsealed
vault status | grep Sealed
# Expected: Sealed = false

# Check Vault health
vault status
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 1 hour (Vault snapshots)
- **RTO** (Recovery Time Objective): 15 minutes (Certificate regeneration + service restart)

### Backup Strategy

**Certificate Backups:**
```bash
# Backup all certificates
tar czf certs-backup-$(date +%Y%m%d).tar.gz ${CA_CERT_PATH}/

# Store securely
aws s3 cp certs-backup-*.tar.gz s3://security-backups/certs/

# Encrypt backup
gpg --encrypt --recipient security@example.com certs-backup-*.tar.gz
```

**Vault Backups:**
```bash
# Create Vault snapshot (hourly)
vault operator raft snapshot save vault-snapshot-$(date +%Y%m%d-%H%M).snap

# Verify snapshot
vault operator raft snapshot inspect vault-snapshot-*.snap

# Store securely
aws s3 cp vault-snapshot-*.snap s3://vault-backups/$(date +%Y/%m/%d)/
```

**Policy Backups:**
```bash
# Backup all policies
cp -r policies/ policies-backup-$(date +%Y%m%d)/
tar czf policies-backup-$(date +%Y%m%d).tar.gz policies-backup-*/

# Version control
git add policies/
git commit -m "backup: policies $(date +%Y-%m-%d)"
git push
```

### Disaster Recovery Procedures

#### Complete CA Loss

**Recovery Steps (15-30 minutes):**
```bash
# 1. Restore CA from backup
aws s3 cp s3://security-backups/certs/latest/ca.crt ${CA_CERT_PATH}/
aws s3 cp s3://security-backups/certs/latest/ca.key ${CA_CERT_PATH}/

# 2. Or regenerate CA (if no backup)
make generate-ca

# 3. Regenerate all service certificates
for service in service-a service-b service-c; do
  ./scripts/generate-service-cert.sh $service
done

# 4. Deploy certificates to all services
make deploy-certs-all

# 5. Restart all services
kubectl rollout restart deployment --all

# 6. Verify mTLS connections
make verify-mtls
```

#### Vault Data Loss

**Recovery Steps (10-15 minutes):**
```bash
# 1. Restore Vault from latest snapshot
vault operator raft snapshot restore vault-snapshot-latest.snap

# 2. Verify Vault data
vault kv list secret/

# 3. Test secret retrieval
vault kv get secret/jwt

# 4. Restart services to reload secrets
kubectl rollout restart deployment/api-gateway
```

### DR Drill Procedure

**Quarterly DR Drill (60 minutes):**
```bash
# 1. Announce drill
echo "DR drill starting at $(date)" | tee dr-drill-$(date +%Y%m%d).log

# 2. Simulate CA certificate loss
mv ${CA_CERT_PATH}/ca.crt ${CA_CERT_PATH}/ca.crt.backup
mv ${CA_CERT_PATH}/ca.key ${CA_CERT_PATH}/ca.key.backup

# 3. Start recovery timer
START_TIME=$(date +%s)

# 4. Execute recovery
./scripts/emergency-ca-renewal.sh
make generate-certs
make deploy-certs-all
kubectl rollout restart deployment --all

# 5. Verify recovery
make verify-mtls
make test

# 6. Calculate recovery time
END_TIME=$(date +%s)
RECOVERY_TIME=$((END_TIME - START_TIME))
echo "Recovery time: $RECOVERY_TIME seconds" | tee -a dr-drill-$(date +%Y%m%d).log

# 7. Restore from backup
mv ${CA_CERT_PATH}/ca.crt.backup ${CA_CERT_PATH}/ca.crt
mv ${CA_CERT_PATH}/ca.key.backup ${CA_CERT_PATH}/ca.key

# 8. Document results and lessons learned
```

---

## Maintenance Procedures

### Daily Tasks
```bash
# Check certificate expiration status
./scripts/check-cert-expiry.sh

# Review authentication failures
kubectl logs deployment/api-gateway | grep "auth_failure" | wc -l

# Check Vault seal status
vault status

# Monitor security alerts
./scripts/check-security-alerts.sh
```

### Weekly Tasks
```bash
# Review Vault audit logs
vault audit -format=json | jq 'select(.error != null)' | tail -50

# Analyze authentication patterns
./scripts/analyze-auth-patterns.sh --since="7 days ago"

# Check network policy effectiveness
kubectl get networkpolicies -A

# Review and update threat model
make review-threat-model
```

### Monthly Tasks
```bash
# Rotate JWT signing keys
./scripts/rotate-jwt-secret.sh

# Rotate Vault secrets
./scripts/rotate-all-secrets.sh

# Update security policies
make review-policies

# Conduct security audit
./scripts/security-audit.sh

# Test disaster recovery procedures
make dr-drill
```

### Quarterly Tasks
```bash
# Review and renew certificates (before expiration)
./scripts/renew-all-certs.sh

# Update zero-trust architecture documentation
make update-docs

# Conduct penetration testing
./scripts/pentest.sh

# Review and update security compliance
make compliance-check
```

---

## Operational Best Practices

### Pre-Deployment Checklist
- [ ] Certificates validated and not expiring soon
- [ ] JWT policies tested with valid and invalid tokens
- [ ] mTLS connections verified
- [ ] Network policies reviewed
- [ ] Vault secrets rotated recently
- [ ] Security monitoring enabled
- [ ] Incident response plan reviewed

### Post-Deployment Checklist
- [ ] All services authenticated successfully
- [ ] JWT validation success rate > 99%
- [ ] mTLS handshakes successful
- [ ] No policy violations detected
- [ ] Monitoring dashboards updated
- [ ] Security team notified

### Security Best Practices
- **Certificate lifetime:** 90 days for service certs, 1 year for CA
- **Secret rotation:** Every 90 days maximum
- **JWT token lifetime:** 1 hour for user tokens, 15 minutes for service tokens
- **Audit logging:** Enabled for all authentication and authorization events
- **Network policies:** Default deny, explicit allow
- **Principle of least privilege:** Minimal permissions for all services

---

## Quick Reference

### Most Common Operations
```bash
# Check certificate expiration
make verify-certs

# Generate new service certificate
./scripts/generate-service-cert.sh service-name

# Deploy certificates
make deploy-certs SERVICE=service-name

# Test mTLS connection
make verify-mtls

# Issue JWT token
./scripts/issue-jwt.sh --user=user@example.com

# Rotate JWT secret
./scripts/rotate-jwt-secret.sh

# Check Vault status
vault status

# Backup Vault
vault operator raft snapshot save backup.snap
```

### Emergency Response
```bash
# P0: Expired CA certificate
./scripts/emergency-ca-renewal.sh && make deploy-certs-all

# P0: Zero-trust breach
kubectl scale deployment/compromised-service --replicas=0
./scripts/block-suspicious-ips.sh

# P1: JWT validation failures
kubectl logs deployment/api-gateway | grep jwt_validation
./scripts/rotate-jwt-secret.sh

# P2: mTLS failures
./scripts/verify-cert-chain.sh
make deploy-certs
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Security Engineering Team
- **Review Schedule:** Quarterly or after security incidents
- **Feedback:** Create issue or submit PR with updates
