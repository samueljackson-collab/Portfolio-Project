# Portfolio Automation Scripts

# ============================

This directory contains automation scripts for managing and maintaining the portfolio project.

## Available Scripts

### 1. organize-screenshots.py

**Purpose:** Intelligent screenshot organization and cataloging for portfolio projects

**Features:**

- Automatically categorizes screenshots by content (dashboards, infrastructure, networking, etc.)
- Renames files with consistent naming convention
- Generates markdown catalogs with image previews
- Creates JSON indexes for programmatic access
- Detects and skips duplicate files
- Extracts image metadata (dimensions, file size, timestamp)

**Usage:**

```bash
# Organize screenshots with auto-detection
python3 organize-screenshots.py /path/to/screenshots

# Organize for specific project
python3 organize-screenshots.py /path/to/screenshots --project PRJ-HOME-001

# Preview without moving files
python3 organize-screenshots.py /path/to/screenshots --dry-run
```

**Categories:**

- `dashboards`: Grafana, metrics, charts
- `infrastructure`: Proxmox, VMs, clusters
- `networking`: UniFi, switches, topology
- `monitoring`: Prometheus, alerts, logs
- `services`: Applications, web interfaces
- `storage`: TrueNAS, NAS, ZFS
- `security`: SIEM, security tools
- `configuration`: Settings, configs
- `deployment`: Terraform, Ansible
- `misc`: Uncategorized

**Output Structure:**

```
projects/PROJECT/assets/screenshots/
├── category1/
│   ├── PRJ-XXX_category_01_20241106.png
│   └── PRJ-XXX_category_02_20241106.png
├── category2/
│   └── PRJ-XXX_category_01_20241106.png
├── README.md                    # Generated catalog
└── screenshots-index.json       # JSON index
```

---

### 2. create-diagram-viewers.py

**Purpose:** Create GitHub-viewable markdown wrappers for Mermaid diagrams

**Features:**

- Wraps Mermaid (.mmd, .mermaid) diagrams in markdown code blocks
- GitHub automatically renders these on the web interface
- No external tools required (no PNG conversion needed)
- Includes instructions for exporting to other formats

**Usage:**

```bash
# Convert all Mermaid diagrams in repository
python3 create-diagram-viewers.py

# The script searches the entire repository automatically
```

**Output:**
For each `diagram.mermaid` file, creates `diagram.md` with:

- Mermaid code in GitHub-compatible fenced code block
- Diagram title and description
- Instructions for viewing and exporting
- Reference to original source file

---

### 3. convert-mermaid-to-png.py

**Purpose:** Convert Mermaid diagrams to PNG using mermaid.ink API

**Features:**

- Uses free mermaid.ink API (no auth required)
- Compresses and base64-encodes diagrams
- Downloads PNG renders
- Configurable theme and scale

**Usage:**

```bash
# Convert all Mermaid diagrams
python3 convert-mermaid-to-png.py

# Convert diagrams in specific directory
python3 convert-mermaid-to-png.py /path/to/diagrams
```

**Note:** This script requires internet access to mermaid.ink API. If API is blocked, use `create-diagram-viewers.py` instead for GitHub-native rendering.

---

## Script Dependencies

### Python Version

All scripts require **Python 3.6+**

### Optional Dependencies

For `organize-screenshots.py`:

```bash
# Install Pillow for advanced image metadata extraction
pip install Pillow
```

For `convert-mermaid-to-png.py`:

```bash
# Requires internet access to mermaid.ink API
# No additional packages needed (uses stdlib)
```

---

## Usage Examples

### Scenario 1: Add New Screenshots

```bash
# Take screenshots and save to ~/screenshots/
# Then organize them:
python3 scripts/organize-screenshots.py ~/screenshots --project PRJ-HOME-001

# Review the generated catalog:
cat projects/06-homelab/PRJ-HOME-001/assets/screenshots/README.md
```

### Scenario 2: Update Diagrams

