# Mermaid Diagram Support - Implementation Guide

## Overview

This document explains how Mermaid diagrams are rendered across different parts of the portfolio.

## Problem Statement

The main README.md contains 50+ Mermaid diagrams (flowcharts and pie charts) that need to render correctly when the portfolio is viewed:
1. On GitHub.com (native support)
2. On GitHub Pages (via VitePress)
3. Via direct index.html (standalone viewer)

## Solution Implemented

### 1. VitePress Integration (Primary Homepage)

**Location**: `projects/25-portfolio-website`

**Implementation**:
- Added `mermaid` and `vitepress-plugin-mermaid` to `package.json`
- Configured `config.ts` to use `withMermaid()` wrapper
- Created `/main/complete-overview.md` with sample diagrams
- Added custom Mermaid theme matching portfolio colors

**How It Works**:
- Mermaid diagrams are rendered client-side using Vue components
- The `<Mermaid>` component receives URL-encoded diagram code
- Diagrams render when JavaScript executes in the browser
- Static HTML contains placeholder `<div class="mermaid">` elements

**Testing**:
```bash
cd projects/25-portfolio-website
npm install
npm run docs:build  # Build static site
npm run docs:dev    # Test locally at http://localhost:5173
```

### 2. Standalone Index.html (Alternative Viewer)

**Location**: `/index.html` (repository root)

**Implementation**:
- Fetches README.md dynamically
- Uses marked.js to convert Markdown to HTML
- Uses mermaid.js CDN to render diagrams
- Provides fallback for viewing README with diagrams

**How It Works**:
1. Loads README.md via fetch API
2. Converts Markdown to HTML using marked.js
3. Replaces code blocks with `<div class="mermaid">` elements
4. Mermaid.js automatically renders diagrams on page load

**Testing**:
```bash
# From repository root
python3 -m http.server 8080
# Visit http://localhost:8080/index.html
```

## Deployment

### GitHub Pages (Automatic)

The `.github/workflows/deploy-docs.yml` workflow automatically:
1. Builds the VitePress site with Mermaid support
2. Deploys to GitHub Pages
3. Makes diagrams available at the live URL

### Verify Deployment

After deployment, visit:
- Main site: `https://samueljackson-collab.github.io/Portfolio-Project/`
- Diagrams page: `https://samueljackson-collab.github.io/Portfolio-Project/main/complete-overview`

## Configuration Files Modified

### `projects/25-portfolio-website/package.json`
```json
{
  "devDependencies": {
    "vitepress": "^1.0.0",
    "mermaid": "^10.6.1",
    "vitepress-plugin-mermaid": "^2.0.13"
  }
}
```

### `projects/25-portfolio-website/docs/.vitepress/config.ts`
```typescript
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(
  defineConfig({
    // ... config
    mermaid: {
      theme: 'default',
      themeVariables: {
        primaryColor: '#2563eb',
        // ... custom colors
      }
    }
  })
)
```

## Troubleshooting

### Diagrams Not Rendering

1. **Check browser console** for JavaScript errors
2. **Verify CDN access** - Mermaid.js CDN must be accessible
3. **Check build logs** for VitePress build errors
4. **Clear browser cache** after deployment

### Build Failures

1. Check for **dead links** in markdown files
2. Verify **Mermaid syntax** is correct
3. Run `npm install` to ensure dependencies are installed

## Adding New Diagrams

### In VitePress Pages

```markdown
# Your Page

## Diagram Example

\`\`\`mermaid
flowchart LR
  A[Start] --> B[Process]
  B --> C[End]
\`\`\`

\`\`\`mermaid
pie title Distribution
  "Part A" : 40
  "Part B" : 30
  "Part C" : 30
\`\`\`
```

### Supported Diagram Types

- Flowcharts (`flowchart` or `graph`)
- Pie charts (`pie`)
- Sequence diagrams (`sequenceDiagram`)
- Class diagrams (`classDiagram`)
- State diagrams (`stateDiagram`)
- Entity relationship diagrams (`erDiagram`)
- And more...

## Performance Notes

- **Client-side rendering**: Diagrams render in browser, not during build
- **Bundle size**: Mermaid adds ~800KB to JavaScript bundle
- **Load time**: Diagrams render progressively as page loads
- **Caching**: Browsers cache Mermaid.js for faster subsequent loads

## References

- [Mermaid Documentation](https://mermaid.js.org/)
- [VitePress Plugin Mermaid](https://github.com/emersonbottero/vitepress-plugin-mermaid)
- [VitePress Documentation](https://vitepress.dev/)

---

**Last Updated**: 2026-01-06
**Status**: ✅ Implemented and tested
