# Runbook — PRJ-CYB-OPS-002 (Incident Response Playbook)

## Overview

Production incident response runbook for cybersecurity operations, focusing on ransomware detection, containment, eradication, and recovery. This runbook provides clear guidance for security operations teams responding to security incidents, breaches, and ransomware attacks.

**System Components:**
- Incident detection and alerting systems
- Forensic data collection tools
- Backup and recovery systems
- Communication and escalation platforms
- Evidence preservation infrastructure
- Threat intelligence feeds
- SIEM and security monitoring
- Endpoint detection and response (EDR)
- Network isolation capabilities

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Critical incident response time** | < 15 minutes | Alert → first responder action |
| **P0 incident containment time** | < 1 hour | Detection → threat contained |
| **Ransomware detection time** | < 10 minutes | Infection → alert trigger |
| **Evidence preservation success** | 100% | All critical evidence captured |
| **Recovery time (ransomware)** | < 8 hours | Containment → systems restored |
| **Communication SLA (P0)** | < 30 minutes | Incident → stakeholder notification |
| **Backup verification frequency** | Daily | Successful backup restoration tests |
| **Post-incident report completion** | 72 hours | Incident resolution → report published |

---

## Dashboards & Alerts

### Dashboards

#### Incident Response Dashboard
```bash
# View active incidents
cat /var/log/security/active-incidents.json | jq '.[] | {id, severity, status, age}'

# Check incident queue
./scripts/incident-queue.sh | column -t

# View incident timeline
./scripts/incident-timeline.sh --incident-id INC-2025-001

# Incident response metrics
./scripts/ir-metrics.sh --period last-30-days | jq '.metrics | {
  total_incidents,
  avg_response_time,
  avg_containment_time,
  avg_recovery_time
}'
```

#### Ransomware Detection Dashboard
```bash
# Check for ransomware indicators
./scripts/check-ransomware-indicators.sh

# View file encryption activity
./scripts/monitor-file-activity.sh --pattern "*.encrypted|*.locked|*.crypto"

# Check for known ransomware extensions
./scripts/scan-ransomware-extensions.sh | grep -E "\.locky|\.cerber|\.revil"

# Monitor process behavior for ransomware
./scripts/detect-suspicious-processes.sh --criteria encryption,mass-file-ops

# Check for ransom notes
find /var/log /home /tmp -name "*RANSOM*" -o -name "*README*" -o -name "*DECRYPT*" 2>/dev/null
```

#### Threat Intelligence Dashboard
```bash
# Check latest threat intelligence
./scripts/fetch-threat-intel.sh --sources all

# View current threat landscape
./scripts/threat-summary.sh --format json | jq '.threats | group_by(.severity)'

# Check for IOCs (Indicators of Compromise)
./scripts/check-iocs.sh --sources alienvault,misp,otx

# Monitor dark web mentions
./scripts/darkweb-monitor.sh --keywords "company-name,brand,executive-names"
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | Ransomware detected | Immediate | Emergency response, isolate systems |
| **P0** | Active data breach | Immediate | Incident response team activation |
| **P0** | Multiple failed backups | Immediate | Verify backup integrity |
| **P1** | Malware outbreak | 15 minutes | Contain and investigate |
| **P1** | Unauthorized access to critical systems | 15 minutes | Revoke access, investigate |
| **P1** | Unusual data exfiltration | 30 minutes | Identify source, block egress |
| **P2** | Suspicious lateral movement | 1 hour | Investigate and monitor |
| **P3** | Policy violation | 4 hours | Document and review |

#### Alert Configuration
```bash
# Configure critical alerts
cat > /etc/security/alert-rules.conf << 'EOF'
# Ransomware Detection
alert.ransomware.file_encryption_rate: 100 files/minute
alert.ransomware.suspicious_extensions: true
alert.ransomware.vss_deletion: immediate
alert.ransomware.backup_tampering: immediate

# Data Breach
alert.data_exfiltration.threshold: 10GB/hour
alert.unauthorized_access.critical_systems: immediate
alert.credential_theft.detection: immediate

# Backup Failures
alert.backup_failure.consecutive: 2
alert.backup_integrity.check_failure: immediate
EOF

# Test alert configuration
./scripts/test-alert-rules.sh --config /etc/security/alert-rules.conf
```

---

## Standard Operations

### Incident Detection and Triage

#### Automated Detection
```bash
# Monitor security events
tail -f /var/log/security/events.log | grep -E "CRITICAL|HIGH|RANSOMWARE"

# Check SIEM for incidents
./scripts/siem-check.sh --severity high,critical --since 1h

# Endpoint detection alerts
./scripts/edr-alerts.sh --status new,in-progress

# Network intrusion detection
./scripts/nids-check.sh --alerts-only

# Automated threat detection
./scripts/auto-detect-threats.sh --continuous
```

#### Manual Triage
```bash
# Assess incident severity
./scripts/triage-incident.sh --incident-id INC-2025-001

