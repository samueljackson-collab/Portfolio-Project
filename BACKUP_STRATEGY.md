# ElderPhoto Backup Strategy

## Overview

ElderPhoto implements a **3-2-1 backup strategy** to ensure photos are never lost:

- **3 copies** of data: 1 primary + 2 backups
- **2 different storage types**: Local SSD (fast) + Remote HDD (reliable)
- **1 offsite copy**: Geographically separated for disaster recovery

## Backup Locations

### Primary Storage (Home Server)
- **Location**: Home server
- **Purpose**: Fast access for day-to-day operations
- **Technology**: Local SSD or fast HDD
- **Path**: `/mnt/elderphoto/primary`

### Backup #1 (Aunt's House)
- **Location**: Aunt's house (local network)
- **Purpose**: Local backup for quick recovery
- **Technology**: Network-attached storage (NAS) or external drive
- **Connection**: SMB share or mounted drive
- **Path**: `/mnt/elderphoto/backup-aunt`

### Backup #2 (Dad's House - Tucson, AZ)
- **Location**: Dad's house in Tucson, Arizona
- **Purpose**: Offsite backup for disaster recovery
- **Technology**: Remote server or NAS
- **Connection**: SSH/rsync over internet
- **Path**: `/mnt/elderphoto/backup-dad`

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Primary Storage                         │
│                    (Home Server)                           │
│              /mnt/elderphoto/primary                       │
│                                                             │
│  ┌───────────────────────────────────────────────┐         │
│  │  users/                                       │         │
│  │  ├── {user_id}/                              │         │
│  │  │   ├── 2024/                               │         │
│  │  │   │   ├── 11/                            │         │
│  │  │   │   │   ├── photo1_abc123.jpg         │         │
│  │  │   │   │   └── photo2_def456.jpg         │         │
│  │  │   │   └── 12/                            │         │
│  │  │   └── thumbnails/                        │         │
│  │  │       ├── 2024/                          │         │
│  │  │       │   └── 11/                        │         │
│  └───────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
         ▲                │                │
         │ Auto-backup    │ rsync          │ rsync
         │ on upload      │                │
         │                ▼                ▼
    ┌─────────┐    ┌──────────────┐  ┌──────────────┐
    │ Upload  │    │   Backup #1  │  │   Backup #2  │
    │ Photos  │    │  (Aunt's     │  │  (Dad's      │
    └─────────┘    │   House)     │  │   Tucson)    │
                   │              │  │              │
                   │  Local/NFS   │  │ Remote/SSH   │
                   └──────────────┘  └──────────────┘
```

## How It Works

### Automatic Backup (Real-time)

When a photo is uploaded:

1. **Photo saved to primary storage** → `/mnt/elderphoto/primary/users/{user_id}/2024/11/photo.jpg`
2. **Thumbnail generated and saved** → `/mnt/elderphoto/primary/users/{user_id}/thumbnails/2024/11/photo.jpg`
3. **Backup triggered automatically** (non-blocking):
   - Copy to Aunt's house (local network)
   - rsync to Dad's house (remote)
4. **User sees success immediately** (backup happens in background)

### Scheduled Sync (Daily/Weekly)

Cron job runs daily for verification and catch-up:

```bash
# Daily incremental sync at 2 AM
0 2 * * * cd /path/to/backend && python scripts/backup_sync.py --incremental

# Weekly full sync and verification on Sundays at 3 AM
0 3 * * 0 cd /path/to/backend && python scripts/backup_sync.py --full --verify
```

## Configuration

### Environment Variables

Add to `/home/user/Portfolio-Project/backend/.env`:

```bash
# Primary Storage
PRIMARY_STORAGE_PATH=/mnt/elderphoto/primary

# Auto-backup on upload (true/false)
AUTO_BACKUP_ENABLED=true

