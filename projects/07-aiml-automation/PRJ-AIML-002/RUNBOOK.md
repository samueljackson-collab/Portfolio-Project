# Runbook — PRJ-AIML-002 (Cross-Platform AI Tab Organization App)

## Overview

Production operations runbook for the Cross-Platform AI Tab Organization App - an AI/ML-powered application that automatically groups and manages browser tabs across Android, Windows, and macOS platforms. Compatible with Chrome, Firefox, and Edge browsers.

**System Components:**
- Flutter cross-platform application (Android/Windows/macOS)
- Browser extensions (Chrome/Firefox/Edge)
- Native messaging host (Dart/Node.js bridge)
- TensorFlow Lite ML model for tab classification
- Firebase/Firestore sync service
- Hive local database
- Background sync workers

**Current Status:** 🟠 In Progress - Phase 1: Foundation Development

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Tab classification accuracy** | 90% | Correctly categorized tabs / total tabs |
| **Classification speed** | < 500ms | Time per tab classification |
| **App availability** | 99% | Uptime across all platforms |
| **Sync latency** | < 2 seconds | Cloud sync propagation time |
| **Battery impact (mobile)** | < 2% per hour | Background process battery consumption |
| **Memory usage** | < 100MB per 100 tabs | RAM consumption for tab management |
| **Browser extension response** | < 200ms | Extension UI interaction latency |

---

## Dashboards & Alerts

### Dashboards

#### Application Health Dashboard
```bash
# Check Flutter app status (desktop)
ps aux | grep flutter | grep -v grep

# Check browser extension status
# Chrome: Navigate to chrome://extensions
# Firefox: Navigate to about:addons

# Check native messaging host
ps aux | grep native-host | grep -v grep
cat /var/log/tab-organizer/native-host.log | tail -20

# Check background sync worker
systemctl status tab-organizer-sync
journalctl -u tab-organizer-sync -n 50
```

#### ML Model Performance Dashboard
```bash
# Check model inference metrics
cat /var/log/tab-organizer/ml-metrics.log | tail -50

# Review classification accuracy
sqlite3 ~/.local/share/tab-organizer/analytics.db \
  "SELECT category, COUNT(*), AVG(confidence) FROM classifications
   WHERE timestamp > datetime('now', '-24 hours')
   GROUP BY category;"

# Check model load time
grep "Model loaded" /var/log/tab-organizer/app.log | tail -5

# Monitor inference queue
cat /tmp/tab-organizer/inference-queue.json | jq '.queue_depth'
```

#### Sync Service Dashboard
```bash
# Check Firebase connection
curl -X GET "https://tab-organizer.firebaseio.com/.json?auth=$FIREBASE_TOKEN"

# Check sync queue status
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT COUNT(*) FROM sync_queue WHERE status='pending';"

# Review sync conflicts
grep "SYNC_CONFLICT" /var/log/tab-organizer/sync.log | tail -10

# Check last successful sync
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT MAX(last_sync_time) FROM sync_metadata;"
```

#### Resource Usage Dashboard
```bash
# Check memory usage
ps aux | grep -E "flutter|tab-organizer" | awk '{sum+=$6} END {print sum/1024 " MB"}'

# Check CPU usage
top -bn1 | grep -E "flutter|tab-organizer"

# Check disk usage
du -sh ~/.local/share/tab-organizer/
du -sh ~/.cache/tab-organizer/

# Check network usage (if iftop available)
iftop -t -s 10 2>&1 | grep -A 5 "firebaseio.com"
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | App crashed on all platforms | Immediate | Restart app, check crash logs |
| **P0** | ML model unavailable | Immediate | Reload model, check filesystem |
| **P1** | Classification accuracy < 70% | 15 minutes | Investigate model, check training data |
| **P1** | Sync service down | 15 minutes | Restart sync worker, check Firebase |
| **P1** | Browser extension unresponsive | 15 minutes | Reload extension, check native host |
| **P2** | Battery drain > 5%/hour | 30 minutes | Check background tasks, optimize |
| **P2** | Memory usage > 200MB | 30 minutes | Investigate memory leak, restart app |
| **P2** | Sync conflicts > 10/hour | 30 minutes | Review conflict resolution logic |
| **P3** | Classification queue depth > 50 | 1 hour | Monitor, consider scaling |

#### Alert Queries

```bash
# Check for app crashes
if ! pgrep -f "flutter.*tab-organizer" > /dev/null; then
  echo "ALERT: Tab organizer app not running"