# Classify incident type
./scripts/classify-incident.sh <<EOF
Symptoms:
- Multiple file extensions changed to .locked
- Ransom note found on desktop
- Network shares inaccessible
- High CPU usage on file server
EOF
# Output: RANSOMWARE - P0 - CRITICAL

# Determine scope
./scripts/assess-incident-scope.sh \
  --affected-systems "fileserver-01,dc-01" \
  --timeframe "last 2 hours"

# Identify patient zero
./scripts/find-patient-zero.sh \
  --incident-type ransomware \
  --symptoms "encrypted files"
```

### Incident Response Procedures

#### Initial Response (OODA Loop)

**Observe:**
```bash
# Gather initial evidence
INCIDENT_ID="INC-$(date +%Y%m%d-%H%M%S)"
mkdir -p /var/forensics/$INCIDENT_ID

# Capture volatile data
./scripts/capture-volatile-data.sh --output /var/forensics/$INCIDENT_ID/volatile/
# - Running processes
# - Network connections
# - Logged-in users
# - Memory dump

# Capture system state
./scripts/capture-system-state.sh --output /var/forensics/$INCIDENT_ID/system/
# - System logs
# - Security logs
# - Application logs
# - Configuration files

# Network capture
tcpdump -i any -w /var/forensics/$INCIDENT_ID/network-$(date +%Y%m%d-%H%M%S).pcap &
TCPDUMP_PID=$!
```

**Orient:**
```bash
# Analyze collected data
./scripts/analyze-evidence.sh --incident-dir /var/forensics/$INCIDENT_ID

# Check against known threats
./scripts/match-iocs.sh --evidence-dir /var/forensics/$INCIDENT_ID/

# Determine attack vector
./scripts/identify-attack-vector.sh --incident-id $INCIDENT_ID
# Output: Phishing email with malicious attachment

# Timeline analysis
./scripts/create-timeline.sh --incident-id $INCIDENT_ID --output /var/forensics/$INCIDENT_ID/timeline.csv
```

**Decide:**
```bash
# Evaluate response options
./scripts/response-options.sh --incident-id $INCIDENT_ID

# Option 1: Immediate isolation (for active threats)
# Option 2: Monitor and collect evidence (for persistent threats)
# Option 3: Controlled shutdown (for ransomware)

# Assess business impact
./scripts/impact-assessment.sh --affected-systems "fileserver-01,dc-01"
# Output:
# - Critical business functions affected: 3
# - Users impacted: 150
# - Estimated downtime: 4-8 hours
# - Financial impact: $50,000-$200,000

# Risk analysis
./scripts/risk-analysis.sh --action isolate --systems fileserver-01
# Output:
# - Risk of continued encryption: HIGH
# - Risk of data loss: MEDIUM
# - Risk of business disruption: MEDIUM
# RECOMMENDATION: Proceed with isolation
```

**Act:**
```bash
# Execute response plan
./scripts/execute-response-plan.sh \
  --incident-id $INCIDENT_ID \
  --action isolate \
  --systems fileserver-01,dc-01 \
  --notify security-team,management

# Document actions taken
./scripts/log-action.sh \
  --incident-id $INCIDENT_ID \
  --action "Isolated affected systems" \
  --timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --responder "$(whoami)"
```

---

## Ransomware Incident Response

### Phase 1: Detection and Containment (0-30 minutes)

**Immediate Actions:**
```bash
# 1. STOP THE SPREAD - Isolate infected systems immediately
INFECTED_SYSTEMS=("fileserver-01" "workstation-42" "dc-01")

for system in "${INFECTED_SYSTEMS[@]}"; do
  echo "[$(date)] Isolating $system"

  # Disable network interfaces (if local access)
  ssh $system "sudo ifconfig eth0 down"

  # Or block at network level (if remote)
  ./scripts/firewall-block.sh --host $system --direction both

  # Disable on hypervisor (for VMs)
  ./scripts/vm-disconnect-network.sh --vm $system

  # Tag system as quarantined
  ./scripts/tag-system.sh --host $system --tag "QUARANTINED:RANSOMWARE:$(date +%Y%m%d)"
done

# 2. Prevent spread to backups
# CRITICAL: Disconnect backup systems to prevent encryption of backups
echo "[$(date)] Protecting backups"

# Disconnect backup network
./scripts/isolate-backup-network.sh --vlan backup-vlan

# Set backups to read-only
./scripts/set-backup-readonly.sh --backup-server backup-01

# Snapshot current backup state
./scripts/snapshot-backups.sh --label "pre-ransomware-$(date +%Y%m%d-%H%M%S)"

# Verify backup integrity
./scripts/verify-backup-integrity.sh --all --detailed > /var/forensics/$INCIDENT_ID/backup-status.txt

# 3. Disable compromised accounts
echo "[$(date)] Disabling compromised accounts"

# Find accounts active on infected systems
COMPROMISED_ACCOUNTS=$(./scripts/find-active-accounts.sh --systems "${INFECTED_SYSTEMS[@]}")

