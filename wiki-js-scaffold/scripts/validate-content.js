#!/usr/bin/env node
/**
 * Wiki.js Content Validator
 *
 * Validates markdown content files for common issues:
 * - Syntax errors
 * - Broken internal links
 * - Missing metadata
 * - Malformed frontmatter
 * - Image references
 *
 * Usage:
 *   node validate-content.js [path/to/content]
 */

const fs = require('fs-extra');
const path = require('path');
const matter = require('gray-matter');
const { marked } = require('marked');

class ContentValidator {
  constructor(contentDir) {
    this.contentDir = contentDir || path.join(__dirname, '../content');
    this.errors = [];
    this.warnings = [];
    this.files = [];
    this.allPaths = new Set();
  }

  /**
   * Run all validations
   */
  async validate() {
    console.log('🔍 Starting content validation...\n');
    console.log(`   Content directory: ${this.contentDir}\n`);

    if (!await fs.pathExists(this.contentDir)) {
      console.error(`❌ Content directory not found: ${this.contentDir}`);
      process.exit(1);
    }

    // Scan all files first
    await this.scanDirectory(this.contentDir);
    console.log(`📚 Found ${this.files.length} markdown files\n`);

    // Validate each file
    for (const file of this.files) {
      await this.validateFile(file);
    }

    // Print results
    this.printResults();

    // Exit with error code if there are errors
    if (this.errors.length > 0) {
      process.exit(1);
    }
  }

  /**
   * Recursively scan directory for markdown files
   */
  async scanDirectory(dir) {
    const items = await fs.readdir(dir);

    for (const item of items) {
      const fullPath = path.join(dir, item);
      const stats = await fs.stat(fullPath);

      if (stats.isDirectory()) {
        await this.scanDirectory(fullPath);
      } else if (item.endsWith('.md')) {
        this.files.push(fullPath);
        // Store relative path for link validation
        const relativePath = path.relative(this.contentDir, fullPath);
        this.allPaths.add(relativePath);
        this.allPaths.add(relativePath.replace(/\.md$/, ''));
      }
    }
  }

  /**
   * Validate individual file
   */
  async validateFile(filePath) {
    const relativePath = path.relative(this.contentDir, filePath);
    console.log(`📄 Validating: ${relativePath}`);

    try {
      const content = await fs.readFile(filePath, 'utf8');

      // Check if file is empty
      if (!content.trim()) {
        this.addError(relativePath, 'File is empty');
        return;
      }

      // Validate frontmatter
      this.validateFrontmatter(relativePath, content);

      // Validate markdown syntax
      this.validateMarkdown(relativePath, content);

      // Validate internal links
      this.validateLinks(relativePath, content);

      // Validate images
      this.validateImages(relativePath, content);

      console.log(`  ✅ Valid\n`);
    } catch (error) {
      this.addError(relativePath, `Failed to read file: ${error.message}`);
    }
  }

  /**
   * Validate frontmatter
   */
  validateFrontmatter(filePath, content) {
    try {
      const parsed = matter(content);

      // Check for common frontmatter fields
      if (parsed.data && Object.keys(parsed.data).length > 0) {
        // Validate title
        if (!parsed.data.title || typeof parsed.data.title !== 'string') {
          this.addWarning(filePath, 'Missing or invalid title in frontmatter');
        }

        // Validate description
        if (parsed.data.description && parsed.data.description.length > 200) {
          this.addWarning(filePath, 'Description exceeds 200 characters');
        }
      }
    } catch (error) {
      this.addError(filePath, `Invalid frontmatter: ${error.message}`);
    }
  }

