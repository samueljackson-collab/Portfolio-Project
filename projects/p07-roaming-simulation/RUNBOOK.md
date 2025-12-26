# Runbook — P07 (International Roaming Test Simulation)

## Overview

Production operations runbook for the telecom roaming test simulation framework. This runbook covers HLR/HSS operations, state machine management, test scenario execution, subscriber database maintenance, and troubleshooting procedures for mobile network roaming simulations.

**System Components:**
- Mock HLR/HSS (Home Location Register / Home Subscriber Server)
- Mock VLR/MME (Visitor Location Register / Mobility Management Entity)
- Subscriber database (SQLite)
- State machine engine (idle, attached, roaming, detached)
- SS7 MAP/Diameter protocol simulator
- Test runner and scenario engine
- Billing trigger simulator

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Successful roaming rate** | 95% | Successful auth / Total attempts |
| **State transition latency** | < 100ms | Time for state change |
| **HLR query response time** | < 50ms | Database query latency |
| **Location update success** | 98% | Successful LU / Total LU attempts |
| **Authentication success rate** | 99% | Valid IMSI auth / Total auth |
| **Test scenario pass rate** | 90% | Passing scenarios / Total scenarios |

---

## Dashboards & Alerts

### Dashboards

#### Roaming Status Dashboard
```bash
# Check overall simulation status
python src/simulator.py --status

# View active subscribers
sqlite3 data/subscribers.db "SELECT imsi, state, visited_mcc_mnc FROM subscribers WHERE state='roaming';"

# Check location updates
tail -f logs/state_transitions.log

# HLR query statistics
grep "HLR Query" logs/hlr_queries.log | wc -l
```

#### Subscriber Database Dashboard
```bash
# Count subscribers by state
sqlite3 data/subscribers.db << 'EOF'
SELECT state, COUNT(*) as count
FROM subscribers
GROUP BY state
ORDER BY count DESC;
EOF

# View failed authentication attempts
sqlite3 data/subscribers.db "SELECT imsi, last_error FROM subscribers WHERE last_error IS NOT NULL;"

# Check roaming agreements
cat config/roaming.yaml | grep -A 10 "roaming_agreements"
```

#### Performance Metrics Dashboard
```bash
# Parse simulation logs for metrics
cat logs/simulation.log | jq -r 'select(.event == "location_update") | .duration' | \
  awk '{sum+=$1; count++} END {print "Avg LU time:", sum/count, "ms"}'

# Count events by type
cat logs/simulation.log | jq -r '.event' | sort | uniq -c

# Success vs failure rate
cat logs/simulation.log | jq -r 'select(.result != null) | .result' | \
  awk '{total++; if($1=="success") success++} END {print "Success rate:", (success/total)*100 "%"}'
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | HLR/HSS database down | Immediate | Restart database, check connectivity |
| **P1** | Auth success rate < 80% | 30 minutes | Check HLR queries, verify test data |
| **P1** | State machine deadlock | 30 minutes | Restart simulator, investigate state |
| **P2** | High latency (> 200ms) | 2 hours | Check database performance |
| **P2** | Failed test scenarios > 20% | 4 hours | Review test data, fix scenarios |
| **P3** | Missing roaming agreement | 24 hours | Update configuration |

#### Alert Queries

**Check authentication failures:**
```bash
# Count auth failures in last hour
sqlite3 data/subscribers.db << 'EOF'
SELECT COUNT(*) as auth_failures
FROM subscribers
WHERE last_error LIKE '%auth%failed%'
  AND updated_at > datetime('now', '-1 hour');
EOF

# Alert if > 10
[ $auth_failures -gt 10 ] && echo "ALERT: High auth failure rate"
```

**Monitor state machine health:**
```bash
# Check for stuck subscribers (same state > 10 min)
sqlite3 data/subscribers.db << 'EOF'
SELECT imsi, state, updated_at
FROM subscribers
WHERE state = 'authenticating'
  AND updated_at < datetime('now', '-10 minutes');
EOF
```

---

## Standard Operations

### Simulation Management

#### Start Simulation
```bash
# Full simulation run
make run-simulation

# Or manually
python src/simulator.py --scenario international_roaming

# Fast mode (reduced delays)
python src/simulator.py --mode fast

# Single subscriber test
python src/simulator.py --mode single --imsi 310410123456789
```

#### Stop Simulation
```bash
# Graceful shutdown
pkill -SIGTERM -f "simulator.py"

