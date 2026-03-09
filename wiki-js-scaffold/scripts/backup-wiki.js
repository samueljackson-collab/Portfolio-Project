#!/usr/bin/env node
/**
 * Wiki.js Backup Script
 *
 * Creates a complete backup of Wiki.js including database and content.
 * Supports both local and Docker deployments.
 *
 * Usage:
 *   node backup-wiki.js [--docker] [--output-dir ./backups]
 */

require('dotenv').config();
const { execSync } = require('child_process');
const fs = require('fs-extra');
const path = require('path');

class WikiBackup {
  constructor(options = {}) {
    this.isDocker = options.docker || false;
    this.outputDir = options.outputDir || path.join(__dirname, '../backups');
    this.timestamp = this.getTimestamp();
    this.backupName = `wiki-backup-${this.timestamp}`;
  }

  /**
   * Get formatted timestamp
   */
  getTimestamp() {
    const now = new Date();
    return now.toISOString()
      .replace(/:/g, '-')
      .replace(/\..+/, '')
      .replace('T', '_');
  }

  /**
   * Execute command and return output
   */
  exec(command, options = {}) {
    try {
      console.log(`🔧 Running: ${command}`);
      return execSync(command, {
        encoding: 'utf8',
        stdio: options.silent ? 'pipe' : 'inherit',
        ...options
      });
    } catch (error) {
      console.error(`❌ Command failed: ${command}`);
      throw error;
    }
  }

  /**
   * Create backup directory
   */
  async createBackupDir() {
    const backupPath = path.join(this.outputDir, this.backupName);
    await fs.ensureDir(backupPath);
    console.log(`📁 Created backup directory: ${backupPath}`);
    return backupPath;
  }

  /**
   * Backup PostgreSQL database
   */
  async backupDatabase(backupPath) {
    console.log('\n📊 Backing up database...');
    const dbFile = path.join(backupPath, 'database.sql');

    if (this.isDocker) {
      // Docker deployment
      const dbUser = process.env.DB_USER || 'wikijs';
      const dbName = process.env.DB_NAME || 'wiki';
      const dockerComposeFile = path.join(__dirname, '../docker/docker-compose.yml');
      const command = `docker-compose -f ${dockerComposeFile} exec -T db pg_dump -U ${dbUser} ${dbName} > ${dbFile}`;
      this.exec(command);
    } else {
      // Local deployment
      const dbUrl = process.env.DATABASE_URL || process.env.DB_CONNECTION_STRING;
      if (!dbUrl) {
        console.warn('⚠️  No database connection string found. Skipping database backup.');
        return;
      }
      const command = `pg_dump ${dbUrl} > ${dbFile}`;
      this.exec(command);
    }

    const stats = await fs.stat(dbFile);
    console.log(`✅ Database backed up: ${(stats.size / 1024).toFixed(2)} KB`);
  }

  /**
   * Backup content files
   */
  async backupContent(backupPath) {
    console.log('\n📄 Backing up content files...');

    const contentDir = path.join(__dirname, '../content');
    const contentBackup = path.join(backupPath, 'content');

    if (await fs.pathExists(contentDir)) {
      await fs.copy(contentDir, contentBackup);
      console.log(`✅ Content files backed up to: ${contentBackup}`);
    } else {
      console.warn('⚠️  Content directory not found. Skipping content backup.');
    }
  }

  /**
   * Backup configuration files
   */
  async backupConfig(backupPath) {
    console.log('\n⚙️  Backing up configuration...');

    const configBackup = path.join(backupPath, 'config');
    await fs.ensureDir(configBackup);

    const configFiles = [
      '.env',
      'docker/docker-compose.yml',
      'docker/nginx.conf'
    ];

    for (const file of configFiles) {
      const filePath = path.join(__dirname, '..', file);
      if (await fs.pathExists(filePath)) {
        const destPath = path.join(configBackup, path.basename(file));
        await fs.copy(filePath, destPath);
        console.log(`  ✅ Backed up: ${file}`);
      }
    }
  }

  /**
   * Create backup metadata
   */
  async createMetadata(backupPath) {
    const metadata = {
      timestamp: this.timestamp,
      date: new Date().toISOString(),
      type: this.isDocker ? 'docker' : 'local',
      version: this.getWikiVersion(),
      files: await this.getBackupContents(backupPath)
    };

    const metadataFile = path.join(backupPath, 'backup-metadata.json');
    await fs.writeJson(metadataFile, metadata, { spaces: 2 });
    console.log('\n📋 Created backup metadata');
  }

  /**
   * Get Wiki.js version
   */
  getWikiVersion() {
    try {
      if (this.isDocker) {
        return this.exec('docker-compose -f docker/docker-compose.yml exec -T wiki cat /wiki/package.json | grep version', { silent: true });
      }
      return 'unknown';
    } catch {
      return 'unknown';
    }
  }

  /**
   * Get list of backed up files
   */
  async getBackupContents(backupPath) {
    const files = await fs.readdir(backupPath);
    const contents = {};

    for (const file of files) {
      const filePath = path.join(backupPath, file);
      const stats = await fs.stat(filePath);
      contents[file] = {
        size: stats.size,
        isDirectory: stats.isDirectory()
      };
    }

    return contents;
  }

  /**
   * Perform complete backup
   */
  async performBackup() {
    console.log('🚀 Starting Wiki.js backup...\n');
    console.log(`   Backup name: ${this.backupName}`);
    console.log(`   Output directory: ${this.outputDir}`);
    console.log(`   Mode: ${this.isDocker ? 'Docker' : 'Local'}\n`);

    try {
      const backupPath = await this.createBackupDir();

      await this.backupDatabase(backupPath);
      await this.backupContent(backupPath);
      await this.backupConfig(backupPath);
      await this.createMetadata(backupPath);

      console.log('\n🎉 Backup completed successfully!');
      console.log(`   Location: ${backupPath}`);

      // Get total backup size
      const size = await this.getDirectorySize(backupPath);
      console.log(`   Total size: ${(size / 1024 / 1024).toFixed(2)} MB`);
    } catch (error) {
      console.error('\n❌ Backup failed:', error.message);
      process.exit(1);
    }
  }

  /**
   * Calculate directory size
   */
  async getDirectorySize(dir) {
    let size = 0;
    const files = await fs.readdir(dir);

    for (const file of files) {
      const filePath = path.join(dir, file);
      const stats = await fs.stat(filePath);

      if (stats.isDirectory()) {
        size += await this.getDirectorySize(filePath);
      } else {
        size += stats.size;
      }
    }

    return size;
  }
}

// Parse command line arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {};

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--docker') {
      options.docker = true;
    } else if (args[i] === '--output-dir' && args[i + 1]) {
      options.outputDir = args[i + 1];
      i++;
    }
  }

  return options;
}

// Main execution
async function main() {
  const options = parseArgs();
  const backup = new WikiBackup(options);
  await backup.performBackup();
}

if (require.main === module) {
  main();
}

module.exports = { WikiBackup };
