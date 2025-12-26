# Runbook — P14 (Disaster Recovery Design)

## Overview

Production operations runbook for the P14 Disaster Recovery (DR) platform. This runbook covers backup operations, restore procedures, DR testing, failover processes, and business continuity planning for production systems with comprehensive RPO/RTO targets.

**System Components:**
- Automated backup scripts (databases, files, configurations)
- Multi-region backup storage (S3 with cross-region replication)
- Restore validation framework
- DR drill automation
- RPO/RTO monitoring and reporting
- Failover procedures and automation

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Backup success rate** | 99.9% | Successful backups / total backup attempts |
| **Backup completion time** | < 4 hours | Time from start to verified backup |
| **RPO (Database)** | 1 hour | Maximum data loss acceptable |
| **RPO (Files)** | 4 hours | Maximum data loss acceptable |
| **RPO (Configs)** | 24 hours | Maximum data loss acceptable |
| **RTO (Full recovery)** | 4 hours | Time to restore full production environment |
| **Restore validation rate** | 100% | Monthly restore test success rate |
| **DR drill success rate** | 95% | Quarterly DR drill completion rate |

---

## Dashboards & Alerts

### Dashboards

#### Backup Status Dashboard
```bash
# Check recent backup jobs
make backup-status

# Or manually check backup logs
ls -lh backup/logs/backup-*.log | tail -10

# Check S3 backup bucket
aws s3 ls s3://${BACKUP_BUCKET}/database/ --recursive --human-readable | tail -20

# Check backup age
echo "=== Database Backups ==="
aws s3 ls s3://${BACKUP_BUCKET}/database/ --recursive | \
  awk '{print $1" "$2" "$4}' | sort -r | head -5

echo "=== File Backups ==="
aws s3 ls s3://${BACKUP_BUCKET}/files/ --recursive | \
  awk '{print $1" "$2" "$4}' | sort -r | head -5

# Verify backup sizes
aws s3api list-objects-v2 \
  --bucket ${BACKUP_BUCKET} \
  --prefix database/ \
  --query 'sort_by(Contents, &LastModified)[-5:].{Key:Key,Size:Size,Modified:LastModified}' \
  --output table
```

#### RPO/RTO Metrics Dashboard
```bash
# Check current RPO (time since last backup)
cat > scripts/check-rpo.sh <<'EOF'
#!/bin/bash
BACKUP_BUCKET=${BACKUP_BUCKET:-"disaster-recovery-backups"}

echo "=== RPO Status ==="

# Database RPO (target: 1 hour)
LAST_DB_BACKUP=$(aws s3 ls s3://${BACKUP_BUCKET}/database/ --recursive | \
  awk '{print $1" "$2}' | sort -r | head -1)
LAST_DB_TIME=$(echo $LAST_DB_BACKUP | xargs -I {} date -d {} +%s)
CURRENT_TIME=$(date +%s)
DB_RPO_MINUTES=$(( (CURRENT_TIME - LAST_DB_TIME) / 60 ))
echo "Database RPO: ${DB_RPO_MINUTES} minutes (target: < 60 min)"
[ $DB_RPO_MINUTES -gt 60 ] && echo "WARNING: Database RPO exceeded!"

# Files RPO (target: 4 hours)
LAST_FILE_BACKUP=$(aws s3 ls s3://${BACKUP_BUCKET}/files/ --recursive | \
  awk '{print $1" "$2}' | sort -r | head -1)
LAST_FILE_TIME=$(echo $LAST_FILE_BACKUP | xargs -I {} date -d {} +%s)
FILE_RPO_HOURS=$(( (CURRENT_TIME - LAST_FILE_TIME) / 3600 ))
echo "Files RPO: ${FILE_RPO_HOURS} hours (target: < 4 hours)"
[ $FILE_RPO_HOURS -gt 4 ] && echo "WARNING: Files RPO exceeded!"

# Config RPO (target: 24 hours)
LAST_CONFIG_BACKUP=$(aws s3 ls s3://${BACKUP_BUCKET}/config/ --recursive | \
  awk '{print $1" "$2}' | sort -r | head -1)
LAST_CONFIG_TIME=$(echo $LAST_CONFIG_BACKUP | xargs -I {} date -d {} +%s)
CONFIG_RPO_HOURS=$(( (CURRENT_TIME - LAST_CONFIG_TIME) / 3600 ))
echo "Config RPO: ${CONFIG_RPO_HOURS} hours (target: < 24 hours)"
[ $CONFIG_RPO_HOURS -gt 24 ] && echo "WARNING: Config RPO exceeded!"
EOF
chmod +x scripts/check-rpo.sh

./scripts/check-rpo.sh
```