# Backup #1: Aunt's House
BACKUP_AUNT_ENABLED=true
BACKUP_AUNT_PATH=/mnt/elderphoto/backup-aunt
BACKUP_AUNT_REMOTE=false    # false for local/NFS mount
# BACKUP_AUNT_SSH_HOST=aunts-nas.local   # Only if using SSH
# BACKUP_AUNT_SSH_USER=elderphoto        # Only if using SSH

# Backup #2: Dad's House (Tucson)
BACKUP_DAD_ENABLED=true
BACKUP_DAD_PATH=/mnt/elderphoto/backup-dad
BACKUP_DAD_REMOTE=true      # true for remote/SSH
BACKUP_DAD_SSH_HOST=dads-server.example.com
BACKUP_DAD_SSH_USER=elderphoto
```

### Setting Up Backup Locations

#### Aunt's House (Local Network)

**Option 1: NFS Mount**
```bash
# On home server, mount aunt's NAS
sudo mkdir -p /mnt/elderphoto/backup-aunt
sudo mount -t nfs aunts-nas.local:/elderphoto /mnt/elderphoto/backup-aunt

# Add to /etc/fstab for automatic mounting
aunts-nas.local:/elderphoto /mnt/elderphoto/backup-aunt nfs defaults 0 0
```

**Option 2: SMB/CIFS Mount**
```bash
# Mount Windows/Samba share
sudo mount -t cifs //aunts-nas.local/elderphoto /mnt/elderphoto/backup-aunt \
  -o username=elderphoto,password=PASSWORD
```

#### Dad's House (Remote - Tucson)

**SSH Key Setup** (passwordless rsync):
```bash
# Generate SSH key for automatic backups
ssh-keygen -t ed25519 -f ~/.ssh/elderphoto_backup -N ""

# Copy to dad's server
ssh-copy-id -i ~/.ssh/elderphoto_backup.pub elderphoto@dads-server.example.com

# Test connection
ssh -i ~/.ssh/elderphoto_backup elderphoto@dads-server.example.com
```

**SSH Config** (`~/.ssh/config`):
```
Host dads-server
    HostName dads-server.example.com
    User elderphoto
    IdentityFile ~/.ssh/elderphoto_backup
    Port 22
    Compression yes
```

## Usage

### Manual Operations

#### Check Backup Status
```bash
cd /home/user/Portfolio-Project/backend

# Quick status check
python scripts/backup_sync.py --status

# API endpoint (requires authentication)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/backup/status
```

#### Run Full Backup
```bash
# Interactive full sync
python scripts/backup_sync.py --full

