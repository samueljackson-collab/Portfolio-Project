# Runbook — Project 21 (Quantum-Safe Cryptography)

## Overview

Production operations runbook for the Quantum-Safe Cryptography service. This runbook covers hybrid
key exchange operations, cryptographic key management, KEM (Key Encapsulation Mechanism) operations,
and incident response for quantum-resistant cryptography systems.

**System Components:**

- Kyber KEM (quantum-resistant key encapsulation)
- Classical ECDH (Elliptic Curve Diffie-Hellman)
- Hybrid key exchange service
- Key rotation mechanisms
- Cryptographic validation layer
- Python-based service runtime

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Service availability** | 99.95% | Key exchange API uptime |
| **Key exchange latency (p95)** | < 100ms | Hybrid KEM+ECDH operation time |
| **Key generation success rate** | 99.99% | Successful key pair generation |
| **Encryption/decryption success rate** | 100% | Valid ciphertext operations |
| **Key rotation completion** | < 5 minutes | Full key rotation cycle |
| **Cryptographic validation pass rate** | 100% | Self-test and validation checks |
| **Memory usage** | < 512MB | Service memory footprint |

---

## Dashboards & Alerts

### Dashboards

#### Service Health Dashboard

```bash
# Check service status
systemctl status quantum-crypto.service

# Check process health
ps aux | grep key_exchange.py

# Check service logs
journalctl -u quantum-crypto.service -n 50

# Memory and CPU usage
top -p $(pgrep -f key_exchange.py)
```

#### Cryptographic Operations Dashboard

```bash
# Test key exchange endpoint
curl -X POST http://localhost:8000/api/key-exchange \
  -H "Content-Type: application/json" \
  -d '{"client_public_key":"test"}' | jq .

# Check operation metrics
curl -s http://localhost:8000/metrics | grep -E "key_exchange|kem_operation|ecdh_operation"

# Verify cryptographic self-tests
python -c "from src.key_exchange import run_self_tests; run_self_tests()"
```

#### Key Rotation Dashboard

```bash
# Check current key age
python -c "from src.key_exchange import get_key_age; print(f'Key age: {get_key_age()} hours')"

# List active keys
ls -lh /var/lib/quantum-crypto/keys/

# Check key rotation schedule
crontab -l | grep key-rotation
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Service down | Immediate | Restart service, check logs |
| **P0** | Cryptographic validation failure | Immediate | Stop operations, investigate keys |
| **P0** | Key corruption detected | Immediate | Restore from backup, rotate keys |
| **P1** | Key exchange latency > 500ms | 15 minutes | Check resource usage, optimize |
| **P1** | Key rotation failed | 30 minutes | Manual rotation, investigate failure |
| **P2** | High error rate (>0.1%) | 1 hour | Review logs, check input validation |
| **P2** | Memory usage > 80% | 2 hours | Check for leaks, restart if needed |
| **P3** | Key age > 7 days | 4 hours | Schedule rotation |

#### Alert Queries

```bash
# Check service health
if ! systemctl is-active --quiet quantum-crypto.service; then
  echo "ALERT: Quantum crypto service is down"
  exit 1
fi