fi

# Check ML model availability
if [ ! -f ~/.local/share/tab-organizer/models/classifier.tflite ]; then
  echo "ALERT: ML model file missing"
fi

# Check classification accuracy
ACCURACY=$(sqlite3 ~/.local/share/tab-organizer/analytics.db \
  "SELECT CAST(SUM(CASE WHEN user_corrected=0 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100
   FROM classifications WHERE timestamp > datetime('now', '-1 hour');")
if (( $(echo "$ACCURACY < 70" | bc -l) )); then
  echo "ALERT: Classification accuracy below threshold: $ACCURACY%"
fi

# Check sync queue depth
SYNC_PENDING=$(sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT COUNT(*) FROM sync_queue WHERE status='pending';")
if [ $SYNC_PENDING -gt 100 ]; then
  echo "ALERT: Sync queue backed up: $SYNC_PENDING items pending"
fi

# Check battery usage (Android - requires adb)
BATTERY=$(adb shell dumpsys battery | grep level | awk '{print $2}')
# Compare with baseline and alert if drain rate exceeds threshold
```

---

## Standard Operations

### Application Management

#### Start Application

**Desktop (Windows/macOS/Linux):**
```bash
# Start Flutter app
cd /opt/tab-organizer/flutter-app
flutter run -d windows  # or macos, linux

# Start in release mode
flutter run --release -d windows

# Start background services
systemctl start tab-organizer-sync
systemctl start tab-organizer-native-host

# Verify startup
ps aux | grep -E "flutter|tab-organizer"
tail -f /var/log/tab-organizer/app.log
```

**Android:**
```bash
# Install via ADB
adb install /path/to/tab-organizer.apk

# Launch app
adb shell am start -n com.taborganizer.app/.MainActivity

# Check app status
adb shell dumpsys package com.taborganizer.app | grep -A 5 "Running"

# View logs
adb logcat | grep TabOrganizer
```

#### Stop Application
```bash
# Stop Flutter app
pkill -f "flutter.*tab-organizer"

# Stop background services
systemctl stop tab-organizer-sync
systemctl stop tab-organizer-native-host

# Android
adb shell am force-stop com.taborganizer.app

# Verify shutdown
ps aux | grep -E "flutter|tab-organizer"
```

#### Restart Application
```bash
# Desktop restart
systemctl restart tab-organizer-sync
systemctl restart tab-organizer-native-host
pkill -f "flutter.*tab-organizer"
cd /opt/tab-organizer/flutter-app && flutter run --release -d windows &

# Android restart
adb shell am force-stop com.taborganizer.app
sleep 2
adb shell am start -n com.taborganizer.app/.MainActivity
```

### Browser Extension Management

#### Install Browser Extensions

**Chrome:**
```bash
# Development mode
# 1. Open chrome://extensions
# 2. Enable "Developer mode"
# 3. Click "Load unpacked"
# 4. Select: /opt/tab-organizer/browser-extensions/chrome-extension

# Production (after publishing)
# Navigate to: https://chrome.google.com/webstore/detail/tab-organizer/[extension-id]
```

**Firefox:**
```bash
# Development mode
# 1. Navigate to about:debugging#/runtime/this-firefox
# 2. Click "Load Temporary Add-on"
# 3. Select: /opt/tab-organizer/browser-extensions/firefox-extension/manifest.json

# Production
# Navigate to: https://addons.mozilla.org/firefox/addon/tab-organizer/
```

**Edge:**
```bash
# Development mode
# 1. Navigate to edge://extensions
# 2. Enable "Developer mode"
# 3. Click "Load unpacked"
# 4. Select: /opt/tab-organizer/browser-extensions/chrome-extension (compatible)
```

#### Update Browser Extensions
```bash
# Update extension code
cd /opt/tab-organizer/browser-extensions
git pull origin main

# Chrome/Edge: Reload extension
# Navigate to chrome://extensions or edge://extensions
# Click reload button for Tab Organizer extension

# Firefox: Reload extension
# Navigate to about:debugging#/runtime/this-firefox
# Click "Reload" for Tab Organizer
```

#### Troubleshoot Extension Issues
```bash
# Check extension logs (Chrome)
# 1. Navigate to chrome://extensions
# 2. Enable "Developer mode"
# 3. Click "background page" or "service worker" for Tab Organizer
# 4. Check console for errors

# Check native messaging host connection
grep "Native host" /var/log/tab-organizer/extension.log

# Test native messaging
echo '{"action": "ping"}' | /opt/tab-organizer/native-host/tab-organizer-host

# Verify permissions
cat /opt/tab-organizer/browser-extensions/chrome-extension/manifest.json | jq '.permissions'
```

### ML Model Operations

#### Load ML Model
```bash
# Check model file exists
ls -lh ~/.local/share/tab-organizer/models/classifier.tflite

# Test model loading
python3 << EOF
import tensorflow as tf
interpreter = tf.lite.Interpreter(
    model_path="/home/user/.local/share/tab-organizer/models/classifier.tflite"
)
interpreter.allocate_tensors()
print("Model loaded successfully")
print(f"Input details: {interpreter.get_input_details()}")
print(f"Output details: {interpreter.get_output_details()}")
EOF

# Monitor model load time
tail -f /var/log/tab-organizer/app.log | grep "Model loaded"
```

#### Update ML Model
```bash
# Backup current model
cp ~/.local/share/tab-organizer/models/classifier.tflite \
   ~/.local/share/tab-organizer/models/backup/classifier-$(date +%Y%m%d).tflite

# Download new model version
wget https://models.tab-organizer.com/classifier-v2.0.tflite \
  -O ~/.local/share/tab-organizer/models/classifier.tflite

# Or copy from development
cp /opt/tab-organizer/ai-model/output/classifier.tflite \
   ~/.local/share/tab-organizer/models/

# Restart app to load new model
systemctl restart tab-organizer-sync
pkill -f "flutter.*tab-organizer"

# Verify new model version
grep "Model version" /var/log/tab-organizer/app.log | tail -1

# Test new model
# Open app and classify a few tabs, check accuracy
```

#### Rollback ML Model
```bash
# List available backups
ls -lh ~/.local/share/tab-organizer/models/backup/

# Restore previous version
BACKUP_DATE="20250101"
cp ~/.local/share/tab-organizer/models/backup/classifier-$BACKUP_DATE.tflite \
   ~/.local/share/tab-organizer/models/classifier.tflite

# Restart app
systemctl restart tab-organizer-sync
pkill -f "flutter.*tab-organizer"

# Verify rollback
grep "Model loaded" /var/log/tab-organizer/app.log | tail -1
```

#### Retrain Model
```bash
# Collect training data
cd /opt/tab-organizer/ai-model
python3 scripts/export_training_data.py \
  --db ~/.local/share/tab-organizer/local.db \
  --output training-data/user-corrections-$(date +%Y%m%d).csv

# Combine with existing training data
cat training-data/*.csv > training-data/combined.csv

# Train new model
python3 scripts/train_classifier.py \
  --input training-data/combined.csv \
  --output output/classifier-v2.1.tflite \
  --epochs 50 \
  --batch-size 32

# Evaluate model
python3 scripts/evaluate_model.py \
  --model output/classifier-v2.1.tflite \
  --test-data training-data/test-set.csv

# Deploy if accuracy improves
cp output/classifier-v2.1.tflite ~/.local/share/tab-organizer/models/classifier.tflite
systemctl restart tab-organizer-sync
```

### Sync Service Operations

#### Check Sync Status
```bash
# View sync service status
systemctl status tab-organizer-sync

# Check last successful sync
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT device_name, last_sync_time, sync_status
   FROM sync_metadata ORDER BY last_sync_time DESC LIMIT 5;"

# Check pending sync items
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT COUNT(*), sync_type FROM sync_queue
   WHERE status='pending' GROUP BY sync_type;"

# View sync log
tail -50 /var/log/tab-organizer/sync.log
```

#### Force Sync
```bash
# Trigger manual sync
curl -X POST http://localhost:8765/api/sync/trigger

# Or via CLI
/opt/tab-organizer/bin/tab-organizer-cli sync --force

# Monitor sync progress
tail -f /var/log/tab-organizer/sync.log
```

#### Resolve Sync Conflicts
```bash
# List conflicts
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT * FROM sync_conflicts WHERE resolved=0;"

# View specific conflict
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT local_data, remote_data, conflict_type
   FROM sync_conflicts WHERE id=123;" | jq .

# Resolve conflict (keep local)
/opt/tab-organizer/bin/tab-organizer-cli sync resolve \
  --conflict-id 123 --strategy keep-local

# Resolve conflict (keep remote)
/opt/tab-organizer/bin/tab-organizer-cli sync resolve \
  --conflict-id 123 --strategy keep-remote

# Resolve conflict (merge)
/opt/tab-organizer/bin/tab-organizer-cli sync resolve \
  --conflict-id 123 --strategy merge
```

#### Reset Sync State
```bash
# ⚠️ CAUTION: This clears sync metadata and resyncs from cloud

# Backup local database
cp ~/.local/share/tab-organizer/local.db \
   ~/.local/share/tab-organizer/backup/local-$(date +%Y%m%d).db

# Clear sync state
sqlite3 ~/.local/share/tab-organizer/local.db \
  "DELETE FROM sync_queue; DELETE FROM sync_metadata;"

# Restart sync service
systemctl restart tab-organizer-sync

# Monitor full resync
tail -f /var/log/tab-organizer/sync.log
```

### Data Management

#### Backup User Data
```bash
# Backup local database
cp ~/.local/share/tab-organizer/local.db \
   ~/backups/tab-organizer/local-$(date +%Y%m%d).db

# Backup user preferences
cp ~/.config/tab-organizer/preferences.json \
   ~/backups/tab-organizer/preferences-$(date +%Y%m%d).json

# Export user data (JSON)
/opt/tab-organizer/bin/tab-organizer-cli export \
  --format json \
  --output ~/backups/tab-organizer/export-$(date +%Y%m%d).json

# Verify backup
ls -lh ~/backups/tab-organizer/
sqlite3 ~/backups/tab-organizer/local-$(date +%Y%m%d).db "SELECT COUNT(*) FROM tabs;"
```

#### Restore User Data
```bash
# Restore local database
cp ~/backups/tab-organizer/local-20250101.db \
   ~/.local/share/tab-organizer/local.db

# Restore preferences
cp ~/backups/tab-organizer/preferences-20250101.json \
   ~/.config/tab-organizer/preferences.json

# Import from JSON export
/opt/tab-organizer/bin/tab-organizer-cli import \
  --format json \
  --input ~/backups/tab-organizer/export-20250101.json

# Restart app
systemctl restart tab-organizer-sync
```

#### Clear Cache
```bash
# Clear tab thumbnails cache
rm -rf ~/.cache/tab-organizer/thumbnails/*

# Clear ML model cache
rm -rf ~/.cache/tab-organizer/ml-cache/*

# Clear sync cache
sqlite3 ~/.local/share/tab-organizer/local.db \
  "DELETE FROM cache WHERE expires_at < datetime('now');"

# Restart app
systemctl restart tab-organizer-sync
```

---

## Incident Response

### Detection

**Automated Detection:**
- App crash reports (sentry.io or similar)
- ML model inference failures
- Sync service health check failures
- Battery drain alerts (Android)
- Memory usage threshold alerts

**Manual Detection:**
```bash
# Check app is running
pgrep -f "flutter.*tab-organizer" || echo "App not running"
systemctl status tab-organizer-sync

# Check for crashes
grep "CRASH" /var/log/tab-organizer/app.log | tail -10
# Android: adb logcat | grep AndroidRuntime

# Check sync status
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT * FROM sync_metadata WHERE last_sync_time < datetime('now', '-1 hour');"

# Check ML model
tail -20 /var/log/tab-organizer/ml-metrics.log | grep ERROR
```

### Triage

#### Severity Classification

**P0: Critical Failure**
- App crashes on startup (all platforms)
- ML model completely unavailable
- Data loss or corruption
- Firebase authentication failure (users locked out)

**P1: Major Degradation**
- Classification accuracy < 50%
- Sync service completely down
- Browser extension unresponsive
- Battery drain > 10%/hour
- Memory leak causing OOM

**P2: Moderate Issues**
- Sync conflicts accumulating
- Individual platform issues
- Extension slow but functional
- Elevated error rate (5-10%)
- UI glitches

**P3: Minor Issues**
- Single classification error
- Temporary sync delay
- Cache miss
- Non-critical warnings

### Incident Response Procedures

#### P0: App Crashes on Startup

**Immediate Actions (0-2 minutes):**
```bash
# 1. Check crash logs
tail -100 /var/log/tab-organizer/app.log
# Android: adb logcat | grep -A 20 "AndroidRuntime"

# 2. Check for missing dependencies
ldd /opt/tab-organizer/flutter-app/build/linux/x64/release/bundle/tab_organizer

# 3. Check database corruption
sqlite3 ~/.local/share/tab-organizer/local.db "PRAGMA integrity_check;"

# 4. Attempt repair or restore
if [ $? -ne 0 ]; then
  cp ~/backups/tab-organizer/local-latest.db ~/.local/share/tab-organizer/local.db
fi
```

**Investigation (2-10 minutes):**
```bash
# Check system resources
df -h ~/.local/share/tab-organizer/
free -m

# Check permissions
ls -la ~/.local/share/tab-organizer/
ls -la ~/.config/tab-organizer/

# Check model file integrity
ls -lh ~/.local/share/tab-organizer/models/classifier.tflite
md5sum ~/.local/share/tab-organizer/models/classifier.tflite

# Check for conflicting processes
ps aux | grep -E "flutter|tab-organizer"
```

**Mitigation:**
```bash
# Option 1: Restore from backup
cp ~/backups/tab-organizer/local-latest.db ~/.local/share/tab-organizer/local.db
cp ~/backups/tab-organizer/preferences-latest.json ~/.config/tab-organizer/preferences.json

# Option 2: Clear and reinitialize
rm -rf ~/.local/share/tab-organizer/
rm -rf ~/.config/tab-organizer/
/opt/tab-organizer/bin/tab-organizer-cli init

# Option 3: Reinstall app
cd /opt/tab-organizer/flutter-app
flutter clean
flutter pub get
flutter build linux --release

# Verify recovery
cd /opt/tab-organizer/flutter-app && flutter run --release -d linux
```

#### P1: ML Model Classification Failures

**Investigation:**
```bash
# Check model file
ls -lh ~/.local/share/tab-organizer/models/classifier.tflite
md5sum ~/.local/share/tab-organizer/models/classifier.tflite

# Check classification logs
grep "Classification" /var/log/tab-organizer/ml-metrics.log | tail -50

# Test model inference manually
python3 << EOF
import tensorflow as tf
import numpy as np

interpreter = tf.lite.Interpreter(
    model_path="/home/user/.local/share/tab-organizer/models/classifier.tflite"
)
interpreter.allocate_tensors()

# Test with dummy input
input_details = interpreter.get_input_details()
dummy_input = np.random.rand(*input_details[0]['shape']).astype(np.float32)
interpreter.set_tensor(input_details[0]['index'], dummy_input)
interpreter.invoke()

output_details = interpreter.get_output_details()
output = interpreter.get_tensor(output_details[0]['index'])
print(f"Model output: {output}")
EOF
```

**Mitigation:**
```bash
# Rollback to previous working model
cp ~/.local/share/tab-organizer/models/backup/classifier-stable.tflite \
   ~/.local/share/tab-organizer/models/classifier.tflite

# Restart app
systemctl restart tab-organizer-sync
pkill -f "flutter.*tab-organizer"

# Monitor classification accuracy
tail -f /var/log/tab-organizer/ml-metrics.log | grep "Accuracy"

# If still failing, use fallback rule-based classifier
/opt/tab-organizer/bin/tab-organizer-cli config set classifier_mode fallback
systemctl restart tab-organizer-sync
```

#### P1: Sync Service Down

**Investigation:**
```bash
# Check sync service status
systemctl status tab-organizer-sync
journalctl -u tab-organizer-sync -n 100

# Check Firebase connectivity
curl -X GET "https://tab-organizer.firebaseio.com/.json?auth=$FIREBASE_TOKEN"

# Check network connectivity
ping -c 3 firebaseio.com

# Check authentication
cat ~/.config/tab-organizer/firebase-credentials.json | jq .
```

**Mitigation:**
```bash
# Restart sync service
systemctl restart tab-organizer-sync

# Check if it started successfully
systemctl status tab-organizer-sync

# If authentication issue, re-authenticate
/opt/tab-organizer/bin/tab-organizer-cli auth login

# If Firebase API issues, switch to local-only mode temporarily
/opt/tab-organizer/bin/tab-organizer-cli config set sync_mode local
systemctl restart tab-organizer-sync

# Monitor sync recovery
tail -f /var/log/tab-organizer/sync.log
```

#### P2: Memory Leak / High Memory Usage

**Investigation:**
```bash
# Check current memory usage
ps aux | grep "tab-organizer" | awk '{print $6/1024 " MB - " $11}'

# Monitor memory over time
watch -n 5 'ps aux | grep tab-organizer | awk "{print \$6/1024 \" MB\"}"'

# Check for memory-related errors
grep -i "memory\|oom" /var/log/tab-organizer/app.log | tail -20

# Check tab count
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT COUNT(*) as tab_count FROM tabs;"

# Check cache size
du -sh ~/.cache/tab-organizer/
```

**Mitigation:**
```bash
# Clear caches
rm -rf ~/.cache/tab-organizer/thumbnails/*
rm -rf ~/.cache/tab-organizer/ml-cache/*

# Limit tab history
sqlite3 ~/.local/share/tab-organizer/local.db \
  "DELETE FROM tabs WHERE last_accessed < datetime('now', '-30 days');"

# Restart app
pkill -f "flutter.*tab-organizer"
systemctl restart tab-organizer-sync

# Enable memory limit if available
# Edit systemd service file
sudo systemctl edit tab-organizer-sync
# Add: MemoryMax=512M

# Monitor memory after restart
watch -n 5 'ps aux | grep tab-organizer'
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > ~/incidents/tab-organizer/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Incident Report - Tab Organizer

**Date:** $(date)
**Severity:** P1
**Duration:** 20 minutes
**Affected Component:** ML Classification Service

## Timeline
- 14:00: Users reported inaccurate tab classifications
- 14:05: Confirmed ML model inference failing
- 14:10: Identified corrupted model file
- 14:15: Rolled back to stable model version
- 14:20: Service restored, accuracy back to normal

## Root Cause
Model file corruption during automatic update process

## Action Items
- [ ] Add model file integrity verification before deployment
- [ ] Implement automatic rollback on model performance degradation
- [ ] Add model health monitoring alerts
- [ ] Create model deployment checklist

EOF

# Update metrics
echo "$(date +%Y-%m-%d),P1,20,ml-model" >> ~/incidents/tab-organizer/incident-log.csv

# Review and update runbook if new procedures discovered
```

---

## Monitoring & Troubleshooting

### Essential Troubleshooting Commands

#### App Issues
```bash
# Check app status
pgrep -f "tab-organizer" || echo "App not running"
systemctl status tab-organizer-sync

# View logs
tail -f /var/log/tab-organizer/app.log
tail -f /var/log/tab-organizer/sync.log
tail -f /var/log/tab-organizer/ml-metrics.log

# Android logs
adb logcat | grep TabOrganizer

# Check database
sqlite3 ~/.local/share/tab-organizer/local.db "SELECT COUNT(*) FROM tabs;"
sqlite3 ~/.local/share/tab-organizer/local.db "PRAGMA integrity_check;"

# Check configuration
cat ~/.config/tab-organizer/preferences.json | jq .
```

#### ML Model Issues
```bash
# Test model inference
python3 /opt/tab-organizer/ai-model/scripts/test_inference.py \
  --model ~/.local/share/tab-organizer/models/classifier.tflite \
  --input "https://example.com Example Page"

# Check classification history
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT url, predicted_category, confidence, user_corrected
   FROM classifications ORDER BY timestamp DESC LIMIT 20;"

# Calculate accuracy
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT
     CAST(SUM(CASE WHEN user_corrected=0 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100 as accuracy
   FROM classifications
   WHERE timestamp > datetime('now', '-24 hours');"
```

#### Browser Extension Issues
```bash
# Check native messaging host
ps aux | grep native-host
tail -f /var/log/tab-organizer/native-host.log

# Test native messaging
echo '{"action": "getTabs"}' | /opt/tab-organizer/native-host/tab-organizer-host

# Check extension installation (Chrome)
ls -la ~/.config/google-chrome/Default/Extensions/ | grep tab-organizer

# Verify manifest
cat /opt/tab-organizer/browser-extensions/chrome-extension/manifest.json | jq .
```

#### Sync Issues
```bash
# Check sync queue
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT COUNT(*), sync_type, status FROM sync_queue GROUP BY sync_type, status;"

# Check Firebase connection
curl -X GET "https://tab-organizer.firebaseio.com/.json?auth=$FIREBASE_TOKEN" | jq .

# Force sync
curl -X POST http://localhost:8765/api/sync/trigger

# View sync conflicts
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT * FROM sync_conflicts WHERE resolved=0;"
```

### Common Issues & Solutions

#### Issue: "Classification accuracy degraded"

**Symptoms:**
- User reports incorrect categorization
- Accuracy metrics below 80%
- Frequent user corrections

**Diagnosis:**
```bash
# Check recent accuracy
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT
     CAST(SUM(CASE WHEN user_corrected=0 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100
   FROM classifications
   WHERE timestamp > datetime('now', '-24 hours');"

# Analyze misclassifications
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT url, predicted_category, correct_category
   FROM classifications
   WHERE user_corrected=1
   ORDER BY timestamp DESC LIMIT 20;"
```

**Solution:**
```bash
# Retrain model with user corrections
cd /opt/tab-organizer/ai-model
python3 scripts/retrain_with_corrections.py \
  --db ~/.local/share/tab-organizer/local.db \
  --output models/classifier-updated.tflite

# Test new model
python3 scripts/evaluate_model.py \
  --model models/classifier-updated.tflite \
  --test-data training-data/test-set.csv

# Deploy if improved
cp models/classifier-updated.tflite ~/.local/share/tab-organizer/models/classifier.tflite
systemctl restart tab-organizer-sync
```

---

#### Issue: "Browser extension not communicating"

**Symptoms:**
- Extension shows "disconnected" status
- Tabs not syncing to app
- Native messaging errors

**Diagnosis:**
```bash
# Check native host is running
ps aux | grep native-host

# Check native host manifest
cat ~/.config/google-chrome/NativeMessagingHosts/com.taborganizer.host.json

# Test native messaging
echo '{"action": "ping"}' | /opt/tab-organizer/native-host/tab-organizer-host

# Check extension permissions
# Navigate to chrome://extensions and check permissions
```

**Solution:**
```bash
# Restart native host
systemctl restart tab-organizer-native-host

# Reinstall native messaging manifest
/opt/tab-organizer/scripts/install-native-host.sh

# Reload browser extension
# Chrome: Navigate to chrome://extensions and click "Reload"

# Verify connection
tail -f /var/log/tab-organizer/native-host.log
# Then open/close a tab in browser and check logs
```

---

#### Issue: "Sync conflicts accumulating"

**Symptoms:**
- Multiple unresolved conflicts
- Data inconsistency across devices
- Sync queue backing up

**Diagnosis:**
```bash
# Count conflicts
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT COUNT(*) FROM sync_conflicts WHERE resolved=0;"

# Analyze conflict types
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT conflict_type, COUNT(*) FROM sync_conflicts WHERE resolved=0 GROUP BY conflict_type;"

# View specific conflicts
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT * FROM sync_conflicts WHERE resolved=0 LIMIT 5;" | jq .
```

**Solution:**
```bash
# Resolve all conflicts with merge strategy
/opt/tab-organizer/bin/tab-organizer-cli sync resolve-all --strategy merge

# Or resolve individually
for conflict_id in $(sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT id FROM sync_conflicts WHERE resolved=0;"); do
  /opt/tab-organizer/bin/tab-organizer-cli sync resolve \
    --conflict-id $conflict_id --strategy merge
done

# Force full resync if conflicts persist
/opt/tab-organizer/bin/tab-organizer-cli sync reset
systemctl restart tab-organizer-sync
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 15 minutes (local DB snapshots + cloud sync)
- **RTO** (Recovery Time Objective): 10 minutes (app reinstall + data restore)

### Backup Strategy

**Automated Backups:**
```bash
# Create backup script
cat > /opt/tab-organizer/scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/backups/tab-organizer
mkdir -p $BACKUP_DIR

# Backup database
cp ~/.local/share/tab-organizer/local.db \
   $BACKUP_DIR/local-$(date +%Y%m%d-%H%M).db

# Backup preferences
cp ~/.config/tab-organizer/preferences.json \
   $BACKUP_DIR/preferences-$(date +%Y%m%d-%H%M).json

# Backup model
cp ~/.local/share/tab-organizer/models/classifier.tflite \
   $BACKUP_DIR/model-$(date +%Y%m%d-%H%M).tflite

# Clean old backups (keep 30 days)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $(date)"
EOF

chmod +x /opt/tab-organizer/scripts/backup.sh

# Schedule via cron (every 6 hours)
(crontab -l 2>/dev/null; echo "0 */6 * * * /opt/tab-organizer/scripts/backup.sh") | crontab -
```

**Cloud Backup:**
```bash
# Firebase/Firestore automatically backs up synced data
# Verify cloud backup status
curl -X GET "https://tab-organizer.firebaseio.com/.json?auth=$FIREBASE_TOKEN" | jq .

# Export cloud data
/opt/tab-organizer/bin/tab-organizer-cli cloud-export \
  --output ~/backups/tab-organizer/cloud-export-$(date +%Y%m%d).json
```

### Disaster Recovery Procedures

#### Complete Data Recovery
```bash
# 1. Restore local database
cp ~/backups/tab-organizer/local-latest.db \
   ~/.local/share/tab-organizer/local.db

# 2. Restore preferences
cp ~/backups/tab-organizer/preferences-latest.json \
   ~/.config/tab-organizer/preferences.json

# 3. Restore model
cp ~/backups/tab-organizer/model-latest.tflite \
   ~/.local/share/tab-organizer/models/classifier.tflite

# 4. Restart services
systemctl restart tab-organizer-sync
pkill -f "tab-organizer"

# 5. Verify data
sqlite3 ~/.local/share/tab-organizer/local.db "SELECT COUNT(*) FROM tabs;"

# 6. Trigger sync
/opt/tab-organizer/bin/tab-organizer-cli sync --force
```

#### Recovery from Cloud
```bash
# If local data lost, restore from Firebase
/opt/tab-organizer/bin/tab-organizer-cli cloud-restore

# Monitor sync
tail -f /var/log/tab-organizer/sync.log

# Verify restoration
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT COUNT(*), category FROM tabs GROUP BY category;"
```

---

## Maintenance Procedures

### Routine Maintenance

#### Daily Tasks
```bash
# Check app health
systemctl status tab-organizer-sync
pgrep -f "tab-organizer" || echo "App not running"

# Check sync status
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT last_sync_time FROM sync_metadata ORDER BY last_sync_time DESC LIMIT 1;"

# Check error logs
tail -20 /var/log/tab-organizer/app.log | grep ERROR

# Monitor resource usage
ps aux | grep tab-organizer | awk '{print $6/1024 " MB"}'
```

#### Weekly Tasks
```bash
# Review classification accuracy
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT
     CAST(SUM(CASE WHEN user_corrected=0 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100
   FROM classifications
   WHERE timestamp > datetime('now', '-7 days');"

# Clean old data
sqlite3 ~/.local/share/tab-organizer/local.db \
  "DELETE FROM tabs WHERE closed_at < datetime('now', '-90 days');"

# Vacuum database
sqlite3 ~/.local/share/tab-organizer/local.db "VACUUM;"

# Review sync conflicts
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT COUNT(*) FROM sync_conflicts WHERE resolved=0;"
```

#### Monthly Tasks
```bash
# Update app dependencies
cd /opt/tab-organizer/flutter-app
flutter pub upgrade
flutter build linux --release

# Review and retrain ML model
cd /opt/tab-organizer/ai-model
python3 scripts/retrain_with_corrections.py

# Archive old logs
cd /var/log/tab-organizer
gzip app.log.1 sync.log.1 ml-metrics.log.1
mv *.gz archive/

# Verify backups
ls -lh ~/backups/tab-organizer/ | head -10
```

---

## Operational Best Practices

### Pre-Deployment Checklist
- [ ] All tests passing (`flutter test`)
- [ ] ML model validated
- [ ] Browser extensions tested on all browsers
- [ ] Database migrations tested
- [ ] Backup completed
- [ ] Rollback plan documented
- [ ] Firebase credentials valid

### Post-Deployment Checklist
- [ ] App launches successfully
- [ ] Classification working correctly
- [ ] Browser extension connected
- [ ] Sync service operational
- [ ] No errors in logs
- [ ] Resource usage normal
- [ ] Monitor for 1 hour

---

## Quick Reference Card

### Most Common Operations
```bash
# Check app status
systemctl status tab-organizer-sync
pgrep -f "tab-organizer"

# View logs
tail -f /var/log/tab-organizer/app.log

# Restart app
systemctl restart tab-organizer-sync

# Backup data
/opt/tab-organizer/scripts/backup.sh

# Force sync
/opt/tab-organizer/bin/tab-organizer-cli sync --force

# Check classification accuracy
sqlite3 ~/.local/share/tab-organizer/local.db \
  "SELECT CAST(SUM(CASE WHEN user_corrected=0 THEN 1 ELSE 0 END) AS REAL) / COUNT(*) * 100
   FROM classifications WHERE timestamp > datetime('now', '-24 hours');"
```

### Emergency Response
```bash
# P0: App crashed
cp ~/backups/tab-organizer/local-latest.db ~/.local/share/tab-organizer/local.db
systemctl restart tab-organizer-sync

# P1: ML model failing
cp ~/.local/share/tab-organizer/models/backup/classifier-stable.tflite \
   ~/.local/share/tab-organizer/models/classifier.tflite
systemctl restart tab-organizer-sync

# P1: Sync down
systemctl restart tab-organizer-sync
tail -f /var/log/tab-organizer/sync.log
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** AI/ML Automation Team
- **Review Schedule:** Quarterly or after major releases
- **Feedback:** Create issue or submit PR with updates
