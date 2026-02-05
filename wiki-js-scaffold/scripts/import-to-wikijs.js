#!/usr/bin/env node
/**
 * Wiki.js Content Importer
 *
 * Automated script to import markdown content into Wiki.js via API.
 * Scans content directory and creates pages with proper hierarchy.
 *
 * Usage:
 *   WIKIJS_URL=http://localhost:3000 WIKIJS_TOKEN=your-token node import-to-wikijs.js
 */

require('dotenv').config();
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');

class WikiJSImporter {
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
   * Create a new page in Wiki.js using GraphQL mutation
   */
  async createPage(pageData) {
    const mutation = `
      mutation Page {
        pages {
          create(
            content: ${JSON.stringify(pageData.content)},
            description: ${JSON.stringify(pageData.description)},
            editor: "markdown",
            isPrivate: false,
            isPublished: true,
            locale: ${JSON.stringify(process.env.LOCALE || "en")},
            path: ${JSON.stringify(pageData.path)},
            tags: ${JSON.stringify(pageData.tags)},
            title: ${JSON.stringify(pageData.title)}
          ) {
            responseResult {
              succeeded
              errorCode
              slug
              message
            }
            page {
              id
              path
              title
            }
          }
        }
      }
    `;

    try {
      const response = await this.client.post('', { query: mutation });

      if (response.data.data.pages.create.responseResult.succeeded) {
        console.log(`✅ Created: ${pageData.title} (${pageData.path})`);
        return response.data.data.pages.create.page;
      } else {
        console.error(`❌ Failed: ${pageData.title}`,
          response.data.data.pages.create.responseResult.message);
      }
    } catch (error) {
      console.error(`❌ Error creating ${pageData.title}:`,
        error.response?.data || error.message);
    }
  }

  /**
   * Import all pages from content directory
   */
  async importFromDirectory(directory, options = {}) {
    const pages = this.scanDirectory(directory, options);

    console.log(`📚 Found ${pages.length} pages to import`);
    console.log('🚀 Starting import...\n');

    for (const page of pages) {
      await this.createPage(page);
      // Delay to avoid rate limiting
      await this.delay(500);
    }

    console.log('\n🎉 Import completed!');
  }

  /**
   * Recursively scan directory for markdown files
   */
  scanDirectory(dir, basePath = '', options = {}) {
    const items = fs.readdirSync(dir);
    const pages = [];

    for (const item of items) {
      const fullPath = path.join(dir, item);
      const stat = fs.statSync(fullPath);

      if (stat.isDirectory()) {
        // Recursively scan subdirectories
        const subPages = this.scanDirectory(fullPath, path.join(basePath, item), options);
        pages.push(...subPages);
      } else if (item.endsWith('.md')) {
        const content = fs.readFileSync(fullPath, 'utf8');
        const parsed = matter(content);
        const filename = path.parse(item).name;

        // Extract metadata from file
        pages.push({
          title: this.extractTitle(parsed, filename),
          content: this.cleanContent(parsed),
          path: this.generatePath(basePath, filename),
          description: this.extractDescription(parsed),
          tags: this.extractTags(basePath, parsed, options)
        });
      }
    }

    return pages.sort((a, b) => a.path.localeCompare(b.path));
  }

  /**
   * Extract title from markdown content or filename
   */
  extractTitle(parsed, filename) {
    if (parsed.data && parsed.data.title) {
      return String(parsed.data.title).trim();
    }

    // Try to extract from first H1 heading
    const h1Match = parsed.content.match(/^#\s+(.+)$/m);
    if (h1Match) {
      return h1Match[1].trim();
    }

    // Fallback: Convert filename to title case
    return filename
      .replace(/^\d+-/, '') // Remove number prefix
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  /**
   * Clean content and remove title if present
   */
  cleanContent(parsed) {
    // Remove first H1 heading if present (title is separate field)
    return parsed.content.replace(/^#\s+.+$/m, '').trim();
  }

  /**
   * Generate Wiki.js path from directory structure
   */
  generatePath(basePath, filename) {
    const cleanFilename = filename.replace(/^\d+-/, '').toLowerCase();
    const cleanBasePath = basePath
      .split(path.sep)
      .map(part => part.replace(/^\d+-/, '').toLowerCase())
      .join('/');

    if (cleanFilename === 'index' && cleanBasePath) {
      return `/${cleanBasePath}`;
    }

    return cleanBasePath ? `/${cleanBasePath}/${cleanFilename}` : `/${cleanFilename}`;
  }

  /**
   * Extract description from first paragraph
   */
  extractDescription(parsed) {
    if (parsed.data && parsed.data.description) {
      return String(parsed.data.description).trim();
    }

    // Find first paragraph after title
    const paragraphMatch = parsed.content
      .replace(/^#\s+.+$/m, '') // Remove title
      .match(/^[A-Z].+?(?=\n\n|\n#|$)/s);

    if (paragraphMatch) {
      const desc = paragraphMatch[0].trim();
      return desc.length > 200 ? desc.substring(0, 197) + '...' : desc;
    }

    return '';
  }

  /**
   * Extract tags from directory path and content
   */
  extractTags(basePath, parsed, options) {
    const tags = new Set(options.defaultTags || ['github-fundamentals']);

    if (parsed.data && parsed.data.tags) {
      const frontmatterTags = Array.isArray(parsed.data.tags)
        ? parsed.data.tags
        : String(parsed.data.tags).split(',');

      frontmatterTags
        .map(tag => String(tag).trim())
        .filter(Boolean)
        .forEach(tag => tags.add(tag));
    }

    // Add tags from directory name
    const dirName = path.basename(basePath);
    if (dirName) {
      tags.add(dirName.replace(/^\d+-/, '').toLowerCase());
    }

    // Look for common keywords in content
    const keywords = ['git', 'github', 'docker', 'ci/cd', 'security', 'workflow'];
    keywords.forEach(keyword => {
      if (parsed.content.toLowerCase().includes(keyword)) {
        tags.add(keyword.replace(/\//g, '-'));
      }
    });

    return Array.from(tags);
  }

  /**
   * Delay execution
   */
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Main execution
async function main() {
  try {
    const config = {
      apiUrl: process.env.WIKIJS_URL,
      authToken: process.env.WIKIJS_TOKEN
    };

    const importer = new WikiJSImporter(config);
    const contentDirs = (process.env.CONTENT_DIRS || 'content')
      .split(',')
      .map(dir => dir.trim())
      .filter(Boolean)
      .map(dir => (path.isAbsolute(dir) ? dir : path.resolve(__dirname, '..', dir)));
    const defaultTags = (process.env.DEFAULT_TAGS || 'github-fundamentals')
      .split(',')
      .map(tag => tag.trim())
      .filter(Boolean);

    for (const contentDir of contentDirs) {
      if (!fs.existsSync(contentDir)) {
        console.warn(`⚠️ Skipping missing content directory: ${contentDir}`);
        continue;
      }

      await importer.importFromDirectory(contentDir, { defaultTags });
    }
  } catch (error) {
    console.error('Fatal error:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { WikiJSImporter };