# Or use Ctrl+C if running in foreground

# Force kill if unresponsive
pkill -SIGKILL -f "simulator.py"

# Verify stopped
ps aux | grep simulator.py
```

#### Monitor Simulation
```bash
# Watch state transitions in real-time
tail -f logs/state_transitions.log

# Monitor HLR queries
tail -f logs/hlr_queries.log

# Watch all simulation events
tail -f logs/simulation.log | jq '.'
```

### Subscriber Database Management

#### View Subscribers
```bash
# List all subscribers
sqlite3 data/subscribers.db "SELECT * FROM subscribers LIMIT 10;"

# Check specific subscriber
sqlite3 data/subscribers.db "SELECT * FROM subscribers WHERE imsi='310410123456789';"

# Count by state
sqlite3 data/subscribers.db << 'EOF'
SELECT state, COUNT(*)
FROM subscribers
GROUP BY state;
EOF
```

#### Add Test Subscriber
```bash
# Add single subscriber
sqlite3 data/subscribers.db << 'EOF'
INSERT INTO subscribers (imsi, msisdn, home_mcc_mnc, state, ki)
VALUES ('310410987654321', '14155551234', '310-410', 'idle', 'A1B2C3D4E5F6789012345678901234');
EOF

# Verify
sqlite3 data/subscribers.db "SELECT * FROM subscribers WHERE imsi='310410987654321';"
```

#### Reset Subscriber State
```bash
# Reset specific subscriber to idle
sqlite3 data/subscribers.db << 'EOF'
UPDATE subscribers
SET state = 'idle',
    visited_mcc_mnc = NULL,
    last_error = NULL
WHERE imsi = '310410123456789';
EOF

# Reset all subscribers
sqlite3 data/subscribers.db << 'EOF'
UPDATE subscribers
SET state = 'idle',
    visited_mcc_mnc = NULL,
    last_error = NULL;
EOF
```

#### Clean Up Database
```bash
# Remove failed subscribers
sqlite3 data/subscribers.db "DELETE FROM subscribers WHERE state = 'rejected';"

# Archive old records
sqlite3 data/subscribers.db << 'EOF'
CREATE TABLE IF NOT EXISTS subscribers_archive AS
SELECT * FROM subscribers WHERE updated_at < datetime('now', '-30 days');
DELETE FROM subscribers WHERE updated_at < datetime('now', '-30 days');
EOF

# Vacuum database
sqlite3 data/subscribers.db "VACUUM;"
```

### Test Execution

#### Run All Test Scenarios
```bash
# Full test suite
make test

# Or manually
pytest tests/ -v

# With coverage
pytest --cov=src --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html
```

#### Run Specific Test Scenarios
```bash
# Successful roaming scenario
pytest tests/test_roaming_success.py -v

# Failed authentication
pytest tests/test_auth_failure.py -v

# State machine tests
pytest tests/test_state_machine.py -v

# Specific test
pytest tests/test_roaming_success.py::test_successful_location_update -v
```

#### Debug Test Scenario
```bash
# Run with debug output
pytest tests/test_roaming_success.py -v -s

# Run with pdb debugger
pytest tests/test_roaming_success.py --pdb

# Run single test with logging
pytest tests/test_roaming_success.py::test_successful_location_update -v -s --log-cli-level=DEBUG
```

### Configuration Management

#### Update Roaming Agreements
```bash
# Edit roaming configuration
vi config/roaming.yaml

# Add new roaming partner
cat >> config/roaming.yaml << 'EOF'
roaming_agreements:
  - home_network: "310-410"  # AT&T
    visited_network: "234-15"  # Vodafone UK
    status: active
EOF

# Reload configuration
python src/simulator.py --reload-config
```

#### Update Network Codes
```bash
# Edit network code mappings
vi config/network_codes.yaml

# Add new MCC-MNC
cat >> config/network_codes.yaml << 'EOF'
networks:
  "310-410":
    operator: "AT&T"
    country: "United States"
    technology: "LTE/5G"
EOF
```

---

## Incident Response

### Detection

**Automated Detection:**
- Test scenario failures
- State machine timeout alerts
- Database connection errors

**Manual Detection:**
```bash
# Check recent errors
tail -100 logs/simulation.log | jq 'select(.level == "ERROR")'

# Check stuck subscribers
sqlite3 data/subscribers.db << 'EOF'
SELECT imsi, state, updated_at
FROM subscribers
WHERE updated_at < datetime('now', '-15 minutes')
  AND state != 'idle';
