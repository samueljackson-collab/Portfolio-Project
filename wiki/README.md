# Portfolio Wiki - Wiki.js Content

This directory contains comprehensive documentation for all portfolio projects in Wiki.js markdown format.

## 📚 What's Included

This wiki provides complete documentation for:

- **Project Documentation**: Implementation guides for all portfolio projects
- **Runbooks**: Incident response procedures (30+ runbooks)
- **Playbooks**: Process workflows for complex scenarios (15+ playbooks)
- **Handbooks**: Reference guides and standards (Engineer's Handbook, Operations, Security, etc.)

## 🚀 Quick Start

### Option 1: Import into Wiki.js

If you have Wiki.js running (like in PRJ-HOME-002):

1. **Copy wiki content to Wiki.js storage**:
   ```bash
   # If Wiki.js uses local storage
   cp -r wiki/* /var/wiki/data/

   # If Wiki.js uses git sync
   cd /path/to/wiki-repo
   cp -r /path/to/Portfolio-Project/wiki/* .
   git add .
   git commit -m "Add portfolio documentation"
   git push
   ```

2. **Access Wiki.js** and navigate to Admin → Storage
   - Click "Synchronize" to import the new content

3. **Navigate to** `http://your-wiki-url/home` to see the main page

### Option 2: Browse Markdown Files Directly

The wiki is organized in markdown files that can be read directly:

```bash
cd wiki/
cat home.md                  # Main landing page
cat getting-started.md       # How to use the wiki

# Browse by category
ls projects/                 # Project documentation
ls runbooks/                 # Incident response procedures
ls playbooks/                # Process workflows
ls handbooks/                # Reference guides
```

### Option 3: Use a Markdown Viewer

Use any markdown viewer or static site generator:

- **VS Code**: Install "Markdown Preview Enhanced" extension
- **MkDocs**: `mkdocs serve` (requires mkdocs.yml configuration)
- **Docsify**: Host with docsify for a web interface
- **GitHub**: Push to GitHub and browse in the web UI

## 📁 Directory Structure

```
wiki/
├── home.md                          # Main landing page
├── getting-started.md               # Wiki usage guide
├── README.md                        # This file
│
├── projects/                        # Project documentation
│   ├── homelab/
│   │   ├── prj-home-001/           # Network infrastructure
│   │   └── prj-home-002/           # Virtualization & services
│   ├── sde-devops/
│   │   ├── prj-sde-001/            # Database infrastructure (Terraform/AWS)
│   │   └── prj-sde-002/            # Observability & backups
│   ├── cybersecurity/
│   │   └── prj-cyb-blue-001/        # SIEM pipeline
│   └── ...
│
├── runbooks/                        # Incident response procedures
│   ├── index.md                     # Runbook index
│   ├── infrastructure/
│   │   ├── host-down.md            # When servers become unreachable
│   │   ├── disk-space-low.md       # Disk usage >80%
│   │   └── ...
│   ├── database/
│   │   ├── backup-failure.md       # Backup job failures
│   │   └── ...
│   ├── networking/
│   ├── security/
│   └── monitoring/
│
├── playbooks/                       # Process workflows
│   ├── index.md                     # Playbook index
│   ├── disaster-recovery.md         # Complete DR procedures
│   ├── backup-recovery.md           # Backup management
│   ├── incident-response.md         # Security incident handling
│   ├── deployment.md                # Deployment workflow
│   └── ...
│
└── handbooks/                       # Reference guides
    ├── engineers-handbook.md        # Standards, quality gates, best practices
    ├── operations-handbook.md       # Day-to-day operations
    ├── security-handbook.md         # Security standards
    ├── monitoring-handbook.md       # Observability best practices
    └── ...
```

## 🎯 Key Documents

Start with these essential documents:

1. **[home.md](./home.md)** - Main landing page with full navigation
2. **[getting-started.md](./getting-started.md)** - How to use this wiki
3. **[runbooks/index.md](./runbooks/index.md)** - All incident response procedures
4. **[playbooks/index.md](./playbooks/index.md)** - All process workflows
5. **[handbooks/engineers-handbook.md](./handbooks/engineers-handbook.md)** - Comprehensive standards guide

## 🔗 Wiki.js Integration

### Wiki.js Metadata

Each markdown file includes Wiki.js frontmatter:

```yaml
---
title: Page Title
description: Page description
published: true
date: 2025-11-07
tags: [tag1, tag2, tag3]
---
```

### Navigation Structure

Wiki.js will automatically:
- Build navigation from directory structure
- Create search index from all pages
- Enable tag-based filtering
- Support full-text search

### Internal Links

Internal links use absolute paths:

```markdown
[Link text](/path/to/page)

Example:
[Host Down Runbook](/runbooks/infrastructure/host-down)
[Disaster Recovery Playbook](/playbooks/disaster-recovery)
```

## 📊 Content Statistics

- **Total Pages**: 100+ documents
- **Runbooks**: 30+ incident response procedures
- **Playbooks**: 15+ process workflows
- **Handbooks**: 5+ comprehensive reference guides
- **Project Docs**: Complete documentation for 5+ major projects

## 🛠️ Customization

### Adding New Content

**New Runbook**:
```bash
# Copy template
cp runbooks/infrastructure/host-down.md runbooks/infrastructure/new-runbook.md

# Edit the new file
# Add link to runbooks/index.md
```

**New Playbook**:
```bash
# Copy template
cp playbooks/disaster-recovery.md playbooks/new-playbook.md

# Edit the new file
# Add link to playbooks/index.md
```

**New Project**:
```bash
# Create directory
mkdir -p projects/category/prj-xxx-###/

# Create documentation files
touch projects/category/prj-xxx-###/overview.md
touch projects/category/prj-xxx-###/implementation.md
touch projects/category/prj-xxx-###/operations.md

# Link from home.md
```

### Updating Existing Content

1. Edit the markdown file
2. Update the `date` field in frontmatter
3. If using git sync with Wiki.js:
   ```bash
   git add .
   git commit -m "Update documentation"
   git push
   ```
4. In Wiki.js: Admin → Storage → Synchronize

## 🔍 Searching Content

**In Wiki.js**:
- Use search bar (top right)
- Filter by tags
- Use advanced search syntax

**Command Line**:
```bash
# Search all files
grep -r "search term" wiki/

# Search runbooks only
grep -r "alert name" wiki/runbooks/

# Search by tag
grep -r "tag: monitoring" wiki/
```

## 📝 Documentation Standards

All documentation follows these standards:

- **Markdown**: GitHub-flavored markdown
- **Structure**: Consistent heading hierarchy
- **Code Blocks**: Language-specific syntax highlighting
- **Links**: Absolute paths for portability
- **Images**: Stored in project `assets/` directories
- **Metadata**: Complete Wiki.js frontmatter

See [Engineer's Handbook](./handbooks/engineers-handbook.md#documentation-standards) for complete standards.

## 🤝 Contributing

To contribute to this wiki:

1. **Find gaps**: Missing runbooks, outdated procedures
2. **Create/update content**: Follow templates and standards
3. **Test locally**: Verify markdown renders correctly
4. **Submit changes**: Create PR or update directly (if access)
5. **Update indexes**: Add links to relevant index pages

## 🆘 Support

**Questions?**
- Check [Getting Started Guide](./getting-started.md)
- Review [Engineer's Handbook](./handbooks/engineers-handbook.md)
- Contact: [Sam Jackson](https://github.com/samueljackson-collab)

**Issues?**
- Broken links: Search for the page name
- Missing content: Check project README files
- Wiki.js issues: Check [Wiki.js docs](https://docs.requarks.io/)

## 📚 Related Documentation

- **Main Portfolio README**: `../README.md`
- **Project Directories**: `../projects/`
- **Infrastructure Code**: `../infrastructure/`
- **GitHub Repo**: [samueljackson-collab/Portfolio-Project](https://github.com/samueljackson-collab/Portfolio-Project)

---

**Author**: Sam Jackson
**GitHub**: [@samueljackson-collab](https://github.com/samueljackson-collab)
**LinkedIn**: [sams-jackson](https://www.linkedin.com/in/sams-jackson)
**Last Updated**: November 7, 2025
**Version**: 1.0