# Check key exchange performance
RESPONSE_TIME=$(curl -w "%{time_total}" -o /dev/null -s http://localhost:8000/health)
if (( $(echo "$RESPONSE_TIME > 0.5" | bc -l) )); then
  echo "ALERT: High latency detected: ${RESPONSE_TIME}s"
fi

# Check key age
KEY_AGE=$(python -c "from src.key_exchange import get_key_age; print(get_key_age())")
if [ $KEY_AGE -gt 168 ]; then  # 7 days
  echo "ALERT: Keys are ${KEY_AGE} hours old, rotation recommended"
fi

# Check for cryptographic errors
ERROR_COUNT=$(journalctl -u quantum-crypto.service --since "1 hour ago" | grep -c "ERROR\|CRITICAL")
if [ $ERROR_COUNT -gt 10 ]; then
  echo "ALERT: $ERROR_COUNT errors in the last hour"
fi
```

---

## Standard Operations

### Service Management

#### Start/Stop Service

```bash
# Start service
sudo systemctl start quantum-crypto.service

# Stop service
sudo systemctl stop quantum-crypto.service

# Restart service
sudo systemctl restart quantum-crypto.service

# Check status
sudo systemctl status quantum-crypto.service

# Enable auto-start on boot
sudo systemctl enable quantum-crypto.service

# View real-time logs
sudo journalctl -u quantum-crypto.service -f
```

#### Manual Service Startup

```bash
# Activate Python virtual environment
cd /opt/quantum-crypto
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run service
python src/key_exchange.py

# Or run with debug logging
LOGLEVEL=DEBUG python src/key_exchange.py

# Run in background
nohup python src/key_exchange.py > /var/log/quantum-crypto/service.log 2>&1 &
```

#### Service Configuration

```bash
# Edit service configuration
sudo vim /etc/systemd/system/quantum-crypto.service

# Example configuration:
cat > /etc/systemd/system/quantum-crypto.service << 'EOF'
[Unit]
Description=Quantum-Safe Cryptography Service
After=network.target

[Service]
Type=simple
User=quantum-crypto
WorkingDirectory=/opt/quantum-crypto
Environment="PATH=/opt/quantum-crypto/venv/bin"
ExecStart=/opt/quantum-crypto/venv/bin/python src/key_exchange.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Restart service
sudo systemctl restart quantum-crypto.service
```

### Key Management

#### Generate New Key Pairs

```bash
# Generate Kyber key pair
python -c "from src.key_exchange import generate_kyber_keypair; generate_kyber_keypair()"

# Generate ECDH key pair
python -c "from src.key_exchange import generate_ecdh_keypair; generate_ecdh_keypair()"

# Generate hybrid key pair
python -c "from src.key_exchange import generate_hybrid_keypair; generate_hybrid_keypair()"

# Verify key generation
ls -lh /var/lib/quantum-crypto/keys/
```

#### Key Rotation

```bash
# Manual key rotation
python -c "from src.key_exchange import rotate_keys; rotate_keys()"

# Or use rotation script
cd /opt/quantum-crypto
./scripts/rotate-keys.sh

# Verify rotation completed
python -c "from src.key_exchange import verify_key_rotation; verify_key_rotation()"

# Check new key age
python -c "from src.key_exchange import get_key_age; print(f'New key age: {get_key_age()} hours')"
```

#### Backup Keys

```bash
# Backup current keys
mkdir -p /backup/quantum-crypto/keys/$(date +%Y%m%d)
cp -r /var/lib/quantum-crypto/keys/* /backup/quantum-crypto/keys/$(date +%Y%m%d)/

# Verify backup
ls -lh /backup/quantum-crypto/keys/$(date +%Y%m%d)/

# Encrypt backup (recommended)
tar czf - /var/lib/quantum-crypto/keys/ | \
  gpg --symmetric --cipher-algo AES256 > \
  /backup/quantum-crypto/keys-$(date +%Y%m%d).tar.gz.gpg

# Store offsite
aws s3 cp /backup/quantum-crypto/keys-$(date +%Y%m%d).tar.gz.gpg \
  s3://crypto-backups/quantum-safe/
```

#### Restore Keys

```bash
# Stop service
sudo systemctl stop quantum-crypto.service

# Restore from backup
BACKUP_DATE="20251110"
rm -rf /var/lib/quantum-crypto/keys/*
cp -r /backup/quantum-crypto/keys/$BACKUP_DATE/* /var/lib/quantum-crypto/keys/

# Or restore from encrypted backup
gpg --decrypt /backup/quantum-crypto/keys-$BACKUP_DATE.tar.gz.gpg | \
  tar xzf - -C /

# Verify restored keys
python -c "from src.key_exchange import verify_keys; verify_keys()"

# Start service
sudo systemctl start quantum-crypto.service
```

### Cryptographic Operations

#### Test Key Exchange

```bash
# Full key exchange test
python -c "
from src.key_exchange import test_key_exchange
result = test_key_exchange()
print(f'Key exchange test: {\"PASS\" if result else \"FAIL\"}')"

# Test Kyber KEM
python -c "
from src.key_exchange import test_kyber_kem
result = test_kyber_kem()
print(f'Kyber KEM test: {\"PASS\" if result else \"FAIL\"}')"

# Test ECDH
python -c "
from src.key_exchange import test_ecdh
result = test_ecdh()
print(f'ECDH test: {\"PASS\" if result else \"FAIL\"}')"

# Test hybrid exchange
python -c "
from src.key_exchange import test_hybrid_exchange
result = test_hybrid_exchange()
print(f'Hybrid exchange test: {\"PASS\" if result else \"FAIL\"}')"
```

#### Validate Cryptographic Integrity

```bash
# Run self-tests
python -c "from src.key_exchange import run_self_tests; run_self_tests()"

# Verify algorithm parameters
python -c "from src.key_exchange import verify_algorithm_params; verify_algorithm_params()"

# Check for known vulnerabilities
python -c "from src.key_exchange import security_audit; security_audit()"

# Validate key strength
python -c "from src.key_exchange import validate_key_strength; validate_key_strength()"
```

#### Performance Testing

```bash
# Benchmark key exchange operations
python -c "
from src.key_exchange import benchmark_operations
import time

iterations = 1000
start = time.time()
benchmark_operations(iterations)
duration = time.time() - start
print(f'Throughput: {iterations/duration:.2f} operations/sec')
print(f'Average latency: {duration/iterations*1000:.2f}ms')"

# Benchmark Kyber operations
python scripts/benchmark-kyber.py

# Benchmark ECDH operations
python scripts/benchmark-ecdh.py

# Load testing
ab -n 1000 -c 10 http://localhost:8000/api/key-exchange
```

---

## Incident Response

### Detection

**Automated Detection:**

- Service health check failures
- Cryptographic validation failures
- High error rates in logs
- Performance degradation alerts
- Memory leak detection

**Manual Detection:**

```bash
# Check service health
systemctl status quantum-crypto.service

# Check for errors
journalctl -u quantum-crypto.service --since "1 hour ago" | grep -i "error\|critical\|failed"

# Check performance metrics
curl -s http://localhost:8000/metrics | grep -E "latency|error_rate|throughput"

# Check key integrity
python -c "from src.key_exchange import verify_keys; verify_keys()"

# Check memory leaks
ps aux | grep key_exchange.py | awk '{print $6}'
```

### Triage

#### Severity Classification

### P0: Critical Security Incident

- Cryptographic validation failure
- Key corruption or compromise
- Service completely down
- Security audit failures
- Known vulnerability detected

### P1: Service Degradation

- High error rate (>1%)
- Severe performance degradation (>500ms latency)
- Key rotation failures
- Memory leaks causing OOM
- Partial service unavailability

### P2: Warning State

- Elevated error rate (0.1-1%)
- Moderate performance degradation (100-500ms)
- Old keys (>7 days)
- High resource usage (>80%)
- Non-critical validation warnings

### P3: Informational

- Occasional errors (<0.1%)
- Minor performance variations
- Routine maintenance needed
- Low resource usage changes

### Incident Response Procedures

#### P0: Cryptographic Validation Failure

**Immediate Actions (0-5 minutes):**

```bash
# 1. STOP THE SERVICE IMMEDIATELY
sudo systemctl stop quantum-crypto.service

# 2. Verify validation failure
python -c "from src.key_exchange import run_self_tests; run_self_tests()"

# 3. Check for key corruption
python -c "from src.key_exchange import verify_keys; verify_keys()"

# 4. Check service logs for details
journalctl -u quantum-crypto.service --since "1 hour ago" | grep -i "validation\|error"

# 5. Isolate affected keys
mkdir -p /var/lib/quantum-crypto/quarantine/$(date +%Y%m%d-%H%M)
mv /var/lib/quantum-crypto/keys/* /var/lib/quantum-crypto/quarantine/$(date +%Y%m%d-%H%M)/
```

**Investigation (5-30 minutes):**

```bash
# Analyze corrupted keys
python scripts/analyze-keys.py /var/lib/quantum-crypto/quarantine/$(date +%Y%m%d)*

# Check for filesystem corruption
fsck -n /var/lib/quantum-crypto/

# Check system integrity
aide --check

# Review recent changes
git log --since="24 hours ago" --oneline

# Check for malicious activity
grep -i "unauthorized\|intrusion" /var/log/auth.log
```

**Recovery:**

```bash
# Restore keys from last known good backup
LAST_BACKUP=$(ls -t /backup/quantum-crypto/keys/ | head -1)
cp -r /backup/quantum-crypto/keys/$LAST_BACKUP/* /var/lib/quantum-crypto/keys/

# Verify restored keys
python -c "from src.key_exchange import verify_keys; verify_keys()"

# Run comprehensive self-tests
python -c "from src.key_exchange import run_self_tests; run_self_tests()"

# Generate new keys if backup compromised
python -c "from src.key_exchange import generate_hybrid_keypair; generate_hybrid_keypair()"

# Restart service
sudo systemctl start quantum-crypto.service

# Verify service health
curl http://localhost:8000/health

# Document incident
cat > /var/log/quantum-crypto/incident-$(date +%Y%m%d-%H%M).txt << EOF
Incident: Cryptographic validation failure
Time: $(date)
Action: Restored from backup: $LAST_BACKUP
Status: Service recovered
Next steps: Security audit, review logs, update monitoring
EOF
```

#### P0: Service Down

**Immediate Actions (0-2 minutes):**

```bash
# 1. Check service status
systemctl status quantum-crypto.service

# 2. Attempt restart
sudo systemctl restart quantum-crypto.service

# 3. Check if restart successful
sleep 5
systemctl is-active quantum-crypto.service

# 4. If still down, check logs
journalctl -u quantum-crypto.service -n 100 --no-pager
```

**Investigation (2-10 minutes):**

```bash
# Check for Python errors
journalctl -u quantum-crypto.service | grep -i "traceback\|exception"

# Check dependencies
cd /opt/quantum-crypto
source venv/bin/activate
pip check

# Check file permissions
ls -la /var/lib/quantum-crypto/keys/
ls -la /var/log/quantum-crypto/

# Check port availability
netstat -tlnp | grep 8000

# Check system resources
df -h /var/lib/quantum-crypto
free -h
```

**Recovery:**

```bash
# Fix dependency issues
cd /opt/quantum-crypto
source venv/bin/activate
pip install -r requirements.txt --force-reinstall

# Fix permissions
sudo chown -R quantum-crypto:quantum-crypto /var/lib/quantum-crypto
sudo chown -R quantum-crypto:quantum-crypto /var/log/quantum-crypto
sudo chmod 700 /var/lib/quantum-crypto/keys

# Kill conflicting processes
sudo pkill -9 -f key_exchange.py
sleep 2

# Start service
sudo systemctl start quantum-crypto.service

# Verify
curl http://localhost:8000/health
```

#### P1: High Error Rate

**Investigation:**

```bash
# Analyze error patterns
journalctl -u quantum-crypto.service --since "1 hour ago" | \
  grep ERROR | awk '{print $NF}' | sort | uniq -c | sort -rn

# Check input validation errors
grep "validation.*failed" /var/log/quantum-crypto/service.log | tail -20

# Check for resource exhaustion
top -b -n 1 | head -20
free -h

# Check for network issues
netstat -s | grep -i error
```

**Remediation:**

```bash
# If input validation issues, check API clients
# Review recent API changes

# If resource issues, restart service
sudo systemctl restart quantum-crypto.service

# If persistent errors, rollback to last known good version
git log --oneline -n 5
git checkout <last-good-commit>
pip install -r requirements.txt
sudo systemctl restart quantum-crypto.service

# Monitor error rate
watch -n 5 'journalctl -u quantum-crypto.service --since "5 minutes ago" | grep -c ERROR'
```

#### P1: Key Rotation Failed

**Investigation:**

```bash
# Check rotation logs
journalctl -u quantum-crypto.service | grep -i "rotation"

# Check disk space
df -h /var/lib/quantum-crypto

# Check file locks
lsof | grep quantum-crypto

# Check key generation
python -c "from src.key_exchange import generate_kyber_keypair; generate_kyber_keypair()"
```

**Manual Rotation:**

```bash
# Stop service
sudo systemctl stop quantum-crypto.service

# Backup current keys
cp -r /var/lib/quantum-crypto/keys /var/lib/quantum-crypto/keys.backup.$(date +%Y%m%d-%H%M)

# Generate new keys
python -c "
from src.key_exchange import generate_hybrid_keypair
generate_hybrid_keypair()"

# Verify new keys
python -c "from src.key_exchange import verify_keys; verify_keys()"

# Start service
sudo systemctl start quantum-crypto.service

# Verify rotation
python -c "from src.key_exchange import get_key_age; print(f'Key age: {get_key_age()} hours')"
```

#### P2: High Latency

**Investigation:**

```bash
# Profile key exchange operations
python -c "
import cProfile
from src.key_exchange import test_key_exchange
cProfile.run('test_key_exchange()', sort='cumtime')"

# Check CPU usage
top -b -n 3 -d 1 | grep key_exchange

# Check I/O wait
iostat -x 1 3

# Check memory
free -h
cat /proc/$(pgrep -f key_exchange.py)/status | grep -i vm
```

**Optimization:**

```bash
# Restart service to clear memory
sudo systemctl restart quantum-crypto.service

# Optimize Python garbage collection
export PYTHONOPTIMIZE=1
sudo systemctl restart quantum-crypto.service

# Scale resources if needed
# Update systemd service file with resource limits

# Consider caching frequently used operations
# Review code for optimization opportunities
```

### Post-Incident

**After Resolution:**

```bash
# Document incident
cat > /var/log/quantum-crypto/incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Cryptographic Service Incident Report

**Date:** $(date)
**Severity:** P1
**Duration:** 20 minutes
**Component:** Key Exchange Service

## Timeline
- 14:00: High error rate detected
- 14:05: Service degradation confirmed
- 14:10: Root cause identified (key corruption)
- 14:15: Keys restored from backup
- 14:20: Service fully recovered

## Root Cause
Key file corruption due to disk write failure

## Mitigation
- Restored keys from hourly backup
- Verified cryptographic integrity
- Restarted service

## Action Items
- [ ] Implement disk health monitoring
- [ ] Add key integrity checksums
- [ ] Increase backup frequency
- [ ] Add automated corruption detection
- [ ] Review filesystem reliability

EOF

# Update monitoring
# Add new alerts based on incident learnings

# Security audit
python -c "from src.key_exchange import security_audit; security_audit()"
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: "ImportError: No module named 'pqcrypto'"

**Symptoms:**

```bash
$ python src/key_exchange.py
ImportError: No module named 'pqcrypto'
```

**Diagnosis:**

```bash
# Check Python environment
which python
python --version

# Check installed packages
pip list | grep pqcrypto

# Check virtual environment
echo $VIRTUAL_ENV
```

**Solution:**

```bash
# Activate virtual environment
cd /opt/quantum-crypto
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import pqcrypto; print(pqcrypto.__version__)"

# Or recreate virtual environment
deactivate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

#### Issue: "KeyError: Key file not found"

**Symptoms:**

```bash
KeyError: '/var/lib/quantum-crypto/keys/kyber_private.key'
```

**Diagnosis:**

```bash
# Check key files
ls -la /var/lib/quantum-crypto/keys/

# Check permissions
ls -ld /var/lib/quantum-crypto/keys/

# Check service user
id quantum-crypto
```

**Solution:**

```bash
# Generate missing keys
python -c "from src.key_exchange import generate_hybrid_keypair; generate_hybrid_keypair()"

# Or restore from backup
cp /backup/quantum-crypto/keys/latest/* /var/lib/quantum-crypto/keys/

# Fix permissions
sudo chown -R quantum-crypto:quantum-crypto /var/lib/quantum-crypto/keys
sudo chmod 700 /var/lib/quantum-crypto/keys
sudo chmod 600 /var/lib/quantum-crypto/keys/*

# Verify
ls -la /var/lib/quantum-crypto/keys/
```

---

#### Issue: High Memory Usage

**Symptoms:**

- Service consuming >1GB RAM
- OOMKiller terminating process
- Slow performance

**Diagnosis:**

```bash
# Check memory usage
ps aux | grep key_exchange.py

# Check for memory leaks
python -m memory_profiler src/key_exchange.py

# Monitor over time
watch -n 5 'ps aux | grep key_exchange'
```

**Solution:**

```bash
# Restart service
sudo systemctl restart quantum-crypto.service

# Add memory limits
sudo vim /etc/systemd/system/quantum-crypto.service
# Add: MemoryLimit=512M

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart quantum-crypto.service

# Review code for memory leaks
# Check for unclosed file handles
# Verify proper cleanup of cryptographic objects
```

---

#### Issue: Cryptographic Test Failures

**Symptoms:**

```bash
$ python -c "from src.key_exchange import run_self_tests; run_self_tests()"
AssertionError: Decryption failed
```

**Diagnosis:**

```bash
# Check algorithm compatibility
python -c "from src.key_exchange import verify_algorithm_params; verify_algorithm_params()"

# Check library versions
pip list | grep -E "pqcrypto|cryptography|ecdsa"

# Check key integrity
python -c "from src.key_exchange import verify_keys; verify_keys()"
```

**Solution:**

```bash
# Update cryptographic libraries
pip install --upgrade pqcrypto cryptography

# Regenerate keys if incompatible
sudo systemctl stop quantum-crypto.service
python -c "from src.key_exchange import generate_hybrid_keypair; generate_hybrid_keypair()"

# Verify tests pass
python -c "from src.key_exchange import run_self_tests; run_self_tests()"

# Restart service
sudo systemctl start quantum-crypto.service
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 1 hour (hourly key backups)
- **RTO** (Recovery Time Objective): 15 minutes (service restoration)

### Backup Strategy

**Automated Key Backups:**

```bash
# Hourly backup cron job
cat > /etc/cron.hourly/quantum-crypto-backup << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/quantum-crypto/keys/$(date +%Y%m%d-%H00)"
mkdir -p $BACKUP_DIR
cp -r /var/lib/quantum-crypto/keys/* $BACKUP_DIR/
tar czf $BACKUP_DIR.tar.gz -C $BACKUP_DIR .
rm -rf $BACKUP_DIR
find /backup/quantum-crypto/keys/ -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x /etc/cron.hourly/quantum-crypto-backup

# Test backup
/etc/cron.hourly/quantum-crypto-backup
ls -lh /backup/quantum-crypto/keys/
```

**Offsite Backup:**

```bash
# Daily offsite backup
cat > /etc/cron.daily/quantum-crypto-offsite << 'EOF'
#!/bin/bash
BACKUP_FILE="/backup/quantum-crypto/keys-$(date +%Y%m%d).tar.gz.gpg"
tar czf - /var/lib/quantum-crypto/keys/ | \
  gpg --symmetric --cipher-algo AES256 > $BACKUP_FILE

aws s3 cp $BACKUP_FILE s3://crypto-backups/quantum-safe/ --sse

find /backup/quantum-crypto/ -name "keys-*.tar.gz.gpg" -mtime +30 -delete
EOF

chmod +x /etc/cron.daily/quantum-crypto-offsite
```

**Configuration Backup:**

```bash
# Backup service configuration
git add src/ requirements.txt scripts/
git commit -m "backup: quantum-crypto configuration $(date +%Y-%m-%d)"
git push origin main
```

### Disaster Recovery Procedures

#### Complete Service Loss

**Recovery Steps (10-15 minutes):**

```bash
# 1. Restore code from Git
cd /opt
git clone https://github.com/org/quantum-crypto.git
cd quantum-crypto

# 2. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Restore keys from backup
LATEST_BACKUP=$(ls -t /backup/quantum-crypto/keys/*.tar.gz | head -1)
mkdir -p /var/lib/quantum-crypto/keys
tar xzf $LATEST_BACKUP -C /var/lib/quantum-crypto/keys/

# 4. Verify keys
python -c "from src.key_exchange import verify_keys; verify_keys()"

# 5. Setup systemd service
sudo cp scripts/quantum-crypto.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable quantum-crypto.service
sudo systemctl start quantum-crypto.service

# 6. Verify service
curl http://localhost:8000/health
python -c "from src.key_exchange import run_self_tests; run_self_tests()"
```

#### Key Compromise

**Emergency Response:**

```bash
# 1. IMMEDIATELY stop service
sudo systemctl stop quantum-crypto.service

# 2. Quarantine compromised keys
mkdir -p /var/lib/quantum-crypto/compromised/$(date +%Y%m%d-%H%M)
mv /var/lib/quantum-crypto/keys/* /var/lib/quantum-crypto/compromised/$(date +%Y%m%d-%H%M)/

# 3. Generate new keys
python -c "from src.key_exchange import generate_hybrid_keypair; generate_hybrid_keypair()"

# 4. Verify new keys
python -c "from src.key_exchange import verify_keys; verify_keys()"
python -c "from src.key_exchange import run_self_tests; run_self_tests()"

# 5. Restart service
sudo systemctl start quantum-crypto.service

# 6. Notify stakeholders
echo "Key rotation completed at $(date)" | mail -s "URGENT: Crypto key rotation" security-team@company.com

# 7. Document incident
# Follow post-incident procedures
```

---

## Maintenance Procedures

### Daily Tasks

```bash
# Check service health
systemctl status quantum-crypto.service

# Check for errors
journalctl -u quantum-crypto.service --since "24 hours ago" | grep -c ERROR

# Verify cryptographic self-tests
python -c "from src.key_exchange import run_self_tests; run_self_tests()"

# Check key age
python -c "from src.key_exchange import get_key_age; print(f'Key age: {get_key_age()} hours')"

# Check disk usage
df -h /var/lib/quantum-crypto
```

### Weekly Tasks

```bash
# Review logs for anomalies
journalctl -u quantum-crypto.service --since "7 days ago" | less

# Check performance metrics
python scripts/performance-report.py

# Update dependencies
cd /opt/quantum-crypto
source venv/bin/activate
pip list --outdated

# Verify backups
ls -lh /backup/quantum-crypto/keys/ | tail -10

# Test key restoration
# (in test environment)
```

### Monthly Tasks

```bash
# Rotate keys
python -c "from src.key_exchange import rotate_keys; rotate_keys()"

# Update cryptographic libraries
pip install --upgrade pqcrypto cryptography
sudo systemctl restart quantum-crypto.service

# Security audit
python -c "from src.key_exchange import security_audit; security_audit()"

# Review and test DR procedures
# Follow DR drill procedures

# Update documentation
git pull
# Review and update this runbook
```

---

## Quick Reference

### Most Common Operations

```bash
# Check service status
systemctl status quantum-crypto.service

# Restart service
sudo systemctl restart quantum-crypto.service

# View logs
journalctl -u quantum-crypto.service -f

# Test key exchange
python -c "from src.key_exchange import test_key_exchange; test_key_exchange()"

# Rotate keys
python -c "from src.key_exchange import rotate_keys; rotate_keys()"

# Backup keys
cp -r /var/lib/quantum-crypto/keys /backup/quantum-crypto/keys-$(date +%Y%m%d)

# Run self-tests
python -c "from src.key_exchange import run_self_tests; run_self_tests()"
```

### Emergency Response

```bash
# P0: Cryptographic failure
sudo systemctl stop quantum-crypto.service
python -c "from src.key_exchange import verify_keys; verify_keys()"
# Restore from backup or regenerate keys

# P0: Service down
sudo systemctl restart quantum-crypto.service
journalctl -u quantum-crypto.service -n 100

# P1: High error rate
journalctl -u quantum-crypto.service | grep ERROR | tail -50
sudo systemctl restart quantum-crypto.service

# P1: Key rotation failed
sudo systemctl stop quantum-crypto.service
python -c "from src.key_exchange import generate_hybrid_keypair; generate_hybrid_keypair()"
sudo systemctl start quantum-crypto.service
```

---

**Document Metadata:**

- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Security Engineering Team
- **Review Schedule:** Monthly or after security incidents
- **Feedback:** Create issue or submit PR with updates