EOF

# Check test results
pytest tests/ --tb=no -q
```

### Triage

#### Severity Classification

**P0: Simulation System Down**
- HLR/HSS database unreachable
- State machine completely broken
- All tests failing (100%)

**P1: Critical Functionality Broken**
- Authentication failures > 50%
- Location updates failing
- State transitions not working
- Critical test scenarios failing

**P2: Degraded Performance**
- High latency (> 200ms)
- Some test scenarios failing (10-30%)
- State machine slow
- Missing roaming agreements

**P3: Minor Issues**
- Individual subscriber stuck
- Single test scenario failing
- Logging issues
- Configuration warnings

### Incident Response Procedures

#### P0: HLR Database Down

**Immediate Actions (0-5 minutes):**
```bash
# 1. Check database file exists
ls -lh data/subscribers.db

# 2. Check database is not locked
fuser data/subscribers.db

# 3. Test database connection
sqlite3 data/subscribers.db "SELECT COUNT(*) FROM subscribers;"

# 4. Check disk space
df -h data/

# 5. Stop simulation
pkill -f "simulator.py"
```

**Investigation (5-15 minutes):**
```bash
# Check for corruption
sqlite3 data/subscribers.db "PRAGMA integrity_check;"

# Check database size
ls -lh data/subscribers.db

# Review error logs
tail -100 logs/simulation.log | jq 'select(.level == "ERROR")'

# Check file permissions
ls -l data/subscribers.db
```

**Recovery:**
```bash
# Option 1: Repair database
sqlite3 data/subscribers.db << 'EOF'
PRAGMA integrity_check;
VACUUM;
REINDEX;
EOF

# Option 2: Restore from backup
cp data/subscribers.db data/subscribers.db.corrupted
cp backups/subscribers-$(date +%Y%m%d).db data/subscribers.db

# Option 3: Recreate database
rm data/subscribers.db
python src/setup_db.py

# Verify and restart
sqlite3 data/subscribers.db "SELECT COUNT(*) FROM subscribers;"
python src/simulator.py --mode fast
```

#### P1: High Authentication Failure Rate

**Investigation:**
```bash
# 1. Check auth failure count
sqlite3 data/subscribers.db << 'EOF'
SELECT COUNT(*) as failures
FROM subscribers
WHERE last_error LIKE '%auth%'
  AND updated_at > datetime('now', '-1 hour');
EOF

# 2. View failed IMSIs
sqlite3 data/subscribers.db << 'EOF'
SELECT imsi, last_error
FROM subscribers
WHERE last_error LIKE '%auth%'
LIMIT 10;
EOF

# 3. Check HLR query logs
grep "AUTH_FAILURE" logs/hlr_queries.log | tail -20

# 4. Verify Ki (authentication keys)
sqlite3 data/subscribers.db "SELECT imsi, ki FROM subscribers LIMIT 5;"
```

**Common Causes & Fixes:**

**Invalid IMSI Format:**
```bash
# Check IMSI format (should be 15 digits)
sqlite3 data/subscribers.db << 'EOF'
SELECT imsi
FROM subscribers
WHERE LENGTH(imsi) != 15;
EOF

# Fix: Update invalid IMSIs
sqlite3 data/subscribers.db << 'EOF'
UPDATE subscribers
SET imsi = '310410' || SUBSTR('000000000' || imsi, -9)
WHERE LENGTH(imsi) < 15;
EOF
```

**Missing Roaming Agreement:**
```bash
# Check if visited network is in allowed list
cat config/roaming.yaml | grep -A 2 "visited_network: \"208-01\""

# Fix: Add roaming agreement
vi config/roaming.yaml
# Add network to roaming_agreements section

# Reload config
python src/simulator.py --reload-config
```

**Incorrect Authentication Keys:**
```bash
# Regenerate test keys
python src/generate_test_keys.py --output data/test_keys.csv

# Update subscriber keys
sqlite3 data/subscribers.db << 'EOF'
UPDATE subscribers
SET ki = (SELECT hex(randomblob(16)));
EOF
```

#### P1: State Machine Deadlock

**Investigation:**
```bash
# 1. Find stuck subscribers
sqlite3 data/subscribers.db << 'EOF'
SELECT imsi, state, updated_at,
       (julianday('now') - julianday(updated_at)) * 24 * 60 as minutes_stuck
