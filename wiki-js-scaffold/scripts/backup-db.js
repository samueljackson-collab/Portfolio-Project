#!/usr/bin/env node
/**
 * Database Backup Script (Cross-platform)
 *
 * Creates a PostgreSQL database backup with timestamped filename.
 * Works on Windows, macOS, and Linux.
 *
 * Usage:
 *   node backup-db.js
 */

require('dotenv').config();
const { execSync } = require('child_process');
const fs = require('fs-extra');
const path = require('path');

/**
 * Get formatted timestamp
 */
function getTimestamp() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');

  return `${year}${month}${day}-${hours}${minutes}${seconds}`;
}

/**
 * Ensure backups directory exists
 */
async function ensureBackupsDir() {
  const backupsDir = path.join(__dirname, '../backups');
  await fs.ensureDir(backupsDir);
  return backupsDir;
}

/**
 * Perform database backup
 */
async function backupDatabase() {
  try {
    console.log('🚀 Starting database backup...\n');

    // Ensure backups directory exists
    const backupsDir = await ensureBackupsDir();

    // Generate timestamped filename
    const timestamp = getTimestamp();
    const filename = `wiki-${timestamp}.sql`;
    const filepath = path.join(backupsDir, filename);

    // Get database connection info
    const dbUser = process.env.DB_USER || 'wikijs';
    const dbName = process.env.DB_NAME || 'wiki';

    console.log(`   Database: ${dbName}`);
    console.log(`   User: ${dbUser}`);
    console.log(`   Output: ${filepath}\n`);

    // Execute pg_dump via docker-compose
    const command = `docker-compose -f docker/docker-compose.yml exec -T db pg_dump -U ${dbUser} ${dbName}`;

    console.log('📊 Running pg_dump...');
    const output = execSync(command, { encoding: 'utf8' });

    // Write output to file
    await fs.writeFile(filepath, output, 'utf8');

    // Get file size
    const stats = await fs.stat(filepath);
    const sizeKB = (stats.size / 1024).toFixed(2);

    console.log('✅ Backup completed successfully!');
    console.log(`   File: ${filename}`);
    console.log(`   Size: ${sizeKB} KB`);
    console.log(`   Location: ${filepath}\n`);

    // List recent backups
    await listRecentBackups(backupsDir);

  } catch (error) {
    console.error('❌ Backup failed:', error.message);
    process.exit(1);
  }
}

/**
 * List recent backups
 */
async function listRecentBackups(backupsDir) {
  try {
    const files = await fs.readdir(backupsDir);
    const sqlFiles = files
      .filter(f => f.endsWith('.sql'))
      .sort()
      .reverse()
      .slice(0, 5);

    if (sqlFiles.length > 0) {
      console.log('📁 Recent backups:');
      for (const file of sqlFiles) {
        const filepath = path.join(backupsDir, file);
        const stats = await fs.stat(filepath);
        const sizeKB = (stats.size / 1024).toFixed(2);
        console.log(`   - ${file} (${sizeKB} KB)`);
      }
    }
  } catch (error) {
    // Silently fail if we can't list backups
  }
}

// Run backup
backupDatabase();