#### DR Site Status Dashboard
```bash
# Check DR region resources
aws ec2 describe-instances \
  --region ${DR_REGION} \
  --filters "Name=tag:Environment,Values=dr" \
  --query 'Reservations[].Instances[].{ID:InstanceId,State:State.Name,Type:InstanceType}' \
  --output table

# Check DR RDS instances
aws rds describe-db-instances \
  --region ${DR_REGION} \
  --query 'DBInstances[?TagList[?Key==`Environment` && Value==`dr`]].{ID:DBInstanceIdentifier,Status:DBInstanceStatus}' \
  --output table

# Check cross-region replication status
aws s3api get-bucket-replication \
  --bucket ${BACKUP_BUCKET} \
  --query 'ReplicationConfiguration.Rules[].{Destination:Destination.Bucket,Status:Status}'
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Backup failure for > 2 cycles | Immediate | Investigate and manual backup |
| **P0** | RPO exceeded by > 2x target | Immediate | Emergency backup, investigate issue |
| **P0** | DR site unavailable | Immediate | Investigate DR region connectivity |
| **P1** | Single backup job failure | 1 hour | Retry backup, investigate cause |
| **P1** | RPO warning (approaching limit) | 1 hour | Trigger manual backup |
| **P1** | Restore validation failure | 1 hour | Investigate backup integrity |
| **P2** | Backup duration exceeded | 4 hours | Optimize backup process |
| **P2** | Storage capacity warning | 4 hours | Clean old backups, increase capacity |
| **P3** | Minor backup delay | 24 hours | Monitor and investigate trend |

#### Alert Queries

```bash
# Check for backup failures in last 24 hours
grep -i "error\|failed" backup/logs/backup-$(date +%Y%m%d)*.log

# Check RPO status
./scripts/check-rpo.sh

# Check storage capacity
BUCKET_SIZE=$(aws s3 ls s3://${BACKUP_BUCKET} --recursive --summarize | \
  grep "Total Size" | awk '{print $3}')
echo "Backup bucket size: $(numfmt --to=iec-i --suffix=B $BUCKET_SIZE)"

# Check for stuck backup jobs
ps aux | grep -i "backup\|pg_dump\|mysqldump" | grep -v grep

# Check backup schedule compliance
cat > scripts/check-backup-schedule.sh <<'EOF'
#!/bin/bash
# Check if backups ran according to schedule
EXPECTED_DB_BACKUPS=24  # Hourly backups
EXPECTED_FILE_BACKUPS=6  # Every 4 hours