FROM subscribers
WHERE state IN ('authenticating', 'location_update')
  AND updated_at < datetime('now', '-10 minutes');
EOF

# 2. Check state transition log
tail -100 logs/state_transitions.log | grep -E "authenticating|TIMEOUT"

# 3. Check for infinite loops
ps aux | grep simulator.py
# High CPU usage indicates possible loop
```

**Mitigation:**
```bash
# Option 1: Reset stuck subscribers
sqlite3 data/subscribers.db << 'EOF'
UPDATE subscribers
SET state = 'idle', last_error = 'State timeout - reset'
WHERE state IN ('authenticating', 'location_update')
  AND updated_at < datetime('now', '-10 minutes');
EOF

# Option 2: Restart simulator
pkill -SIGTERM -f "simulator.py"
sleep 5
python src/simulator.py --mode fast

# Option 3: Increase timeout in config
vi config/roaming.yaml
# Change: state_timeout: 300  # 5 minutes

# Verify resolution
sqlite3 data/subscribers.db "SELECT state, COUNT(*) FROM subscribers GROUP BY state;"
```

#### P2: Test Scenario Failures

**Investigation:**
```bash
# Run tests with verbose output
pytest tests/ -v --tb=short

# Check specific failure
pytest tests/test_roaming_success.py -v -s

# Review test logs
cat logs/test_output.log

# Check test data
sqlite3 data/subscribers.db "SELECT * FROM subscribers WHERE imsi LIKE '999%';"
```

**Common Fixes:**
```bash
# Fix: Reset test database
python tests/setup_test_db.py

# Fix: Update test expectations
vi tests/test_roaming_success.py
# Update expected state/values

# Fix: Regenerate test data
python src/generate_test_data.py --count 100

# Re-run tests
pytest tests/ -v
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Roaming Simulation Incident Report

**Date:** $(date)
**Severity:** P1
**Duration:** 30 minutes
**Affected Component:** Authentication system

## Timeline
- 14:00: Auth failure rate spiked to 60%
- 14:10: Identified missing roaming agreement for network 208-01
- 14:20: Added roaming agreement to config
- 14:30: Auth success rate restored to 98%

## Root Cause
New visited network (208-01) not in roaming agreements list

## Action Items
- [ ] Add validation for roaming agreements before simulation
- [ ] Alert when new MCC-MNC detected without agreement
- [ ] Document roaming agreement setup process

EOF

# Update metrics
cat logs/simulation.log | jq -r 'select(.event == "auth_failure")' | wc -l >> metrics/daily_failures.txt
```

---

## Monitoring & Troubleshooting

### Essential Troubleshooting Commands

#### Database Issues
```bash
# Check database integrity
sqlite3 data/subscribers.db "PRAGMA integrity_check;"

# Check table schema
sqlite3 data/subscribers.db ".schema subscribers"

# Export data for debugging
sqlite3 data/subscribers.db << 'EOF'
.headers on
.mode csv
.output debug_subscribers.csv
SELECT * FROM subscribers;
EOF

# Count records
sqlite3 data/subscribers.db "SELECT COUNT(*) FROM subscribers;"
```

#### State Machine Issues
```bash
# Trace state transitions
tail -f logs/state_transitions.log | grep <imsi>

# Check current state distribution
sqlite3 data/subscribers.db << 'EOF'
SELECT state, COUNT(*) as count,
       AVG(julianday('now') - julianday(updated_at)) * 24 * 60 as avg_minutes
FROM subscribers
GROUP BY state;
EOF

# Force state change (debug only)
sqlite3 data/subscribers.db << 'EOF'
UPDATE subscribers
SET state = 'idle'
WHERE imsi = '310410123456789';
EOF
```

#### Performance Issues
```bash
# Check query performance
sqlite3 data/subscribers.db << 'EOF'
.timer on
SELECT * FROM subscribers WHERE imsi = '310410123456789';
EOF

# Add indexes if missing
sqlite3 data/subscribers.db << 'EOF'
CREATE INDEX IF NOT EXISTS idx_imsi ON subscribers(imsi);
CREATE INDEX IF NOT EXISTS idx_state ON subscribers(state);
CREATE INDEX IF NOT EXISTS idx_updated ON subscribers(updated_at);
EOF