for account in $COMPROMISED_ACCOUNTS; do
  echo "Disabling account: $account"

  # Disable AD account
  ./scripts/disable-ad-account.sh --username $account

  # Force logoff all sessions
  ./scripts/force-logoff.sh --username $account

  # Revoke tokens/credentials
  ./scripts/revoke-credentials.sh --username $account

  # Reset password
  NEW_PASS=$(./scripts/generate-secure-password.sh)
  ./scripts/reset-password.sh --username $account --password "$NEW_PASS"

  # Require password change on next login
  ./scripts/force-password-reset.sh --username $account
done

# 4. Block malicious IPs/domains
echo "[$(date)] Blocking malicious indicators"

# Extract C2 servers from network logs
C2_SERVERS=$(./scripts/extract-c2-servers.sh --incident-id $INCIDENT_ID)

for c2 in $C2_SERVERS; do
  echo "Blocking C2: $c2"

  # Firewall block
  ./scripts/firewall-block.sh --ip $c2 --direction outbound

  # DNS sinkhole
  ./scripts/dns-sinkhole.sh --domain $c2

  # Add to threat intel
  ./scripts/add-to-threat-intel.sh --indicator $c2 --type c2-server --threat ransomware
done

# 5. Preserve evidence
echo "[$(date)] Preserving forensic evidence"

# Memory dumps from infected systems
for system in "${INFECTED_SYSTEMS[@]}"; do
  ./scripts/acquire-memory-dump.sh --host $system --output /var/forensics/$INCIDENT_ID/memory/${system}.mem
done

# Disk images (for critical systems)
./scripts/acquire-disk-image.sh --host fileserver-01 --output /var/forensics/$INCIDENT_ID/disk/

# Export logs before they rotate
./scripts/export-all-logs.sh \
  --systems "${INFECTED_SYSTEMS[@]}" \
  --output /var/forensics/$INCIDENT_ID/logs/ \
  --timeframe "last 48 hours"

# Preserve network captures
kill $TCPDUMP_PID
gzip /var/forensics/$INCIDENT_ID/network-*.pcap

# 6. Notify stakeholders
echo "[$(date)] Notifying stakeholders"

./scripts/send-incident-notification.sh \
  --incident-id $INCIDENT_ID \
  --severity P0 \
  --type RANSOMWARE \
  --recipients "security-team@company.com,management@company.com,legal@company.com" \
  --subject "P0: RANSOMWARE INCIDENT - Immediate Action Required" \
  --message "$(cat <<EOF
RANSOMWARE INCIDENT DETECTED

Incident ID: $INCIDENT_ID
Detection Time: $(date)
Affected Systems: ${INFECTED_SYSTEMS[@]}
Status: CONTAINED

Immediate actions taken:
- Infected systems isolated
- Backups protected
- Compromised accounts disabled
- Malicious infrastructure blocked
- Evidence preserved

Current Phase: Containment
Next Steps: Investigation and recovery planning

Incident Commander: Security Operations Team
War Room: conference-room-A
Bridge: +1-555-0100 (PIN: 1234)

DO NOT PAY THE RANSOM. Recovery procedures in progress.
EOF
)"

# 7. Activate incident response team
./scripts/activate-ir-team.sh \
  --incident-id $INCIDENT_ID \
  --severity P0 \
  --call-tree security-team,management,it-ops,legal,pr

# 8. Document containment
cat > /var/forensics/$INCIDENT_ID/containment-report.md << EOF
# Containment Report - $INCIDENT_ID

**Time:** $(date -u +%Y-%m-%dT%H:%M:%SZ)
**Incident Type:** Ransomware
**Severity:** P0 - Critical

## Affected Systems
${INFECTED_SYSTEMS[@]}

## Containment Actions
- [x] Systems isolated from network
- [x] Backups protected and verified
- [x] Compromised accounts disabled
- [x] Malicious infrastructure blocked
- [x] Forensic evidence preserved
- [x] Stakeholders notified
- [x] IR team activated

## Status
Spread has been stopped. Proceeding to investigation phase.

## Incident Commander
$(whoami)

## Next Steps
1. Complete forensic analysis
2. Identify ransomware variant
3. Assess encryption extent
4. Develop recovery plan
5. Execute recovery
EOF
```

### Phase 2: Investigation and Analysis (30 minutes - 4 hours)

**Forensic Analysis:**
```bash
# 1. Identify ransomware variant
echo "[$(date)] Identifying ransomware variant"

# Analyze ransom note
RANSOM_NOTE=$(find /mnt/infected-filesystems -name "*RANSOM*" -o -name "*README*" | head -1)
./scripts/analyze-ransom-note.sh --file "$RANSOM_NOTE"
# Output: REvil (Sodinokibi) variant detected

# Analyze encrypted file extensions
ENCRYPTED_EXTENSIONS=$(find /mnt/infected-filesystems -type f | grep -oE '\.[^.]+$' | sort | uniq -c | sort -rn | head)
echo "$ENCRYPTED_EXTENSIONS" > /var/forensics/$INCIDENT_ID/encrypted-extensions.txt