```bash
# Edit a Mermaid diagram
vim projects/06-homelab/PRJ-HOME-002/assets/diagrams/service-architecture.mermaid

# Regenerate markdown viewer
python3 scripts/create-diagram-viewers.py

# Commit changes
git add .
git commit -m "Update service architecture diagram"
```

### Scenario 3: Bulk Organization

```bash
# Organize all screenshots from multiple sources
for dir in ~/screenshots/grafana ~/screenshots/proxmox ~/screenshots/unifi; do
  python3 scripts/organize-screenshots.py "$dir" --dry-run
done

# Review the preview, then run without --dry-run
```

---

## Best Practices

### For Screenshots

1. **Name Descriptively:** Include service/tool name in filename before organizing
2. **One Topic Per Screenshot:** Makes categorization more accurate
3. **High Resolution:** Minimum 1920x1080 for dashboards
4. **Redact Sensitive Data:** Remove IPs, hostnames, credentials before organizing
5. **Consistent Source:** Take screenshots in same browser/resolution for consistency

### For Diagrams

1. **Valid Syntax:** Test diagrams at <https://mermaid.live> before committing
2. **Clear Labels:** Use descriptive node names and edge labels
3. **Logical Flow:** Top-to-bottom or left-to-right flow
4. **Consistent Style:** Use same diagram type for similar architectures
5. **Version Control:** Keep `.mermaid` source files in git, regenerate .md as needed

### For Automation

1. **Test First:** Always use `--dry-run` before actual organization
2. **Backup Originals:** Keep original files until organization is verified
3. **Review Catalogs:** Check generated README files for accuracy
4. **Incremental Updates:** Run scripts after each batch of new files
5. **Commit Often:** Git commit after each successful organization

---

## Troubleshooting

### organize-screenshots.py Issues

**Problem:** Script can't determine project

```
Solution: Use --project flag explicitly
  python3 organize-screenshots.py /path --project PRJ-HOME-001
```

**Problem:** Duplicate detection too aggressive

```
Solution: Duplicates are based on file hash (content). Rename files
          with different content if needed
```

**Problem:** Wrong category assigned

```
Solution: Rename file to include category keyword before organizing
  Example: rename "screen1.png" to "grafana-dashboard.png"
```

### create-diagram-viewers.py Issues

**Problem:** Diagram doesn't render on GitHub

```
Solution: Check Mermaid syntax at https://mermaid.live
          Ensure proper fenced code block format
```

**Problem:** File encoding errors

```
Solution: Ensure .mermaid files are UTF-8 encoded
```

### convert-mermaid-to-png.py Issues

**Problem:** HTTP 403 errors from mermaid.ink

```
Solution: API may be rate-limited or blocked
          Use create-diagram-viewers.py instead
          Or export manually from https://mermaid.live
```

---

## Contributing

### Adding New Scripts

1. Follow existing naming convention: `action-object.py`
2. Include comprehensive docstring and help text
3. Add usage examples and error handling
4. Update this README with documentation
5. Make executable: `chmod +x script.py`

### Script Template

```python
#!/usr/bin/env python3
"""
Script Name - Description
==========================
Detailed description of what the script does.

Usage:
    python3 script.py [options]

Author: Portfolio Project Automation
"""

import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='...')
    # Add arguments
    args = parser.parse_args()
    # Implementation
    return 0

if __name__ == '__main__':
    sys.exit(main())
```

---

## Future Enhancements

Planned script additions:

- [ ] `generate-resume-variants.py` - Auto-generate resume PDFs from templates
- [ ] `validate-configs.py` - Lint and validate configuration files
- [ ] `export-portfolio.py` - Package portfolio for offline viewing
- [ ] `check-links.py` - Verify all markdown links are valid
- [ ] `generate-metrics.py` - Portfolio statistics and completion tracking

---

## Support

For issues or questions:

1. Check this README first
2. Review script help: `python3 script.py --help`
3. Check script source code (well-documented)
4. Open issue in portfolio repository

---

**Last Updated:** 2024-11-06
**Maintained By:** Portfolio Automation Team