# Analyze query plan
sqlite3 data/subscribers.db << 'EOF'
EXPLAIN QUERY PLAN
SELECT * FROM subscribers WHERE state = 'roaming';
EOF
```

### Common Issues & Solutions

#### Issue: "No roaming agreement found"

**Symptoms:**
```bash
ERROR: Location update failed for IMSI 310410123456789
Reason: No roaming agreement between 310-410 and 208-01
```

**Diagnosis:**
```bash
# Check roaming agreements
cat config/roaming.yaml | grep -A 5 "roaming_agreements"

# Check visited network
echo "Visited: 208-01"
```

**Solution:**
```bash
# Add roaming agreement
vi config/roaming.yaml

# Add:
roaming_agreements:
  - home_network: "310-410"
    visited_network: "208-01"
    status: active

# Reload configuration
pkill -HUP -f "simulator.py"
```

---

#### Issue: State machine stuck in "authenticating"

**Symptoms:**
```bash
$ sqlite3 data/subscribers.db "SELECT state, COUNT(*) FROM subscribers GROUP BY state;"
authenticating|47
idle|3
```

**Diagnosis:**
```bash
# Check how long they've been stuck
sqlite3 data/subscribers.db << 'EOF'
SELECT imsi,
       (julianday('now') - julianday(updated_at)) * 24 * 60 as minutes_stuck
FROM subscribers
WHERE state = 'authenticating'
ORDER BY minutes_stuck DESC
LIMIT 5;
EOF

# Check HLR response logs
tail -50 logs/hlr_queries.log | grep -A 2 "AUTH_REQUEST"
```

**Solution:**
```bash
# Option 1: Increase timeout
vi config/roaming.yaml
# Change: authentication_timeout: 60  # seconds

# Option 2: Reset stuck subscribers
sqlite3 data/subscribers.db << 'EOF'
UPDATE subscribers
SET state = 'idle', last_error = 'Auth timeout'
WHERE state = 'authenticating'
  AND updated_at < datetime('now', '-5 minutes');
EOF

# Option 3: Check HLR mock is responding
python -c "from src.hlr import HLR; hlr = HLR(); print(hlr.query('310410123456789'))"
```

---

#### Issue: IMSI validation failures

**Symptoms:**
```bash
ERROR: Invalid IMSI format: 31041012345
Expected 15 digits, got 11
```

**Diagnosis:**
```bash
# Check IMSI lengths
sqlite3 data/subscribers.db << 'EOF'
SELECT LENGTH(imsi) as imsi_length, COUNT(*)
FROM subscribers
GROUP BY LENGTH(imsi);
EOF

# Find invalid IMSIs
sqlite3 data/subscribers.db "SELECT imsi FROM subscribers WHERE LENGTH(imsi) != 15;"
```

**Solution:**
```bash
# Fix: Pad short IMSIs with leading zeros
sqlite3 data/subscribers.db << 'EOF'
UPDATE subscribers
SET imsi = SUBSTR('000000000000000' || imsi, -15)
WHERE LENGTH(imsi) < 15;
EOF

# Or delete invalid subscribers
sqlite3 data/subscribers.db "DELETE FROM subscribers WHERE LENGTH(imsi) != 15;"

# Verify
sqlite3 data/subscribers.db "SELECT MIN(LENGTH(imsi)), MAX(LENGTH(imsi)) FROM subscribers;"
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 1 hour (database backups)
- **RTO** (Recovery Time Objective): 15 minutes (restore + restart)

### Backup Strategy

**Database Backups:**
```bash
# Daily backup
sqlite3 data/subscribers.db ".backup backups/subscribers-$(date +%Y%m%d).db"

# Compress old backups
gzip backups/subscribers-$(date -d '7 days ago' +%Y%m%d).db

# Clean up old backups (keep 30 days)
find backups/ -name "subscribers-*.db.gz" -mtime +30 -delete
```

**Configuration Backups:**
```bash
# Backup configuration
cp config/roaming.yaml backups/roaming-$(date +%Y%m%d).yaml
cp config/network_codes.yaml backups/network_codes-$(date +%Y%m%d).yaml

# Version control
git add config/
git commit -m "backup: roaming configuration $(date +%Y-%m-%d)"
```

### Disaster Recovery Procedures

#### Database Corruption