# With verification
python scripts/backup_sync.py --full --verify
```

#### Run Incremental Backup
```bash
# Daily incremental (faster)
python scripts/backup_sync.py --incremental
```

#### Verify Backups
```bash
# Verify without syncing
python scripts/backup_sync.py --verify-only
```

### API Endpoints

#### Get Backup Status
```http
GET /backup/status
Authorization: Bearer YOUR_TOKEN
```

Response:
```json
{
  "timestamp": "2025-11-12T10:30:00",
  "primary": {
    "name": "Home Server",
    "path": "/mnt/elderphoto/primary",
    "accessible": true
  },
  "backups": [
    {
      "name": "Aunt's House",
      "enabled": true,
      "remote": false,
      "accessible": true
    },
    {
      "name": "Dad's House (Tucson)",
      "enabled": true,
      "remote": true,
      "ssh_host": "dads-server.example.com",
      "accessible": true
    }
  ]
}
```

#### Health Check (No Auth Required)
```http
GET /backup/health
```

Response:
```json
{
  "health": "healthy",
  "message": "All backup locations accessible",
  "primary_accessible": true,
  "backups_accessible": "2/2",
  "timestamp": "2025-11-12T10:30:00"
}
```

## Monitoring & Alerts

### Health Check Monitoring

Use the `/backup/health` endpoint with monitoring tools:

**Nagios/Icinga:**
```bash
#!/bin/bash
# Check ElderPhoto backup health
HEALTH=$(curl -s http://localhost:8000/backup/health | jq -r '.health')

if [ "$HEALTH" = "healthy" ]; then
  echo "OK: All backups accessible"
  exit 0
elif [ "$HEALTH" = "degraded" ]; then
  echo "WARNING: Some backups not accessible"
  exit 1
else
  echo "CRITICAL: Backup system failure"
  exit 2
fi
```

**Prometheus Monitoring:**
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'elderphoto-backup'
    metrics_path: '/backup/health'
    static_configs:
      - targets: ['localhost:8000']
```

### Email Alerts

Add to cron for daily email reports:

```bash
# Daily backup report via email
0 4 * * * cd /path/to/backend && \
  python scripts/backup_sync.py --status | \
  mail -s "ElderPhoto Backup Status" admin@example.com
```

## Recovery Procedures

### Scenario 1: Primary Storage Failure

If home server fails, recover from backups:

**From Aunt's House (Fast Recovery):**
```bash
# Mount aunt's backup as primary
sudo umount /mnt/elderphoto/primary
sudo mount -t nfs aunts-nas.local:/elderphoto /mnt/elderphoto/primary

# Or copy data back
rsync -av /mnt/elderphoto/backup-aunt/ /mnt/elderphoto/primary/
```

**From Dad's House (Remote Recovery):**
```bash
# Sync from dad's server
rsync -avz elderphoto@dads-server.example.com:/mnt/elderphoto/backup-dad/ \
  /mnt/elderphoto/primary/
```

### Scenario 2: Individual Photo Recovery

Restore specific photo from backup:

```bash
# Find photo in backup
PHOTO_PATH="users/abc-123/2024/11/photo_xyz.jpg"

# Copy from aunt's backup
cp /mnt/elderphoto/backup-aunt/$PHOTO_PATH \
   /mnt/elderphoto/primary/$PHOTO_PATH

# Or from dad's backup
rsync -av elderphoto@dads-server.example.com:/mnt/elderphoto/backup-dad/$PHOTO_PATH \
  /mnt/elderphoto/primary/$PHOTO_PATH
```

### Scenario 3: Complete Disaster (All Locations Lost)

**Prevention is key!** The 3-2-1 strategy makes this extremely unlikely.

If all backups are lost:
1. Photos are gone (no recovery possible)
2. This requires simultaneous failure of:
   - Home server
   - Aunt's house storage
   - Dad's house in Tucson

**Risk Mitigation:**
- Test backups monthly
- Monitor backup health daily
- Consider cloud backup as 4th location

## Backup Verification

### Automated Verification

Run weekly to verify backup integrity:

```bash
# Verify sample of photos (first 100)
python scripts/backup_sync.py --verify-only
```

### Manual Spot Check

```bash
# Check specific photo exists in all locations
PHOTO="users/abc-123/2024/11/vacation_photo.jpg"

# Primary
ls /mnt/elderphoto/primary/$PHOTO

# Aunt's
ls /mnt/elderphoto/backup-aunt/$PHOTO

# Dad's (remote)
ssh elderphoto@dads-server.example.com \
  "ls /mnt/elderphoto/backup-dad/$PHOTO"
```

### Checksum Verification

For critical verification, compare file hashes:

```bash
# Get SHA256 from all locations
sha256sum /mnt/elderphoto/primary/$PHOTO
sha256sum /mnt/elderphoto/backup-aunt/$PHOTO
ssh dads-server "sha256sum /mnt/elderphoto/backup-dad/$PHOTO"

# All three should match
```

## Storage Requirements

### Estimating Space Needed

**Per Photo:**
- Original: ~5MB (12MP camera)
- Thumbnail: ~100KB

**For 1000 photos:**
- Originals: ~5GB
- Thumbnails: ~100MB
- Total: ~5.1GB

**Recommended Storage:**
- **Home Server**: 500GB - 1TB SSD
- **Aunt's Backup**: 500GB - 1TB HDD (NAS)
- **Dad's Backup**: 500GB - 1TB HDD

**For 10,000 photos:** Scale to 1-2TB per location

## Performance Considerations

### Upload Performance

- **Primary save**: Instant (local SSD)
- **Thumbnail generation**: <1 second
- **Backup to aunt**: 1-2 seconds (local network)
- **Backup to dad**: 5-30 seconds (internet speed dependent)

**User experience:** Upload returns immediately; backups happen in background.

### Sync Performance

**Incremental Sync:**
- **Local (Aunt's)**: ~50-100 MB/s
- **Remote (Dad's)**: ~1-10 MB/s (depends on upload speed)

**Full Sync (1000 photos):**
- **To Aunt's**: ~1-2 minutes
- **To Dad's**: ~10-50 minutes

## Troubleshooting

### Common Issues

#### Backup Location Not Accessible

**Check:**
```bash
# Test primary storage
ls /mnt/elderphoto/primary

# Test aunt's storage
ls /mnt/elderphoto/backup-aunt

# Test dad's storage (remote)
ssh dads-server "ls /mnt/elderphoto/backup-dad"
```

**Fix:**
- Verify network connectivity
- Check mount points (`mount | grep elderphoto`)
- Verify SSH keys for remote backups
- Check disk space (`df -h`)

#### Backup Sync Slow

**Causes:**
- Network congestion
- Too many files at once
- Insufficient bandwidth to remote location

**Solutions:**
- Run sync during off-peak hours (2-4 AM)
- Use `--incremental` instead of `--full`
- Enable rsync compression (already enabled)
- Consider rate limiting for remote sync

#### Backup Failed - Disk Full

**Check space:**
```bash
df -h /mnt/elderphoto/backup-aunt
df -h /mnt/elderphoto/backup-dad
```

**Fix:**
- Add more storage
- Clean up old/deleted photos
- Implement retention policy (keep last N days)

## Best Practices

1. **Test restores monthly** - Don't just backup, verify you can restore
2. **Monitor daily** - Check backup health endpoint
3. **Automate everything** - Use cron for scheduled tasks
4. **Document changes** - Update this file when changing backup locations
5. **Secure SSH keys** - Use passphrase-protected keys for production
6. **Rotate backup media** - Replace drives every 3-5 years
7. **Keep offsite current** - Don't let remote backup fall behind by days

## Future Enhancements

### Planned Features

- **Incremental tracking**: Only sync files modified since last run
- **Deduplication**: Save space by detecting duplicate photos
- **Compression**: Compress old photos (>1 year) to save space
- **Cloud backup**: Add AWS S3/Glacier as 4th backup location
- **Backup versioning**: Keep multiple versions of edited photos
- **Bandwidth throttling**: Limit sync speed to not saturate connection

### Optional 4th Backup (Cloud)

For extra security, consider cloud backup:

```bash
# AWS S3 Glacier (low cost, slow retrieval)
aws s3 sync /mnt/elderphoto/primary/ \
  s3://elderphoto-backup/primary/ \
  --storage-class GLACIER

# Backblaze B2 (affordable cloud storage)
b2 sync /mnt/elderphoto/primary/ b2://elderphoto-backup/
```

## Summary

ElderPhoto's backup strategy ensures:

✅ **Photos never lost** - 3 copies in 2 locations
✅ **Quick recovery** - Local backup at aunt's house
✅ **Disaster recovery** - Offsite backup in Tucson
✅ **Automatic** - Backups happen on upload + daily sync
✅ **Monitored** - Health checks and alerts
✅ **Verified** - Regular integrity checks

Your precious memories are safe! 📷✨

---

**Last Updated:** 2025-11-12
**Maintainer:** Portfolio Project
**Support:** See ELDERPHOTO_README.md for contact info
