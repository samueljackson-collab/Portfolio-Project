# Reportify Pro - Example Projects

This directory contains example project files demonstrating how to use Reportify Pro templates.

## Available Examples

### 1. Vulnerability Assessment (`vulnerability_assessment_example.json`)

**Domain:** Security
**Template:** `vulnerability_assessment`
**Description:** Comprehensive Q4 2024 security assessment with CVSS-rated findings

**Demonstrates:**
- Executive summary for stakeholder communication
- Multiple severity findings (Critical, High, Medium)
- Risk assessment with impact/likelihood matrix
- Timeline tracking from discovery to remediation
- Technical stack documentation
- Smart variables for consistency

**Generate Report:**
```bash
python src/reportify_pro.py generate \
  -i templates/examples/vulnerability_assessment_example.json \
  -o vulnerability_assessment_report.docx
```

### 2. Cloud Migration Assessment (`cloud_migration_example.json`)

**Domain:** Cloud Infrastructure
**Template:** `cloud_migration`
**Description:** Enterprise ERP migration to AWS with TCO analysis

**Demonstrates:**
- Multi-phase migration strategy (18-month timeline)
- Total Cost of Ownership (TCO) analysis
- Risk mitigation planning
- KPI tracking (RTO/RPO improvements)
- Architecture design documentation
- Complex timeline with dependencies

**Generate Report:**
```bash
python src/reportify_pro.py generate \
  -i templates/examples/cloud_migration_example.json \
  -o cloud_migration_assessment.docx
```

## Using Examples as Templates

### Method 1: CLI

```bash
# Copy an example and customize
cp templates/examples/vulnerability_assessment_example.json my_project.json

# Edit the JSON file
nano my_project.json  # or use your preferred editor

# Generate report
python src/reportify_pro.py generate -i my_project.json -o my_report.docx
```

### Method 2: GUI

```bash
# Launch the GUI
python src/reportify_gui.py

# File → Open → Select example JSON
# Modify fields in the form
# File → Save As → Save with new name
# Export → Generate DOCX
```

## Customizing Examples

All examples are JSON files that can be edited with any text editor. Key sections to customize:

```json
{
  "title": "Your Report Title Here",
  "company_name": "Your Company Name",
  "author": "Your Name",
  "executive_summary": "High-level summary for executives...",
  "findings": [
    "Finding 1",
    "Finding 2"
  ],
  "recommendations": [
    "Recommendation 1",
    "Recommendation 2"
  ],
  "tags": ["tag1", "tag2"]
}
```

### Smart Variables

Both examples use smart variables for consistency:

```json
{
  "smart_variables": {
    "project_name": "My Project",
    "system": "Production System"
  },
  "title": "{{project_name}} - Assessment Report",
  "scope": "This assessment covers {{system}}..."
}
```

Variables are automatically replaced during document generation.

## Creating Your Own Examples

1. Start from a template:
   ```bash
   python src/reportify_pro.py new -t <template_key> -o my_example.json
   ```

2. Fill in all sections comprehensively

3. Add realistic data (metrics, findings, recommendations)

4. Test generation:
   ```bash
   python src/reportify_pro.py generate -i my_example.json -o test_output.docx
   ```

5. Save in `templates/examples/` with descriptive filename

## Tips for Realistic Examples

- **Executive Summaries**: 2-3 paragraphs, focus on business impact
- **Findings**: Be specific with versions, CVEs, or metrics
- **Recommendations**: Prioritize by urgency (Immediate, High, Medium, Low)
- **Risks**: Include all 4 attributes (impact, likelihood, mitigation, owner)
- **Timeline**: Use realistic dates and status values
- **Tags**: Add 5-10 relevant tags for searchability

## Output Examples

Generated reports will include:

- Professional cover page with company branding
- Table of contents (placeholder for manual generation in Word)
- All content sections from the JSON
- Risk assessment matrix
- Project timeline table
- Appendices with technical details
- Consistent professional formatting

## Questions?

See the main [README.md](../../README.md) for full documentation.