# Check ransomware databases
./scripts/identify-ransomware.sh \
  --ransom-note "$RANSOM_NOTE" \
  --extensions "$ENCRYPTED_EXTENSIONS" \
  --hash $(md5sum "$RANSOM_NOTE" | awk '{print $1}')
# Output: Identified as REvil/Sodinokibi - Decryption unlikely without key

# 2. Determine infection vector
echo "[$(date)] Analyzing infection vector"

# Check patient zero
PATIENT_ZERO=$(./scripts/find-patient-zero.sh \
  --incident-id $INCIDENT_ID \
  --method timeline-analysis)
echo "Patient zero: $PATIENT_ZERO"

# Analyze email logs for phishing
./scripts/analyze-email-logs.sh \
  --user $(echo $PATIENT_ZERO | cut -d'\\' -f2) \
  --timeframe "$(date -d '48 hours ago' +%Y-%m-%d) to $(date +%Y-%m-%d)" \
  --suspicious-only

# Check web proxy logs for malicious downloads
./scripts/analyze-proxy-logs.sh \
  --user $PATIENT_ZERO \
  --timeframe "48 hours ago" \
  --pattern "\.exe|\.zip|\.js|\.vbs"

# Malware analysis
./scripts/extract-malware-sample.sh \
  --source /var/forensics/$INCIDENT_ID/memory/${PATIENT_ZERO}.mem \
  --output /var/forensics/$INCIDENT_ID/malware-samples/