**Recovery Steps (10-15 minutes):**
```bash
# 1. Stop simulation
pkill -f "simulator.py"

# 2. Backup corrupted database
cp data/subscribers.db data/subscribers.db.corrupted-$(date +%Y%m%d)

# 3. Attempt repair
sqlite3 data/subscribers.db << 'EOF'
PRAGMA integrity_check;
VACUUM;
REINDEX;
EOF

# 4. If repair fails, restore from backup
cp backups/subscribers-$(date +%Y%m%d).db data/subscribers.db

# 5. Verify database
sqlite3 data/subscribers.db "SELECT COUNT(*) FROM subscribers;"
sqlite3 data/subscribers.db "PRAGMA integrity_check;"

# 6. Restart simulation
python src/simulator.py --mode fast

# 7. Verify functionality
pytest tests/test_state_machine.py -v
```

#### Complete Data Loss

**Recovery Steps (20-30 minutes):**
```bash
# 1. Recreate database schema
python src/setup_db.py

# 2. Generate new test data
python src/generate_test_data.py --count 1000

# 3. Verify database
sqlite3 data/subscribers.db "SELECT COUNT(*) FROM subscribers;"

# 4. Restore configuration
cp backups/roaming-latest.yaml config/roaming.yaml

# 5. Run tests to verify
pytest tests/ -v

# 6. Start simulation
python src/simulator.py --scenario international_roaming
```

---

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks
```bash
# Check simulation health
tail -20 logs/simulation.log

# Monitor auth success rate
sqlite3 data/subscribers.db << 'EOF'
SELECT
  COUNT(CASE WHEN state = 'roaming' THEN 1 END) as successful,
  COUNT(CASE WHEN state = 'rejected' THEN 1 END) as rejected
FROM subscribers;
EOF

# Backup database
sqlite3 data/subscribers.db ".backup backups/subscribers-$(date +%Y%m%d).db"
```

#### Weekly Tasks
```bash
# Run full test suite
pytest tests/ -v --cov=src

# Clean up old logs
find logs/ -name "*.log" -mtime +7 -delete

# Database maintenance
sqlite3 data/subscribers.db << 'EOF'
VACUUM;
ANALYZE;
EOF

# Review stuck subscribers
sqlite3 data/subscribers.db << 'EOF'
SELECT state, COUNT(*)
FROM subscribers
WHERE updated_at < datetime('now', '-1 day')
GROUP BY state;
EOF
```

#### Monthly Tasks
```bash
# Update test data
python src/generate_test_data.py --refresh

# Review and update roaming agreements
vi config/roaming.yaml

# Archive old backups
tar -czf archives/backups-$(date +%Y%m).tar.gz backups/
find backups/ -mtime +30 -delete

# Performance testing
time pytest tests/ -v
```

---

## Quick Reference

### Common Commands
```bash
# Run simulation
make run-simulation

# Run tests
make test

# Check database
sqlite3 data/subscribers.db "SELECT state, COUNT(*) FROM subscribers GROUP BY state;"

# View logs
tail -f logs/simulation.log

# Reset database
sqlite3 data/subscribers.db "UPDATE subscribers SET state='idle';"
```

### Emergency Response
```bash
# P0: Database down
sqlite3 data/subscribers.db "PRAGMA integrity_check;" || cp backups/subscribers-latest.db data/subscribers.db

# P1: High auth failures
vi config/roaming.yaml  # Add missing agreements

# P1: State machine stuck
sqlite3 data/subscribers.db "UPDATE subscribers SET state='idle' WHERE updated_at < datetime('now', '-10 minutes');"

# P2: Reset all subscribers
sqlite3 data/subscribers.db "UPDATE subscribers SET state='idle', visited_mcc_mnc=NULL, last_error=NULL;"
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Telecom Testing Team
- **Review Schedule:** Quarterly or after major protocol changes
- **Feedback:** Create issue or submit PR with updates

## Evidence & Verification

Verification summary: Evidence artifacts captured on 2025-11-14 to validate the quickstart configuration and document audit-ready supporting files.

**Evidence artifacts**
- [Screenshot](./docs/evidence/screenshot.svg)
- [Run log](./docs/evidence/run-log.txt)
- [Dashboard export](./docs/evidence/dashboard-export.json)
- [Load test summary](./docs/evidence/load-test-summary.txt)

### Evidence Checklist

| Evidence Item | Location | Status |
| --- | --- | --- |
| Screenshot captured | `docs/evidence/screenshot.svg` | ✅ |
| Run log captured | `docs/evidence/run-log.txt` | ✅ |
| Dashboard export captured | `docs/evidence/dashboard-export.json` | ✅ |
| Load test summary captured | `docs/evidence/load-test-summary.txt` | ✅ |