ACTUAL_DB=$(aws s3 ls s3://${BACKUP_BUCKET}/database/ --recursive | grep $(date +%Y-%m-%d) | wc -l)
ACTUAL_FILE=$(aws s3 ls s3://${BACKUP_BUCKET}/files/ --recursive | grep $(date +%Y-%m-%d) | wc -l)

echo "Database backups today: $ACTUAL_DB (expected: $EXPECTED_DB_BACKUPS)"
echo "File backups today: $ACTUAL_FILE (expected: $EXPECTED_FILE_BACKUPS)"

[ $ACTUAL_DB -lt $EXPECTED_DB_BACKUPS ] && echo "ALERT: Missing database backups"
[ $ACTUAL_FILE -lt $EXPECTED_FILE_BACKUPS ] && echo "ALERT: Missing file backups"
EOF
chmod +x scripts/check-backup-schedule.sh

./scripts/check-backup-schedule.sh
```

---

## Standard Operations

### Backup Operations

#### Database Backup
```bash
# Run manual database backup
make backup-database

# Or use script directly
./scripts/backup-database.sh

# Script performs:
# 1. Dumps PostgreSQL/MySQL database
# 2. Compresses backup
# 3. Encrypts backup (optional)
# 4. Uploads to S3
# 5. Validates upload
# 6. Logs results

# Check backup completion
tail -f backup/logs/backup-database-$(date +%Y%m%d).log

# Verify backup in S3
aws s3 ls s3://${BACKUP_BUCKET}/database/$(date +%Y-%m-%d)/ --human-readable

# Test backup integrity
./scripts/validate-backup.sh database backup-20251110-120000.sql.gz
```

#### File System Backup
```bash
# Run manual file system backup
make backup-files

# Or use script directly
./scripts/backup-files.sh

# Script performs:
# 1. Creates tarball of critical directories
# 2. Compresses backup
# 3. Uploads to S3
# 4. Validates upload
# 5. Logs results

# Check backup completion
tail -f backup/logs/backup-files-$(date +%Y%m%d).log

# Verify backup in S3
aws s3 ls s3://${BACKUP_BUCKET}/files/$(date +%Y-%m-%d)/ --human-readable
```

#### Configuration Backup
```bash
# Run manual configuration backup
make backup-config

# Or use script directly
./scripts/backup-config.sh

# Script backs up:
# - /etc/ system configs
# - Application configs
# - Environment files
# - Infrastructure as Code (Terraform, CloudFormation)
# - Docker compose files
# - Git repositories

# Check backup completion
tail -f backup/logs/backup-config-$(date +%Y%m%d).log
```

#### Full System Backup
```bash
# Run all backup types
make backup-all

# This runs in sequence:
# 1. Database backup
# 2. File system backup
# 3. Configuration backup
# 4. Validates all backups
# 5. Generates backup report

# View backup report
cat backup/logs/backup-report-$(date +%Y%m%d).txt
```

### Restore Operations

#### Restore Database
```bash
# List available database backups
aws s3 ls s3://${BACKUP_BUCKET}/database/ --recursive | tail -10

# Restore from specific backup
./scripts/restore-database.sh backup-20251110-120000.sql.gz

# Restore process:
# 1. Downloads backup from S3
# 2. Validates backup integrity
# 3. Stops application (to prevent writes)
# 4. Creates pre-restore snapshot
# 5. Restores database
# 6. Validates restore
# 7. Starts application

# Monitor restore progress
tail -f restore/logs/restore-database-$(date +%Y%m%d).log

# Verify restore
./scripts/validate-restore.sh database
```

#### Restore Files
```bash
# List available file backups
aws s3 ls s3://${BACKUP_BUCKET}/files/ --recursive | tail -10

# Restore from specific backup
./scripts/restore-files.sh backup-20251110-120000.tar.gz /restore/target/path

# Restore process:
# 1. Downloads backup from S3
# 2. Validates backup integrity
# 3. Extracts files to target location
# 4. Sets correct permissions
# 5. Validates restore

# Monitor restore progress
tail -f restore/logs/restore-files-$(date +%Y%m%d).log
```

#### Restore Configuration
```bash
# List available config backups
aws s3 ls s3://${BACKUP_BUCKET}/config/ --recursive | tail -10

# Restore from specific backup
./scripts/restore-config.sh backup-20251110-120000.tar.gz

# Restore process:
# 1. Downloads backup from S3
# 2. Validates backup integrity
# 3. Restores configs to correct locations
# 4. Applies correct permissions
# 5. Restarts affected services

# Monitor restore progress
tail -f restore/logs/restore-config-$(date +%Y%m%d).log
```

#### Point-in-Time Restore
```bash
# Restore database to specific timestamp
# Requires continuous archiving (WAL/binlog)

# PostgreSQL Point-in-Time Recovery (PITR)
./scripts/restore-pitr.sh "2025-11-10 12:00:00"

# MySQL Point-in-Time Recovery
./scripts/restore-binlog.sh "2025-11-10 12:00:00"

# Process:
# 1. Restores base backup
# 2. Applies transaction logs up to target time
# 3. Validates restore
```

### DR Site Management

#### Prepare DR Environment
```bash
# Deploy DR infrastructure
make setup-dr-site

# Script performs:
# 1. Creates DR region resources
# 2. Configures cross-region replication
# 3. Deploys minimal DR infrastructure
# 4. Sets up monitoring
# 5. Validates DR readiness

# Check DR site status
./scripts/check-dr-status.sh
```

#### Sync to DR Site
```bash
# Sync latest backups to DR site
make sync-dr-site

# Script performs:
# 1. Syncs S3 backups to DR region
# 2. Syncs database snapshots
# 3. Syncs AMIs/images
# 4. Validates sync completion

# Check sync status
aws s3 ls s3://${BACKUP_BUCKET}-${DR_REGION}/database/ --region ${DR_REGION} | tail -10
```

#### Activate DR Site (Failover)
```bash
# CAUTION: This activates DR site for production traffic!

# Full failover procedure
make activate-dr-site

# Script performs:
# 1. Verifies DR site is ready
# 2. Updates DNS/load balancers to point to DR
# 3. Activates DR databases
# 4. Starts DR application servers
# 5. Validates DR site is serving traffic
# 6. Monitors for issues

# Monitor failover
tail -f logs/failover-$(date +%Y%m%d).log

# Verify DR site is active
curl -I https://dr-site.example.com
```

#### Failback to Primary Site
```bash
# After primary site is recovered, failback

# Full failback procedure
make failback-to-primary

# Script performs:
# 1. Ensures primary site is fully recovered
# 2. Syncs data from DR to primary
# 3. Updates DNS/load balancers to point to primary
# 4. Deactivates DR site (standby mode)
# 5. Validates primary site is serving traffic
# 6. Monitors for issues

# Monitor failback
tail -f logs/failback-$(date +%Y%m%d).log
```

### Backup Management

#### List Backups
```bash
# List all database backups
aws s3 ls s3://${BACKUP_BUCKET}/database/ --recursive --human-readable

# List backups for specific date
aws s3 ls s3://${BACKUP_BUCKET}/database/2025-11-10/ --human-readable

# List recent backups (last 7 days)
aws s3api list-objects-v2 \
  --bucket ${BACKUP_BUCKET} \
  --prefix database/ \
  --query "Contents[?LastModified>='$(date -d '7 days ago' -u +%Y-%m-%d)'].[Key,Size,LastModified]" \
  --output table
```

#### Delete Old Backups
```bash
# Delete backups older than retention period
./scripts/cleanup-old-backups.sh

# Script performs:
# 1. Lists backups older than retention (default: 90 days)
# 2. Validates backups are eligible for deletion
# 3. Deletes old backups
# 4. Logs deletion

# Manual deletion of specific backup
aws s3 rm s3://${BACKUP_BUCKET}/database/old-backup.sql.gz

# Delete all backups for specific date (CAUTION!)
aws s3 rm s3://${BACKUP_BUCKET}/database/2025-01-01/ --recursive
```

#### Backup Retention Policy
```bash
# Configure lifecycle policies on S3 bucket
cat > backup-lifecycle.json <<'EOF'
{
  "Rules": [
    {
      "Id": "database-backup-retention",
      "Filter": {"Prefix": "database/"},
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ],
      "Expiration": {
        "Days": 365
      }
    },
    {
      "Id": "files-backup-retention",
      "Filter": {"Prefix": "files/"},
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        }
      ],
      "Expiration": {
        "Days": 180
      }
    }
  ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
  --bucket ${BACKUP_BUCKET} \
  --lifecycle-configuration file://backup-lifecycle.json
```

---

## Incident Response

### Detection

**Automated Detection:**
- Backup job failures
- RPO/RTO threshold breaches
- Storage capacity alerts
- DR site health check failures

**Manual Detection:**
```bash
# Check backup status
make backup-status

# Check RPO compliance
./scripts/check-rpo.sh

# Check recent backup logs
grep -i "error\|failed" backup/logs/*.log | tail -20

# Check backup schedule compliance
./scripts/check-backup-schedule.sh
```

### Triage

#### Severity Classification

### P0: Critical DR Failure
- Multiple consecutive backup failures
- RPO exceeded by > 2x target
- DR site completely unavailable
- Production disaster requiring immediate recovery

### P1: Degraded DR Capability
- Single backup type failure
- RPO warning (approaching limit)
- DR site partially available
- Restore validation failure

### P2: DR Warning State
- Backup delays
- Storage capacity warning
- Minor DR site issues
- Backup performance degradation

### P3: Informational
- Single backup retry succeeded
- Minor backup delays
- Routine maintenance notifications

### Incident Response Procedures

#### P0: Production Disaster - Initiate Full Recovery

**Immediate Actions (0-15 minutes):**
```bash
# 1. Declare disaster
echo "DISASTER DECLARED: $(date)" | tee logs/disaster-$(date +%Y%m%d-%H%M%S).log

# 2. Assemble DR team
# - Notify all stakeholders
# - Page on-call DR lead
# - Open war room / incident channel

# 3. Assess situation
# - What failed? (datacenter, region, specific services)
# - Is primary site recoverable?
# - What is the scope of the disaster?

# 4. Document decision to activate DR site
echo "Activating DR site at $(date)" | tee -a logs/disaster-$(date +%Y%m%d-%H%M%S).log
echo "Estimated RTO: 4 hours" | tee -a logs/disaster-$(date +%Y%m%d-%H%M%S).log

# 5. Start RTO timer
START_TIME=$(date +%s)
echo "Recovery started: $(date)" | tee -a logs/disaster-$(date +%Y%m%d-%H%M%S).log
```

**Recovery Execution (15 minutes - 4 hours):**
```bash
# 1. Verify DR site readiness
./scripts/check-dr-status.sh | tee -a logs/disaster-$(date +%Y%m%d-%H%M%S).log

# 2. Restore latest backups to DR site
echo "Restoring database..." | tee -a logs/disaster-$(date +%Y%m%d-%H%M%S).log
./scripts/restore-database.sh $(aws s3 ls s3://${BACKUP_BUCKET}-${DR_REGION}/database/ --region ${DR_REGION} | tail -1 | awk '{print $4}') --region ${DR_REGION}

echo "Restoring files..." | tee -a logs/disaster-$(date +%Y%m%d-%H%M%S).log
./scripts/restore-files.sh $(aws s3 ls s3://${BACKUP_BUCKET}-${DR_REGION}/files/ --region ${DR_REGION} | tail -1 | awk '{print $4}') --region ${DR_REGION}

echo "Restoring configs..." | tee -a logs/disaster-$(date +%Y%m%d-%H%M%S).log
./scripts/restore-config.sh $(aws s3 ls s3://${BACKUP_BUCKET}-${DR_REGION}/config/ --region ${DR_REGION} | tail -1 | awk '{print $4}') --region ${DR_REGION}

# 3. Start DR services
echo "Starting DR services..." | tee -a logs/disaster-$(date +%Y%m%d-%H%M%S).log
./scripts/start-dr-services.sh --region ${DR_REGION}

# 4. Validate services are operational
echo "Validating DR services..." | tee -a logs/disaster-$(date +%Y%m%d-%H%M%S).log
./scripts/validate-dr-services.sh --region ${DR_REGION}

# 5. Update DNS to point to DR site
echo "Updating DNS to DR site..." | tee -a logs/disaster-$(date +%Y%m%d-%H%M%S).log
./scripts/update-dns-to-dr.sh

# 6. Monitor DNS propagation
echo "Waiting for DNS propagation..." | tee -a logs/disaster-$(date +%Y%m%d-%H%M%S).log
for i in {1..60}; do
  DR_IP=$(dig +short example.com | head -1)
  echo "DNS resolves to: $DR_IP"
  sleep 10
done

# 7. Verify application is accessible
echo "Testing application..." | tee -a logs/disaster-$(date +%Y%m%d-%H%M%S).log
curl -f https://example.com/health || echo "WARNING: Health check failed"

# 8. Calculate RTO
END_TIME=$(date +%s)
RTO_SECONDS=$((END_TIME - START_TIME))
RTO_MINUTES=$((RTO_SECONDS / 60))
echo "Recovery completed in $RTO_MINUTES minutes ($RTO_SECONDS seconds)" | tee -a logs/disaster-$(date +%Y%m%d-%H%M%S).log
echo "Target RTO: 240 minutes (4 hours)" | tee -a logs/disaster-$(date +%Y%m%d-%H%M%S).log

if [ $RTO_MINUTES -lt 240 ]; then
  echo "SUCCESS: RTO target met" | tee -a logs/disaster-$(date +%Y%m%d-%H%M%S).log
else
  echo "WARNING: RTO target exceeded" | tee -a logs/disaster-$(date +%Y%m%d-%H%M%S).log
fi
```

**Post-Recovery (4+ hours):**
```bash
# 9. Monitor DR site for stability
echo "Monitoring DR site..." | tee -a logs/disaster-$(date +%Y%m%d-%H%M%S).log
watch -n 60 './scripts/check-dr-health.sh'

# 10. Assess primary site damage
echo "Assessing primary site..." | tee -a logs/disaster-$(date +%Y%m%d-%H%M%S).log
# Document what failed and estimated recovery time

# 11. Plan for failback (when primary is recovered)
echo "Planning failback..." | tee -a logs/disaster-$(date +%Y%m%d-%H%M%S).log
# Schedule failback during maintenance window
# Prepare data sync from DR to primary

# 12. Update stakeholders
echo "Disaster recovery completed at $(date)" | tee -a logs/disaster-$(date +%Y%m%d-%H%M%S).log
# Send status update to all stakeholders
```

---

#### P0: Multiple Backup Failures

**Immediate Actions (0-30 minutes):**
```bash
# 1. Check backup logs
grep -i "error\|failed" backup/logs/backup-$(date +%Y%m%d)*.log

# 2. Check storage availability
df -h
aws s3 ls s3://${BACKUP_BUCKET}/ || echo "S3 bucket inaccessible!"

# 3. Check database connectivity
psql -h ${DB_HOST} -U ${DB_USER} -c "SELECT 1;" || echo "Database inaccessible!"

# 4. Check backup scripts
./scripts/backup-database.sh --dry-run

# 5. Emergency: Trigger manual backup
echo "Attempting emergency backup..."
./scripts/backup-all.sh --priority

# 6. Verify backup completion
aws s3 ls s3://${BACKUP_BUCKET}/database/ | tail -5
```

**Investigation (30 minutes - 2 hours):**
```bash
# Common causes:
# - Storage full
# - Database connection timeout
# - Permissions issues
# - Network connectivity
# - Backup script errors

# Check disk space
df -h /backup

# Check S3 permissions
aws s3api get-bucket-policy --bucket ${BACKUP_BUCKET}

# Check database permissions
psql -h ${DB_HOST} -U ${DB_USER} -c "\du"

# Test network connectivity
ping -c 5 ${DB_HOST}
telnet ${DB_HOST} 5432

# Review recent changes
git log --since="24 hours ago" --oneline
```

**Resolution:**
```bash
# Fix identified issue
# Then run backup verification
./scripts/backup-all.sh --verify

# Update monitoring
echo "Backup failure resolved at $(date)" >> logs/incident-$(date +%Y%m%d).log

# Schedule extra backup to catch up
crontab -e
# Add: */15 * * * * /path/to/scripts/backup-database.sh
```

---

#### P1: Restore Validation Failure

**Investigation:**
```bash
# 1. Identify which backup failed validation
cat restore/logs/validation-$(date +%Y%m%d).log

# 2. Download suspect backup
aws s3 cp s3://${BACKUP_BUCKET}/database/suspect-backup.sql.gz /tmp/

# 3. Test backup integrity
gunzip -t /tmp/suspect-backup.sql.gz || echo "Backup corrupted!"

# 4. If corrupted, try previous backup
PREV_BACKUP=$(aws s3 ls s3://${BACKUP_BUCKET}/database/ | tail -2 | head -1 | awk '{print $4}')
echo "Testing previous backup: $PREV_BACKUP"
./scripts/validate-backup.sh database $PREV_BACKUP
```

**Resolution:**
```bash
# If backup is corrupted, trigger new backup
./scripts/backup-database.sh --force

# Update backup validation frequency
# Increase to daily validation instead of weekly

# Document incident
cat > logs/backup-corruption-$(date +%Y%m%d).md <<EOF
# Backup Corruption Incident

**Date:** $(date)
**Affected Backup:** suspect-backup.sql.gz
**Root Cause:** [Document root cause]
**Resolution:** [Document resolution]
**Action Items:**
- [ ] Increase validation frequency
- [ ] Review backup process
- [ ] Test restore procedure
EOF
```

---

## Monitoring & Troubleshooting

### Essential Troubleshooting Commands

#### Backup Troubleshooting
```bash
# Check backup process
ps aux | grep -i "backup\|pg_dump\|mysqldump"

# Check backup logs
tail -f backup/logs/backup-database-$(date +%Y%m%d).log

# Test database connectivity
psql -h ${DB_HOST} -U ${DB_USER} -c "SELECT version();"

# Test S3 connectivity
aws s3 ls s3://${BACKUP_BUCKET}/

# Check backup script syntax
bash -n scripts/backup-database.sh

# Run backup in debug mode
bash -x scripts/backup-database.sh
```

#### Restore Troubleshooting
```bash
# Check restore process
ps aux | grep -i "restore\|psql\|mysql"

# Check restore logs
tail -f restore/logs/restore-database-$(date +%Y%m%d).log

# Test backup download
aws s3 cp s3://${BACKUP_BUCKET}/database/test-backup.sql.gz /tmp/ --dryrun

# Test backup extraction
gunzip -t /tmp/test-backup.sql.gz

# Check database capacity
psql -h ${DB_HOST} -U ${DB_USER} -c "
SELECT pg_size_pretty(pg_database_size('postgres'));
"

# Check disk space for restore
df -h /restore
```

#### DR Site Troubleshooting
```bash
# Check DR region connectivity
aws ec2 describe-instances --region ${DR_REGION} --max-items 1

# Check cross-region replication
aws s3api get-bucket-replication --bucket ${BACKUP_BUCKET}

# Test DR site resources
./scripts/check-dr-status.sh

# Verify DNS configuration
dig example.com +short
dig dr-example.com +short

# Check DR site health
curl -I https://dr-example.com/health
```

### Common Issues & Solutions

#### Issue: Backup taking too long

**Symptoms:**
- Backup duration exceeds window
- Backup jobs overlapping

**Diagnosis:**
```bash
# Check backup duration
grep "Duration:" backup/logs/backup-database-*.log | tail -10

# Check database size
psql -h ${DB_HOST} -U ${DB_USER} -c "
SELECT pg_size_pretty(pg_database_size('appdb'));
"

# Check backup compression ratio
ls -lh backup/staging/ | tail -5
```

**Solution:**
```bash
# Option 1: Parallel dumps
pg_dump -j 4 -Fd -f /backup/staging/parallel-dump appdb

# Option 2: Incremental backups
# Use WAL archiving for PostgreSQL
# Use binary logs for MySQL

# Option 3: Optimize backup window
# Backup from replica instead of primary
# Schedule during low-traffic periods
```

---

#### Issue: Restore fails with "disk full"

**Symptoms:**
- Restore stops mid-way
- Disk space error in logs

**Diagnosis:**
```bash
# Check available disk space
df -h /restore

# Check backup size
aws s3api head-object \
  --bucket ${BACKUP_BUCKET} \
  --key database/backup.sql.gz \
  --query 'ContentLength' \
  --output text | numfmt --to=iec-i --suffix=B

# Estimate uncompressed size (usually 3-5x compressed)
```

**Solution:**
```bash
# Option 1: Free up space
du -sh /restore/* | sort -h | tail -10
rm -rf /restore/old-data

# Option 2: Restore to different volume
mkdir -p /mnt/large-volume/restore
./scripts/restore-database.sh backup.sql.gz /mnt/large-volume/restore

# Option 3: Stream restore (no disk needed)
aws s3 cp s3://${BACKUP_BUCKET}/database/backup.sql.gz - | \
  gunzip | \
  psql -h ${DB_HOST} -U ${DB_USER} appdb
```

---

## Disaster Recovery & Testing

### DR Drill Procedures

#### Monthly Restore Test (30 minutes)
```bash
# Test database restore without impacting production

# 1. Create test environment
./scripts/create-test-env.sh

# 2. Download latest backup
LATEST_BACKUP=$(aws s3 ls s3://${BACKUP_BUCKET}/database/ | tail -1 | awk '{print $4}')
echo "Testing restore of: $LATEST_BACKUP"

# 3. Restore to test database
./scripts/restore-database.sh $LATEST_BACKUP --target test-db

# 4. Validate restore
./scripts/validate-restore.sh test-db

# 5. Run data integrity checks
psql -h test-db -U ${DB_USER} -c "SELECT COUNT(*) FROM users;"
psql -h test-db -U ${DB_USER} -c "SELECT MAX(created_at) FROM transactions;"

# 6. Document results
cat > logs/restore-test-$(date +%Y%m%d).md <<EOF
# Monthly Restore Test

**Date:** $(date)
**Backup Tested:** $LATEST_BACKUP
**Result:** SUCCESS/FAILURE
**Duration:** X minutes
**Issues:** None / [Document any issues]
EOF

# 7. Cleanup test environment
./scripts/cleanup-test-env.sh
```

#### Quarterly DR Drill (4 hours)
```bash
# Full DR drill simulating complete disaster

# 1. Announce DR drill
echo "=== QUARTERLY DR DRILL ===" | tee logs/dr-drill-$(date +%Y%m%d).log
echo "Start time: $(date)" | tee -a logs/dr-drill-$(date +%Y%m%d).log

# 2. Simulate disaster (in non-prod environment)
echo "Simulating disaster..." | tee -a logs/dr-drill-$(date +%Y%m%d).log
./scripts/simulate-disaster.sh --env staging

# 3. Start RTO timer
START_TIME=$(date +%s)

# 4. Execute full DR procedure
echo "Activating DR site..." | tee -a logs/dr-drill-$(date +%Y%m%d).log
make activate-dr-site --env staging

# 5. Validate DR site
echo "Validating DR site..." | tee -a logs/dr-drill-$(date +%Y%m%d).log
./scripts/validate-dr-services.sh --env staging

# 6. Run application tests
echo "Running application tests..." | tee -a logs/dr-drill-$(date +%Y%m%d).log
./tests/smoke-tests.sh --env staging-dr

# 7. Calculate RTO
END_TIME=$(date +%s)
RTO_MINUTES=$(( (END_TIME - START_TIME) / 60 ))
echo "DR drill completed in $RTO_MINUTES minutes" | tee -a logs/dr-drill-$(date +%Y%m%d).log
echo "Target RTO: 240 minutes" | tee -a logs/dr-drill-$(date +%Y%m%d).log

# 8. Test failback
echo "Testing failback..." | tee -a logs/dr-drill-$(date +%Y%m%d).log
make failback-to-primary --env staging

# 9. Document lessons learned
cat > logs/dr-drill-report-$(date +%Y%m%d).md <<EOF
# Quarterly DR Drill Report

**Date:** $(date)
**Duration:** $RTO_MINUTES minutes
**RTO Target:** 240 minutes
**Result:** $([ $RTO_MINUTES -lt 240 ] && echo "SUCCESS" || echo "NEEDS IMPROVEMENT")

## What Went Well
- [Document successes]

## Issues Encountered
- [Document issues]

## Action Items
- [ ] [Action item 1]
- [ ] [Action item 2]

## Runbook Updates
- [Any updates needed to this runbook]
EOF

# 10. Cleanup
./scripts/cleanup-dr-drill.sh --env staging
```

---

## Maintenance Procedures

### Daily Tasks
```bash
# Check backup status
./scripts/check-rpo.sh

# Verify latest backups
aws s3 ls s3://${BACKUP_BUCKET}/database/ | tail -5

# Check for backup failures
grep -i "error\|failed" backup/logs/backup-$(date +%Y%m%d)*.log

# Monitor storage usage
aws s3 ls s3://${BACKUP_BUCKET}/ --recursive --summarize | grep "Total Size"
```

### Weekly Tasks
```bash
# Run restore validation test
./scripts/monthly-restore-test.sh

# Review backup logs
grep -i "warning\|error" backup/logs/*.log | wc -l

# Check backup retention compliance
./scripts/check-backup-retention.sh

# Verify DR site readiness
./scripts/check-dr-status.sh

# Review and archive old logs
mkdir -p logs/archive/$(date +%Y-%m)
mv logs/*.log logs/archive/$(date +%Y-%m)/ 2>/dev/null || true
```

### Monthly Tasks
```bash
# Run full restore test (see DR Drill Procedures above)

# Update backup retention policies
aws s3api get-bucket-lifecycle-configuration --bucket ${BACKUP_BUCKET}

# Review and optimize backup schedules
crontab -l

# Test DR failover procedures (in staging)

# Update DR documentation
# Review and update this runbook

# Conduct DR training for team
```

### Quarterly Tasks
```bash
# Run full DR drill (see DR Drill Procedures above)

# Review RTO/RPO targets and adjust if needed

# Audit backup and DR processes

# Update DR contact list

# Review and test escalation procedures

# Conduct DR tabletop exercise with stakeholders
```

---

## Quick Reference

### Common Commands
```bash
# Run all backups
make backup-all

# Check RPO status
./scripts/check-rpo.sh

# List backups
aws s3 ls s3://${BACKUP_BUCKET}/database/ --recursive | tail -10

# Restore database
./scripts/restore-database.sh backup-20251110.sql.gz

# Test DR site
./scripts/check-dr-status.sh

# Monthly restore test
./scripts/monthly-restore-test.sh
```

### Emergency Response
```bash
# P0: Production disaster - Activate DR
make activate-dr-site
# Follow full recovery procedure in runbook

# P0: Backup failure - Emergency backup
./scripts/backup-all.sh --priority

# P1: Restore validation failure - Test previous backup
./scripts/validate-backup.sh database $(aws s3 ls s3://${BACKUP_BUCKET}/database/ | tail -2 | head -1 | awk '{print $4}')
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Platform Engineering & SRE Team
- **Review Schedule:** Quarterly or after DR drills/incidents
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
