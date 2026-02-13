# Content Restore Guide

1. **Identify Backup Artifact**
   - Locate the latest content export (JSON/CSV) from object storage.
   - Validate checksum and timestamp before proceeding.
2. **Prepare Environment**
   - Ensure backend service is running in maintenance mode.
   - Create a snapshot of the target database for rollback if needed.
3. **Restore Procedure**
   - Use the `/api/content` endpoints or administrative script to re-import content.
   - Verify record counts against the backup manifest.
4. **Post-Restore Validation**
   - Run automated smoke tests to confirm CRUD operations.
   - Exit maintenance mode and notify stakeholders.
