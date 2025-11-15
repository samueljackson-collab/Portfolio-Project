#!/usr/bin/env node
/**
 * Wiki.js Deployment Verification Script
 *
 * Verifies that all components of the Wiki.js deployment are properly configured
 * and operational before going live.
 */

// Load dotenv if available
try {
  require('dotenv').config();
} catch (e) {
  // dotenv not installed, environment variables won't be loaded from .env
}

const fs = require('fs').promises;
const fsSync = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class DeploymentVerifier {
  constructor() {
    this.errors = [];
    this.warnings = [];
    this.checks = 0;
    this.passed = 0;
  }

  /**
   * Log check result
   */
  check(name, passed, message) {
    this.checks++;
    if (passed) {
      this.passed++;
      console.log(`✅ ${name}`);
    } else {
      console.log(`❌ ${name}`);
      this.errors.push(`${name}: ${message}`);
    }
  }

  /**
   * Log warning
   */
  warn(name, message) {
    console.log(`⚠️  ${name}`);
    this.warnings.push(`${name}: ${message}`);
  }

  /**
   * Check if file exists
   */
  fileExists(filepath) {
    return fsSync.existsSync(filepath);
  }

  /**
   * Run command and check success
   */
  runCommand(command) {
    try {
      execSync(command, { stdio: 'pipe' });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Verify environment configuration
   */
  async verifyEnvironment() {
    console.log('\n🔧 Environment Configuration\n');

    // Check .env file
    const envExists = this.fileExists('.env');
    this.check('Environment file (.env)', envExists, '.env file not found');

    if (envExists) {
      const dbPass = process.env.DB_PASSWORD;
      this.check('DB_PASSWORD set', !!dbPass, 'Database password not configured');

      const domain = process.env.DOMAIN;
      if (!domain || domain === 'wiki.example.com') {
        this.warn('Domain configuration', 'Using example domain');
      }

      const wikijsToken = process.env.WIKIJS_TOKEN;
      if (!wikijsToken) {
        this.warn('Wiki.js API token', 'Not configured (needed for content import)');
      }
    }
  }

  /**
   * Verify Docker setup
   */
  async verifyDocker() {
    console.log('\n🐳 Docker Setup\n');

    // Check Docker
    const dockerInstalled = this.runCommand('docker --version');
    this.check('Docker installed', dockerInstalled, 'Docker not found');

    // Check Docker Compose
    const composeInstalled = this.runCommand('docker-compose --version');
    this.check('Docker Compose installed', composeInstalled, 'Docker Compose not found');

    // Check docker-compose.yml
    const composeExists = this.fileExists('docker/docker-compose.yml');
    this.check('docker-compose.yml exists', composeExists, 'Docker Compose file not found');

    // Check nginx.conf
    const nginxExists = this.fileExists('docker/nginx.conf');
    this.check('nginx.conf exists', nginxExists, 'Nginx configuration not found');
  }

  /**
   * Verify scripts
   */
  async verifyScripts() {
    console.log('\n📜 Scripts\n');

    const scripts = [
      'import-to-wikijs.js',
      'export-from-wikijs.js',
      'backup-wiki.js',
      'backup-db.js',
      'validate-content.js'
    ];

    for (const script of scripts) {
      const exists = this.fileExists(`scripts/${script}`);
      this.check(`Script: ${script}`, exists, `${script} not found`);
    }
  }

  /**
   * Verify content structure
   */
  async verifyContent() {
    console.log('\n📚 Content Structure\n');

    const contentDirs = [
      '01-setup-fundamentals',
      '02-git-fundamentals',
      '03-documentation',
      '04-real-world-projects',
      '05-github-platform',
      '06-advanced-topics',
      '07-next-steps'
    ];

    let totalLessons = 0;

    for (const dir of contentDirs) {
      const dirPath = `content/${dir}`;
      const exists = this.fileExists(dirPath);

      if (exists) {
        const files = await fs.readdir(dirPath);
        const mdFiles = files.filter(f => f.endsWith('.md'));
        totalLessons += mdFiles.length;
        this.check(`Content: ${dir}`, mdFiles.length > 0, `No lessons in ${dir}`);
      } else {
        this.check(`Content: ${dir}`, false, `Directory not found: ${dir}`);
      }
    }

    console.log(`\n📊 Total lessons found: ${totalLessons}`);
  }

  /**
   * Verify documentation
   */
  async verifyDocumentation() {
    console.log('\n📖 Documentation\n');

    const docs = ['README.md', 'SETUP-GUIDE.md', '.env.example'];

    for (const doc of docs) {
      const exists = this.fileExists(doc);
      this.check(`Documentation: ${doc}`, exists, `${doc} not found`);
    }
  }

  /**
   * Verify Node.js setup
   */
  async verifyNode() {
    console.log('\n📦 Node.js Setup\n');

    // Check Node.js
    const nodeInstalled = this.runCommand('node --version');
    this.check('Node.js installed', nodeInstalled, 'Node.js not found');

    // Check package.json
    const packageExists = this.fileExists('package.json');
    this.check('package.json exists', packageExists, 'package.json not found');

    // Check node_modules
    const modulesExists = this.fileExists('node_modules');
    if (!modulesExists) {
      this.warn('Dependencies', 'node_modules not found. Run: npm install');
    }
  }

  /**
   * Print summary
   */
  printSummary() {
    console.log('\n' + '='.repeat(60));
    console.log('📊 Verification Summary');
    console.log('='.repeat(60));
    console.log(`   Total checks: ${this.checks}`);
    console.log(`   ✅ Passed: ${this.passed}`);
    console.log(`   ❌ Failed: ${this.errors.length}`);
    console.log(`   ⚠️  Warnings: ${this.warnings.length}`);

    if (this.errors.length > 0) {
      console.log('\n❌ Errors:');
      this.errors.forEach(error => console.log(`   - ${error}`));
    }

    if (this.warnings.length > 0) {
      console.log('\n⚠️  Warnings:');
      this.warnings.forEach(warning => console.log(`   - ${warning}`));
    }

    console.log('='.repeat(60));

    if (this.errors.length === 0) {
      console.log('\n🎉 All critical checks passed! Deployment is ready.');
      console.log('\n📋 Next steps:');
      console.log('   1. Review warnings (if any)');
      console.log('   2. Run: npm run dev');
      console.log('   3. Access: http://localhost:3000');
      console.log('   4. Configure Wiki.js admin account');
      console.log('   5. Run: npm run import\n');
      return 0;
    } else {
      console.log('\n❌ Deployment verification failed. Fix errors above.\n');
      return 1;
    }
  }

  /**
   * Run all verifications
   */
  async verify() {
    console.log('🚀 Wiki.js Deployment Verification\n');
    console.log('Checking all components...\n');

    await this.verifyEnvironment();
    await this.verifyDocker();
    await this.verifyNode();
    await this.verifyScripts();
    await this.verifyContent();
    await this.verifyDocumentation();

    return this.printSummary();
  }
}

// Main execution
async function main() {
  const verifier = new DeploymentVerifier();
  const exitCode = await verifier.verify();
  process.exit(exitCode);
}

if (require.main === module) {
  main();
}

module.exports = { DeploymentVerifier };
