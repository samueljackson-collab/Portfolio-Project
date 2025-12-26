#!/usr/bin/env node
/**
 * Wiki.js Content Exporter
 *
 * Exports all pages from Wiki.js via GraphQL API to local markdown files.
 *
 * Usage:
 *   WIKIJS_URL=http://localhost:3000 WIKIJS_TOKEN=your-token node export-from-wikijs.js
 */

require('dotenv').config();
const axios = require('axios');
const fs = require('fs-extra');
const path = require('path');

class WikiJSExporter {
  constructor(config) {
    this.apiUrl = config.apiUrl || process.env.WIKIJS_URL || 'http://localhost:3000';
    this.authToken = config.authToken || process.env.WIKIJS_TOKEN;

    if (!this.authToken) {
      throw new Error('API token required! Set WIKIJS_TOKEN environment variable.');
    }

    this.client = axios.create({
      baseURL: `${this.apiUrl}/graphql`,
      headers: {
        'Authorization': `Bearer ${this.authToken}`,
        'Content-Type': 'application/json'
      }
    });
  }

  /**
   * Fetch all pages from Wiki.js
   */
  async fetchAllPages() {
    const query = `
      query {
        pages {
          list {
            id
            path
            title
            description
            content
            contentType
            tags {
              tag
            }
            locale
            createdAt
            updatedAt
          }
        }
      }
    `;

    try {
      const response = await this.client.post('', { query });

      if (response.data.errors) {
        throw new Error(`GraphQL Error: ${JSON.stringify(response.data.errors)}`);
      }

      return response.data.data.pages.list;
    } catch (error) {
      console.error('❌ Error fetching pages:', error.response?.data || error.message);
      throw error;
    }
  }

  /**
   * Export pages to local directory
   */
  async exportToDirectory(outputDir) {
    console.log('🚀 Starting export from Wiki.js...\n');

    const pages = await this.fetchAllPages();
    console.log(`📚 Found ${pages.length} pages to export\n`);

    let exported = 0;
    let skipped = 0;

    for (const page of pages) {
      try {
        // Only export markdown content
        if (page.contentType !== 'markdown') {
          console.log(`⏭️  Skipped: ${page.title} (${page.contentType})`);
          skipped++;
          continue;
        }

        const filePath = this.getFilePath(outputDir, page.path);
        const content = this.formatMarkdown(page);

        // Ensure directory exists
        await fs.ensureDir(path.dirname(filePath));

        // Write file
        await fs.writeFile(filePath, content, 'utf8');
        console.log(`✅ Exported: ${page.title} → ${filePath}`);
        exported++;
      } catch (error) {
        console.error(`❌ Failed to export ${page.title}:`, error.message);
      }
    }

    console.log(`\n🎉 Export completed!`);
    console.log(`   ✅ Exported: ${exported} pages`);
    console.log(`   ⏭️  Skipped: ${skipped} pages`);
  }

  /**
   * Generate file path from Wiki.js path
   */
  getFilePath(baseDir, pagePath) {
    const cleanPath = pagePath.replace(/^\//, '');
    return path.join(baseDir, `${cleanPath}.md`);
  }

  /**
   * Format page as markdown with frontmatter
   */
  formatMarkdown(page) {
    const tags = page.tags.map(t => t.tag).join(', ');
    const frontmatter = `---
title: ${page.title}
description: ${page.description || ''}
tags: ${tags}
locale: ${page.locale}
created: ${page.createdAt}
updated: ${page.updatedAt}
---

`;

    return frontmatter + `# ${page.title}\n\n${page.content}`;
  }
}

// Main execution
async function main() {
  try {
    const config = {
      apiUrl: process.env.WIKIJS_URL,
      authToken: process.env.WIKIJS_TOKEN
    };

    const exporter = new WikiJSExporter(config);
    const outputDir = path.join(__dirname, '../exports', `export-${Date.now()}`);

    await exporter.exportToDirectory(outputDir);
  } catch (error) {
    console.error('Fatal error:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { WikiJSExporter };