# Submit to sandbox for analysis
./scripts/submit-to-sandbox.sh \
  --samples /var/forensics/$INCIDENT_ID/malware-samples/* \
  --sandbox any.run,hybrid-analysis

# 3. Timeline reconstruction
echo "[$(date)] Reconstructing attack timeline"

./scripts/create-detailed-timeline.sh \
  --incident-id $INCIDENT_ID \
  --sources "syslog,security-log,proxy,email,edr" \
  --output /var/forensics/$INCIDENT_ID/detailed-timeline.csv

# Key events in timeline:
# - Initial compromise (phishing email opened)
# - Malware execution
# - Lateral movement
# - Privilege escalation
# - Backup discovery
# - Encryption started
# - Ransom note deployed

# 4. Assess encryption extent
echo "[$(date)] Assessing encryption extent"

./scripts/assess-encryption-damage.sh \
  --systems "${INFECTED_SYSTEMS[@]}" \
  --output /var/forensics/$INCIDENT_ID/encryption-assessment.json

# Sample output:
# {
#   "total_files": 500000,
#   "encrypted_files": 125000,
#   "encryption_percentage": 25,
#   "critical_systems_affected": 3,
#   "data_recovery_priority": [
#     {"system": "fileserver-01", "priority": "critical", "files": 100000},
#     {"system": "dc-01", "priority": "high", "files": 20000},
#     {"system": "workstation-42", "priority": "low", "files": 5000}
#   ]
# }

# 5. Check for data exfiltration
echo "[$(date)] Checking for data exfiltration"

./scripts/check-data-exfiltration.sh \
  --incident-id $INCIDENT_ID \
  --systems "${INFECTED_SYSTEMS[@]}" \
  --timeframe "7 days"

# Analyze network traffic for large transfers
./scripts/analyze-network-transfers.sh \
  --pcap /var/forensics/$INCIDENT_ID/network-*.pcap.gz \
  --threshold 100MB

# Check for credential theft
./scripts/check-credential-theft.sh --incident-id $INCIDENT_ID
```

### Phase 3: Eradication (4-8 hours)

**Remove Threat:**
```bash
# 1. Identify all infected systems
echo "[$(date)] Identifying all infected systems"

# Scan entire network for indicators
./scripts/network-wide-scan.sh \
  --indicators /var/forensics/$INCIDENT_ID/iocs.txt \
  --output /var/forensics/$INCIDENT_ID/infected-systems-full.txt

FULL_INFECTED_LIST=$(cat /var/forensics/$INCIDENT_ID/infected-systems-full.txt)

# 2. Prepare clean rebuild
echo "[$(date)] Preparing clean system images"

# Verify clean base images
./scripts/verify-base-images.sh --all
# Ensure no malware in base images

# Prepare rebuild configuration
./scripts/generate-rebuild-plan.sh \
  --systems "$FULL_INFECTED_LIST" \
  --output /var/forensics/$INCIDENT_ID/rebuild-plan.json

# 3. Eradicate malware
for system in $FULL_INFECTED_LIST; do
  echo "[$(date)] Eradicating malware from $system"

  # Option A: Nuke and rebuild (RECOMMENDED for ransomware)
  ./scripts/nuke-and-rebuild.sh \
    --host $system \
    --base-image clean-windows-2019 \
    --preserve-data false \
    --backup-before true

  # Option B: Malware removal (NOT RECOMMENDED - may leave persistence)
  # ./scripts/remove-malware.sh --host $system --thorough

  # Option C: Restore from pre-infection backup
  # ./scripts/restore-from-backup.sh --host $system --date "$(date -d '3 days ago' +%Y-%m-%d)"
done

# 4. Credential reset
echo "[$(date)] Resetting all credentials"

# Reset ALL domain credentials (assume compromise)
./scripts/mass-credential-reset.sh \
  --scope all-users \
  --include service-accounts,computer-accounts \
  --method forced-reset \
  --notify-users true

# Regenerate Kerberos keys
./scripts/regenerate-krbtgt.sh --twice --interval 24h

# Reset service account passwords
./scripts/reset-service-accounts.sh --all

# Revoke all access tokens
./scripts/revoke-all-tokens.sh --systems all

# 5. Remove persistence mechanisms
echo "[$(date)] Removing persistence mechanisms"

# Scan for persistence
./scripts/scan-persistence.sh --all-systems --deep

# Common ransomware persistence locations:
# - Registry Run keys
# - Scheduled tasks
# - WMI event subscriptions
# - Service installations
# - GPO modifications

./scripts/remove-persistence.sh \
  --incident-id $INCIDENT_ID \
  --aggressive

# 6. Clean backups
echo "[$(date)] Validating and cleaning backups"

# Identify last known good backup (before infection)
INFECTION_TIME="2025-11-10 09:00:00"
CLEAN_BACKUP_DATE=$(./scripts/find-clean-backup.sh --before "$INFECTION_TIME")

echo "Last clean backup: $CLEAN_BACKUP_DATE"

# Delete compromised backups
./scripts/delete-compromised-backups.sh \
  --after "$INFECTION_TIME" \
  --confirm

# Verify clean backups are not infected
./scripts/scan-backups-for-malware.sh \
  --backup-date "$CLEAN_BACKUP_DATE" \
  --deep-scan
```

### Phase 4: Recovery (8-24 hours)

**Restore Operations:**
```bash
# 1. Develop recovery plan
echo "[$(date)] Developing recovery plan"

./scripts/create-recovery-plan.sh \
  --incident-id $INCIDENT_ID \
  --clean-backup-date "$CLEAN_BACKUP_DATE" \
  --systems-to-recover "${INFECTED_SYSTEMS[@]}" \
  --priority critical-first \
  --output /var/forensics/$INCIDENT_ID/recovery-plan.json

# Recovery order (based on business criticality):
# 1. Domain Controllers
# 2. Email servers
# 3. File servers
# 4. Database servers
# 5. Application servers
# 6. Workstations

# 2. Restore from backups
echo "[$(date)] Beginning system recovery"

RECOVERY_ORDER=("dc-01" "fileserver-01" "workstation-42")

for system in "${RECOVERY_ORDER[@]}"; do
  echo "[$(date)] Recovering $system"

  # Restore from clean backup
  ./scripts/restore-system.sh \
    --host $system \
    --backup-date "$CLEAN_BACKUP_DATE" \
    --verify-integrity true \
    --test-restore true

  # Verify restoration
  ./scripts/verify-system-integrity.sh --host $system

  # Apply security patches
  ./scripts/apply-security-patches.sh --host $system --all

  # Harden configuration
  ./scripts/harden-system.sh --host $system --profile ransomware-protection

  # Install enhanced monitoring
  ./scripts/install-edr-agent.sh --host $system

  # Verify no malware
  ./scripts/malware-scan.sh --host $system --deep

  # Document recovery
  ./scripts/log-recovery.sh \
    --incident-id $INCIDENT_ID \
    --system $system \
    --status "RECOVERED" \
    --backup-used "$CLEAN_BACKUP_DATE"
done

# 3. Data recovery for files encrypted after clean backup
echo "[$(date)] Attempting recovery of recently encrypted files"

# Check for Shadow Copies (if not deleted by ransomware)
./scripts/check-shadow-copies.sh --systems "${RECOVERY_ORDER[@]}"

# Attempt file recovery from shadow copies
./scripts/restore-from-shadow-copies.sh \
  --systems fileserver-01 \
  --output /var/recovery/shadow-copy-files/

# Check for ransomware decryptors
./scripts/check-for-decryptor.sh --ransomware-variant REvil
# Note: As of 2025-11, no reliable decryptor for REvil

# Reconstruct lost data from other sources
./scripts/reconstruct-data.sh \
  --sources "email-attachments,local-copies,cloud-sync" \
  --output /var/recovery/reconstructed/

# 4. Reconnect to network (carefully)
echo "[$(date)] Reconnecting systems to network"

for system in "${RECOVERY_ORDER[@]}"; do
  echo "[$(date)] Reconnecting $system"

  # Re-enable network in isolated VLAN first
  ./scripts/vm-connect-network.sh --vm $system --vlan recovery-vlan

  # Monitor for 30 minutes
  ./scripts/monitor-system-behavior.sh --host $system --duration 30m

  # Check for re-infection indicators
  ./scripts/check-reinfection.sh --host $system

  # If clear, move to production network
  ./scripts/vm-connect-network.sh --vm $system --vlan production-vlan

  # Enable firewall rules
  ./scripts/firewall-enable.sh --host $system --profile production
done

# 5. Validate recovery
echo "[$(date)] Validating recovery"

./scripts/validate-recovery.sh \
  --incident-id $INCIDENT_ID \
  --systems "${RECOVERY_ORDER[@]}" \
  --tests "connectivity,authentication,file-access,application-functionality"

# User acceptance testing
./scripts/uat-checklist.sh \
  --incident-id $INCIDENT_ID \
  --business-functions "file-sharing,email,crm,erp"

# 6. Resume normal operations
echo "[$(date)] Resuming normal operations"

# Notify users
./scripts/send-notification.sh \
  --recipients all-users@company.com \
  --subject "Systems Restored - Normal Operations Resumed" \
  --message "$(cat <<EOF
All systems have been recovered from the ransomware incident.

Recovered Systems:
- File servers
- Domain controllers
- Email services

Please note the following:
- All passwords have been reset - check your email for new credentials
- Files modified after $(date -d "$CLEAN_BACKUP_DATE" +%Y-%m-%d) may need to be recreated
- Enhanced monitoring is in place
- Report any unusual activity immediately

If you experience any issues, contact IT support.

Thank you for your patience.
EOF
)"

# Re-enable backups
./scripts/reconnect-backup-network.sh --vlan backup-vlan
./scripts/set-backup-readwrite.sh --backup-server backup-01

# Start full backup of recovered systems
./scripts/start-full-backup.sh --systems "${RECOVERY_ORDER[@]}"
```

### Phase 5: Post-Incident (24-72 hours)

**Lessons Learned and Improvement:**
```bash
# 1. Post-incident review
echo "[$(date)] Conducting post-incident review"

./scripts/generate-post-incident-report.sh \
  --incident-id $INCIDENT_ID \
  --output /var/forensics/$INCIDENT_ID/post-incident-report.pdf

# Schedule PIR meeting
./scripts/schedule-meeting.sh \
  --title "Post-Incident Review: $INCIDENT_ID" \
  --attendees "security-team,management,it-ops,affected-users" \
  --duration "2 hours" \
  --date "$(date -d '+3 days' +%Y-%m-%d)"

# 2. Root cause analysis
cat > /var/forensics/$INCIDENT_ID/root-cause-analysis.md << 'EOF'
# Root Cause Analysis - Ransomware Incident

## Incident Summary
- Type: REvil ransomware
- Initial compromise: Phishing email
- Attack vector: Malicious Excel attachment with macros
- Patient zero: workstation-42 (john.doe)

## Root Causes

### Primary Cause
**Lack of email attachment filtering**
- Malicious macro-enabled documents not blocked
- No sandboxing of email attachments
- User able to execute macros

### Contributing Causes
1. **Inadequate user training**: User opened suspicious attachment
2. **Insufficient endpoint protection**: Antivirus did not detect malware
3. **Excessive user privileges**: User had local admin rights
4. **Missing network segmentation**: Lateral movement too easy
5. **Incomplete backup protection**: Backups accessible from infected system

## Recommendations
1. Deploy email attachment sandboxing
2. Block macro-enabled documents by default
3. Enhance security awareness training
4. Remove local admin rights from users
5. Implement network segmentation
6. Isolate backup infrastructure
7. Deploy EDR on all endpoints
8. Implement application whitelisting

EOF

# 3. Implement preventive controls
echo "[$(date)] Implementing preventive controls"

# Email security improvements
./scripts/configure-email-protection.sh \
  --block-macros true \
  --sandbox-attachments true \
  --link-protection true

# Endpoint hardening
./scripts/mass-endpoint-hardening.sh \
  --disable-macros true \
  --remove-local-admin true \
  --enable-applocker true \
  --install-edr true

# Network segmentation
./scripts/implement-network-segmentation.sh \
  --isolate backups,admin-systems,critical-servers

# Backup protection
./scripts/harden-backup-infrastructure.sh \
  --air-gap true \
  --immutable-backups true \
  --separate-credentials true

# Enhanced monitoring
./scripts/deploy-enhanced-monitoring.sh \
  --focus ransomware-indicators,lateral-movement,privilege-escalation

# 4. Update incident response procedures
./scripts/update-runbook.sh \
  --incident-id $INCIDENT_ID \
  --lessons-learned /var/forensics/$INCIDENT_ID/root-cause-analysis.md

# 5. Conduct tabletop exercise
./scripts/schedule-tabletop-exercise.sh \
  --scenario ransomware \
  --date "$(date -d '+30 days' +%Y-%m-%d)" \
  --participants "security-team,it-ops,management"

# 6. Final report
./scripts/generate-final-report.sh \
  --incident-id $INCIDENT_ID \
  --include-all \
  --output /var/forensics/$INCIDENT_ID/FINAL-REPORT.pdf \
  --distribution "management,legal,insurance,board"
```

---

## Evidence Collection and Preservation

### Forensic Data Collection

#### Volatile Data Collection
```bash
# Create forensic collection script
cat > /tmp/collect-volatile-data.sh << 'EOF'
#!/bin/bash
# Volatile Data Collection Script
# Run on suspected compromised system

OUTPUT_DIR="/tmp/forensics-$(hostname)-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo "[+] Collecting volatile data to $OUTPUT_DIR"

# System information
uname -a > "$OUTPUT_DIR/system-info.txt"
date >> "$OUTPUT_DIR/system-info.txt"
uptime >> "$OUTPUT_DIR/system-info.txt"

# Running processes
ps auxww > "$OUTPUT_DIR/processes.txt"
pstree -p > "$OUTPUT_DIR/process-tree.txt"

# Network connections
netstat -anp > "$OUTPUT_DIR/network-connections.txt"
ss -tulpn >> "$OUTPUT_DIR/network-connections.txt"
lsof -i >> "$OUTPUT_DIR/open-files-network.txt"

# Logged-in users
who > "$OUTPUT_DIR/logged-in-users.txt"
w >> "$OUTPUT_DIR/logged-in-users.txt"
last -F >> "$OUTPUT_DIR/login-history.txt"

# Open files
lsof > "$OUTPUT_DIR/open-files-all.txt"

# Environment variables
env > "$OUTPUT_DIR/environment.txt"

# Loaded modules
lsmod > "$OUTPUT_DIR/loaded-modules.txt"

# Routing table
route -n > "$OUTPUT_DIR/routing-table.txt"
ip route >> "$OUTPUT_DIR/routing-table.txt"

# ARP cache
arp -a > "$OUTPUT_DIR/arp-cache.txt"

# Clipboard (if accessible)
xclip -o > "$OUTPUT_DIR/clipboard.txt" 2>/dev/null || echo "N/A" > "$OUTPUT_DIR/clipboard.txt"

# Memory dump (requires root)
if [ "$EUID" -eq 0 ]; then
  echo "[+] Acquiring memory dump (may take several minutes)"
  dd if=/dev/mem of="$OUTPUT_DIR/memory.dump" bs=1M 2>/dev/null || \
    echo "Memory dump failed - requires kernel module" > "$OUTPUT_DIR/memory-dump-failed.txt"
fi

# Create tarball
cd /tmp
tar czf "forensics-$(hostname)-$(date +%Y%m%d-%H%M%S).tar.gz" "$(basename $OUTPUT_DIR)"
echo "[+] Collection complete: /tmp/forensics-$(hostname)-$(date +%Y%m%d-%H%M%S).tar.gz"
EOF

chmod +x /tmp/collect-volatile-data.sh

# Deploy and execute on target systems
for system in "${INFECTED_SYSTEMS[@]}"; do
  scp /tmp/collect-volatile-data.sh $system:/tmp/
  ssh $system "sudo /tmp/collect-volatile-data.sh"
  scp $system:/tmp/forensics-*.tar.gz /var/forensics/$INCIDENT_ID/
done
```

#### Disk Imaging
```bash
# Create disk image for forensic analysis
./scripts/create-forensic-image.sh \
  --host fileserver-01 \
  --disk /dev/sda \
  --output /var/forensics/$INCIDENT_ID/disk-images/fileserver-01.dd \
  --hash-algorithm sha256 \
  --compress true

# Verify integrity
sha256sum /var/forensics/$INCIDENT_ID/disk-images/fileserver-01.dd > \
  /var/forensics/$INCIDENT_ID/disk-images/fileserver-01.dd.sha256

# Mount as read-only for analysis
mkdir -p /mnt/forensics/fileserver-01
mount -o ro,loop /var/forensics/$INCIDENT_ID/disk-images/fileserver-01.dd /mnt/forensics/fileserver-01
```

#### Log Collection
```bash
# Centralize all relevant logs
./scripts/collect-all-logs.sh \
  --incident-id $INCIDENT_ID \
  --systems "${INFECTED_SYSTEMS[@]}" \
  --sources "syslog,auth,security,application,firewall,proxy,email" \
  --timeframe "7 days before incident to now" \
  --output /var/forensics/$INCIDENT_ID/logs/

# Parse and normalize logs
./scripts/normalize-logs.sh \
  --input /var/forensics/$INCIDENT_ID/logs/ \
  --output /var/forensics/$INCIDENT_ID/logs-normalized/ \
  --format json

# Import into analysis platform
./scripts/import-to-splunk.sh \
  --logs /var/forensics/$INCIDENT_ID/logs-normalized/ \
  --index "incident-$INCIDENT_ID"
```

### Chain of Custody

**Evidence Tracking:**
```bash
# Initialize chain of custody
./scripts/init-chain-of-custody.sh --incident-id $INCIDENT_ID

# Record evidence
./scripts/record-evidence.sh \
  --incident-id $INCIDENT_ID \
  --evidence-id "EVID-001" \
  --type "Disk Image" \
  --description "Full disk image of fileserver-01" \
  --location "/var/forensics/$INCIDENT_ID/disk-images/fileserver-01.dd" \
  --hash "sha256:abc123..." \
  --collected-by "$(whoami)" \
  --collected-at "$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Transfer evidence
./scripts/transfer-evidence.sh \
  --incident-id $INCIDENT_ID \
  --evidence-id "EVID-001" \
  --from "$(whoami)" \
  --to "forensics-team@company.com" \
  --reason "Forensic analysis" \
  --timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Generate chain of custody report
./scripts/generate-chain-of-custody-report.sh \
  --incident-id $INCIDENT_ID \
  --output /var/forensics/$INCIDENT_ID/chain-of-custody.pdf
```

---

## Communication and Escalation

### Incident Communication

#### Internal Communication
```bash
# Initial notification (within 30 minutes)
./scripts/send-incident-alert.sh \
  --severity P0 \
  --type RANSOMWARE \
  --recipients "security-team,it-management,c-level" \
  --template initial-alert

# Regular updates (every 2 hours during active response)
./scripts/send-incident-update.sh \
  --incident-id $INCIDENT_ID \
  --status "Containment complete, recovery in progress" \
  --next-update "2 hours"

# Status page update
./scripts/update-status-page.sh \
  --incident-id $INCIDENT_ID \
  --status "Investigating" \
  --message "We are investigating a security incident affecting file services."
```

#### External Communication
```bash
# Legal notification (data breach laws)
./scripts/assess-breach-notification-requirements.sh \
  --incident-id $INCIDENT_ID \
  --data-types accessed,exfiltrated \
  --jurisdictions "US,EU,UK,CA"

# If required, notify authorities
./scripts/notify-authorities.sh \
  --incident-id $INCIDENT_ID \
  --agencies "FBI,State-AG,ICO,CISA"

# Customer notification (if data breach)
./scripts/generate-customer-notification.sh \
  --incident-id $INCIDENT_ID \
  --template data-breach \
  --output /var/forensics/$INCIDENT_ID/customer-notification.pdf

# Media statement
./scripts/generate-media-statement.sh \
  --incident-id $INCIDENT_ID \
  --approved-by "Legal,PR" \
  --output /var/forensics/$INCIDENT_ID/media-statement.pdf
```

### Escalation Paths

| Severity | Initial Contact | Escalation (15 min) | Escalation (30 min) |
|----------|----------------|-------------------|-------------------|
| P0 | Security Team Lead | CISO | CTO / CIO |
| P1 | On-call Security Analyst | Security Team Lead | CISO |
| P2 | Security Analyst | Security Team Lead | - |
| P3 | Security Analyst | - | - |

```bash
# Automated escalation
./scripts/auto-escalate.sh \
  --incident-id $INCIDENT_ID \
  --severity P0 \
  --no-response-timeout 15m
```

---

## Troubleshooting

### Common Issues

#### Issue: Backup Restoration Fails
```bash
# Check backup integrity
./scripts/verify-backup.sh --backup-id <backup-id> --deep-check

# Try alternative backup
./scripts/list-available-backups.sh --system fileserver-01 --before "$INFECTION_TIME"

# Restore to alternative location
./scripts/restore-to-staging.sh --backup-id <backup-id> --staging-server recovery-01
```

#### Issue: Ransomware Re-infection
```bash
# Immediate re-isolation
./scripts/re-isolate-system.sh --host $system

# Deep scan for persistence
./scripts/deep-persistence-scan.sh --host $system

# Check for compromised credentials
./scripts/audit-credentials.sh --system $system

# Rebuild from clean image (do not restore from backup)
./scripts/nuke-and-rebuild.sh --host $system --clean-image-only
```

---

## Quick Reference

### Ransomware Response Checklist
- [ ] Isolate infected systems immediately
- [ ] Protect backups (disconnect/read-only)
- [ ] Disable compromised accounts
- [ ] Block malicious infrastructure (C2 servers)
- [ ] Preserve forensic evidence
- [ ] Notify stakeholders
- [ ] Activate incident response team
- [ ] DO NOT PAY THE RANSOM
- [ ] Identify ransomware variant
- [ ] Determine infection vector
- [ ] Assess encryption extent
- [ ] Develop recovery plan
- [ ] Restore from clean backups
- [ ] Verify no re-infection
- [ ] Resume normal operations
- [ ] Conduct post-incident review
- [ ] Implement preventive controls

### Emergency Contacts
- **Security Team**: security-team@company.com / +1-555-0100
- **CISO**: ciso@company.com / +1-555-0101
- **Legal**: legal@company.com / +1-555-0102
- **PR**: pr@company.com / +1-555-0103
- **External IR**: external-ir@partner.com / +1-555-0200

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Security Operations / Incident Response Team
- **Review Schedule:** Quarterly or after major incidents
- **Related Docs**: Business Continuity Plan, Disaster Recovery Plan, Security Policies
- **Feedback:** Submit via security@company.com