  /**
   * Validate markdown syntax
   */
  validateMarkdown(filePath, content) {
    try {
      // Remove frontmatter for parsing
      const parsed = matter(content);
      const markdown = parsed.content;

      // Parse markdown
      marked.parse(markdown);

      // Check for common issues
      if (!markdown.match(/^#\s+/m)) {
        this.addWarning(filePath, 'No H1 heading found');
      }

      // Check for multiple H1 headings
      const h1Count = (markdown.match(/^#\s+/gm) || []).length;
      if (h1Count > 1) {
        this.addWarning(filePath, `Multiple H1 headings found (${h1Count})`);
      }

      // Check for very long lines (over 120 chars)
      const lines = markdown.split('\n');
      lines.forEach((line, index) => {
        if (line.length > 200 && !line.startsWith('http') && !line.startsWith('![')) {
          this.addWarning(filePath, `Line ${index + 1} is very long (${line.length} chars)`);
        }
      });
    } catch (error) {
      this.addError(filePath, `Markdown syntax error: ${error.message}`);
    }
  }

  /**
   * Validate internal links
   */
  validateLinks(filePath, content) {
    // Extract markdown links
    const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    let match;

    while ((match = linkRegex.exec(content)) !== null) {
      const linkText = match[1];
      const linkUrl = match[2];

      // Check internal links (not starting with http/https)
      if (!linkUrl.startsWith('http://') && !linkUrl.startsWith('https://') && !linkUrl.startsWith('#')) {
        // Remove ./ and ../ prefixes for comparison
        const cleanUrl = linkUrl.replace(/^\.\//, '').replace(/^\.\.\//, '');

        // Check if linked file exists
        if (!this.allPaths.has(cleanUrl) && !this.allPaths.has(cleanUrl.replace(/\.md$/, ''))) {
          this.addWarning(filePath, `Potentially broken link: ${linkUrl}`);
        }
      }

      // Check for empty link text
      if (!linkText.trim()) {
        this.addWarning(filePath, `Empty link text for: ${linkUrl}`);
      }
    }
  }

  /**
   * Validate image references
   */
  validateImages(filePath, content) {
    // Extract image references
    const imageRegex = /!\[([^\]]*)\]\(([^)]+)\)/g;
    let match;

    while ((match = imageRegex.exec(content)) !== null) {
      const altText = match[1];
      const imageUrl = match[2];

      // Check for missing alt text
      if (!altText.trim()) {
        this.addWarning(filePath, `Missing alt text for image: ${imageUrl}`);
      }

      // Check local image references
      if (!imageUrl.startsWith('http://') && !imageUrl.startsWith('https://')) {
        const imagePath = path.join(path.dirname(filePath), imageUrl);
        if (!fs.existsSync(imagePath)) {
          this.addWarning(filePath, `Image file not found: ${imageUrl}`);
        }
      }
    }
  }

  /**
   * Add error
   */
  addError(filePath, message) {
    this.errors.push({ file: filePath, message });
    console.log(`  ❌ ERROR: ${message}`);
  }

  /**
   * Add warning
   */
  addWarning(filePath, message) {
    this.warnings.push({ file: filePath, message });
    console.log(`  ⚠️  WARNING: ${message}`);
  }

  /**
   * Print validation results
   */
  printResults() {
    console.log('\n' + '='.repeat(60));
    console.log('📊 Validation Results');
    console.log('='.repeat(60));
    console.log(`   Files validated: ${this.files.length}`);
    console.log(`   ❌ Errors: ${this.errors.length}`);
    console.log(`   ⚠️  Warnings: ${this.warnings.length}`);

    if (this.errors.length === 0 && this.warnings.length === 0) {
      console.log('\n🎉 All content is valid!');
    } else {
      if (this.errors.length > 0) {
        console.log('\n❌ Errors:');
        this.errors.forEach(error => {
          console.log(`   ${error.file}: ${error.message}`);
        });
      }

      if (this.warnings.length > 0) {
        console.log('\n⚠️  Warnings:');
        this.warnings.forEach(warning => {
          console.log(`   ${warning.file}: ${warning.message}`);
        });
      }
    }
    console.log('='.repeat(60) + '\n');
  }
}

// Main execution
async function main() {
  const contentDir = process.argv[2];
  const validator = new ContentValidator(contentDir);
  await validator.validate();
}

if (require.main === module) {
  main();
}

module.exports = { ContentValidator };
