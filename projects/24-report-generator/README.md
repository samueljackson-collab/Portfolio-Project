# Reportify Pro v2.1 - Enterprise Report Generator

**Professional report generation system with 25+ IT templates for Security, DevOps, Cloud, SysAdmin, Project Management, Compliance, and Networking domains.**

![Status](https://img.shields.io/badge/status-active-success)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🎯 Overview

Reportify Pro is a comprehensive enterprise-grade report generation system designed for IT professionals across multiple domains. Generate professional Word documents (.docx) with consistent formatting, smart variables, risk matrices, timeline management, and more.

### Key Features

- **25+ Professional Templates** across 7+ IT job role domains
- **Modern GUI Interface** with three-panel design (Categories | Templates | Form)
- **CLI Support** for automation and batch processing
- **Smart Variables** - Define once, use everywhere (e.g., `{{project_name}}`, `{{system}}`)
- **Risk Assessment** - Built-in risk matrix with impact/likelihood tracking
- **Timeline Management** - Project milestones with status tracking
- **Tag System** - Intelligent tagging with auto-suggestions
- **Multi-Section Support** - Executive summaries, findings, recommendations, appendices
- **Professional Formatting** - Consistent styles, cover pages, tables, metadata
- **Save/Load Projects** - JSON-based project files for reusability
- **Export to DOCX** - Microsoft Word format with professional styling

---

## 📚 Template Categories

### 🔒 Security (6 templates)
- **Vulnerability Assessment** - CVSS-rated security assessment
- **Penetration Testing** - OWASP/PTES methodology reports
- **Incident Response** - Security incident documentation (NIST SP 800-61)
- **IAM Security Audit** - Identity and access management review
- **Attack Surface Analysis** - External exposure assessment
- **Log Analysis** - SIEM correlation and anomaly detection

### 🏗️ DevOps (5 templates)
- **Infrastructure Design** - Architecture specifications
- **Deployment Report** - Production deployment summaries
- **Proof of Concept** - Technical feasibility validation
- **QA Test Report** - Functional and regression testing (IEEE 829)
- **Performance Optimization** - Load testing and tuning

### ☁️ Cloud Infrastructure (4 templates)
- **Cloud Migration** - Migration strategy and planning
- **Cost Optimization** - FinOps analysis and recommendations
- **AWS Infrastructure Audit** - Well-Architected Framework review
- **Multi-Cloud Strategy** - Cross-cloud governance

### 🖥️ System Administration (4 templates)
- **System Audit** - Server configuration and hardening review
- **Technology Assessment** - Stack evaluation and modernization
- **Patch Management** - Compliance and scheduling
- **Capacity Planning** - Resource forecasting

### 📋 Project Management (4 templates)
- **Project Status** - Progress tracking and milestone reporting
- **Project Proposal** - Executive-ready proposals with ROI
- **Project Closure** - Lessons learned and outcomes
- **Operational Report** - Monthly KPI and SRE metrics

### ✅ Compliance (1 template)
- **Compliance Audit** - ISO 27001, SOC 2, GDPR gap analysis

### 🌐 Networking (1 template)
- **Network Security Assessment** - Infrastructure security review

### 📊 Data Analytics (1 template)
- **Analytical Report** - Business intelligence and data insights

---

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python src/generate_report.py --help
```

### Generate Reports Manually

```bash
# Generate a single report
python src/generate_report.py generate \
    --template weekly.html \
    --output ./reports/weekly-report.pdf \
    --format pdf

# Generate all reports
python src/generate_report.py generate-all \
    --output-dir ./reports

# View portfolio statistics
python src/generate_report.py stats
```

## 📊 Components

### 1. Manual Report Generation

**Basic Usage**:
```bash
# HTML report
python src/generate_report.py generate \
    -t project_status.html \
    -o report.html \
    -f html

# PDF report
python src/generate_report.py generate \
    -t executive_summary.html \
    -o summary.pdf \
    -f pdf

# All reports at once
python src/generate_report.py generate-all -o ./reports
```

**Available Templates**:
- `project_status.html` - Detailed project status and completion
- `executive_summary.html` - High-level overview for executives
- `technical_documentation.html` - Architecture and implementation details
- `weekly.html` - Weekly progress report

### 2. Scheduled Report Generation

**Configuration**:
Edit `config/scheduler.yml`:
```yaml
schedules:
  weekly:
    day_of_week: mon
    hour: 9
    minute: 0

  monthly:
    day: 1
    hour: 9
    minute: 0
```

**Start Scheduler**:
```bash
# Run with default config
python src/scheduler.py --config config/scheduler.yml

# Run in test mode (5 min intervals)
python src/scheduler.py --test-mode

# Run a single job and exit
python src/scheduler.py --run-once weekly
```

**Scheduled Jobs**:
- **Weekly Report**: Every Monday at 9 AM
- **Monthly Summary**: 1st of month at 9 AM
- **Daily Stats**: Every day at 8 AM

### 3. Email Delivery

**Configuration**:
Edit `config/scheduler.yml`:
```yaml
email:
  enabled: true
  smtp_server: smtp.gmail.com
  smtp_port: 587
  smtp_user: your-email@gmail.com
  smtp_password: your-app-password
  from_address: your-email@gmail.com
  from_name: Portfolio Report Generator
  use_tls: true

  weekly_recipients:
    - team@example.com
    - manager@example.com

  monthly_recipients:
    - executives@example.com
```

**Test Email Sending**:
```bash
python src/email_sender.py \
    --smtp-server smtp.gmail.com \
    --smtp-port 587 \
    --smtp-user your-email@gmail.com \
    --smtp-password your-app-password \
    --to recipient@example.com \
    --reports report.pdf
```

**Email Features**:
- HTML-formatted emails with embedded styling
- Multiple attachments (HTML + PDF)
- Weekly and monthly templates
- Custom subject lines and messages

### 4. Historical Comparison

**Save Current Snapshot**:
```bash
# Save current portfolio state
python src/compare.py \
    --action save \
    --data-file current_data.json \
    --history-dir ./history
```

**Compare with Previous**:
```bash
# Compare with snapshot from 7 days ago
python src/compare.py \
    --action compare \
    --data-file current_data.json \
    --days-back 7 \
    --history-dir ./history
```

**View Trends**:
```bash
# View trend for a metric over 30 days
python src/compare.py \
    --action trend \
    --metric avg_completion \
    --days-back 30 \
    --history-dir ./history
```

**Comparison Features**:
- Metric deltas and percentage changes
- Trend detection (up/down/stable)
- Technology stack changes
- Project status changes
- Automated insights generation

## 📈 Report Templates

### Executive Summary
- High-level portfolio overview
- Key metrics and KPIs
- Status breakdown by tier
- Technology stack summary
- Quality indicators

### Project Status
- Detailed project listing
- Completion percentages
- Code statistics
- CI/CD and testing status
- Docker and Kubernetes indicators

### Technical Documentation
- Architecture overview
- Implementation details
- Technology choices
- Best practices
- Deployment guides

### Weekly Report
- Recent changes
- Progress updates
- Blockers and risks
- Next week's focus

## Run

### One-Time Report
```bash
# Clone the repository
git clone https://github.com/your-org/Portfolio-Project.git
cd Portfolio-Project/projects/24-report-generator

# Install dependencies
pip install -r requirements.txt
```

### GUI Mode (Recommended)

```bash
# Launch the graphical interface
python src/reportify_gui.py
```

**GUI Workflow:**
1. Select a category from the left sidebar (Security, DevOps, Cloud, etc.)
2. Browse templates in the middle panel
3. Click "Use Template" to load pre-configured defaults
4. Fill in the form on the right (organized in tabs: Basic Info, Content, Analysis, Metadata)
5. Click "💾 Save" to save your project as JSON
6. Click "📄 Export" to generate the final Word document

### CLI Mode (Automation)

```bash
# List all available templates
python src/reportify_pro.py list-templates

# Create new project from template
python src/reportify_pro.py new \
  -t vulnerability_assessment \
  -o my_security_audit.json

# Edit the JSON file manually or load in GUI

# Generate report from project file
python src/reportify_pro.py generate \
  -i my_security_audit.json \
  -o security_audit_report.docx
```

---

## 📖 Usage Guide

### Creating Your First Report

**Option 1: Using the GUI**

1. Launch the GUI: `python src/reportify_gui.py`
2. Click **Security** in the left sidebar
3. Select **Vulnerability Assessment Report**
4. Click **Use Template** - the form auto-populates with defaults
5. Update the fields:
   - **Title**: "Q4 2024 Production Environment Vulnerability Assessment"
   - **Company**: "Acme Corporation"
   - **Author**: Your name
   - **Executive Summary**: High-level overview for stakeholders
6. Add objectives, findings, and recommendations using the list managers
7. Switch to the **Metadata** tab to add tags: `security`, `vulnerability`, `Q4-2024`
8. Click **💾 Save** and choose a location (e.g., `acme_vuln_q4.json`)
9. Click **📄 Export** to generate `acme_vuln_q4.docx`

**Option 2: Using the CLI**

```bash
# Create a new project
python src/reportify_pro.py new \
  -t penetration_test \
  -o pentest_project.json

# Edit the JSON file
nano pentest_project.json  # or use any text editor

# Generate the report
python src/reportify_pro.py generate \
  -i pentest_project.json \
  -o pentest_report.docx
```

### Smart Variables

Define variables once and reuse throughout your report:

```json
{
  "smart_variables": {
    "project_name": "Cloud Migration Initiative",
    "system": "Production EKS Cluster",
    "environment": "Production"
  },
  "title": "{{project_name}} - Security Assessment",
  "scope": "This assessment covers the {{system}} in the {{environment}} environment."
}
```

Variables are automatically substituted during document generation.

### Working with Risks

The GUI includes a Risk Manager (if you extend it), or you can manually edit JSON:

```json
{
  "risks": [
    {
      "description": "Unpatched critical vulnerabilities in public-facing services",
      "category": "Security",
      "impact": "Critical",
      "likelihood": "Likely",
      "mitigation": "Implement automated patch management and monthly patching cycle",
      "owner": "Security Team"
    }
  ]
}
```

Risks are rendered as formatted tables with detailed mitigation plans.

### Timeline & Milestones

Track project phases:

```json
{
  "timeline": [
    {
      "milestone": "Phase 1: Discovery and Enumeration",
      "date": "2024-12-01",
      "status": "Completed",
      "owner": "Security Analyst",
      "notes": "Identified 45 in-scope hosts"
    },
    {
      "milestone": "Phase 2: Vulnerability Scanning",
      "date": "2024-12-05",
      "status": "In Progress",
      "owner": "Security Analyst",
      "notes": "Nessus scan running"
    }
  ]
}
```

---

## 🗂️ Project Structure

```
24-report-generator/
├── src/
│   ├── __init__.py
│   ├── reportify_pro.py       # Core engine + CLI
│   ├── reportify_gui.py       # Tkinter GUI application
│   └── generate_report.py     # Legacy Jinja2 generator (optional)
├── templates/
│   ├── weekly.html            # Legacy HTML template
│   └── examples/              # Example JSON projects for GUI/CLI
├── output/                    # Generated reports (gitignored)
├── requirements.txt
└── README.md

---

## 🛠️ Advanced Usage

### Batch Processing with CLI

Generate multiple reports from a directory of project files:

```bash
#!/bin/bash
# batch_generate.sh

for project in projects/*.json; do
  output="${project%.json}.docx"
  python src/reportify_pro.py generate -i "$project" -o "$output"
  echo "Generated: $output"
done
```

### Custom Templates (Developers)

Add your own template to `REPORT_TEMPLATES` in `reportify_pro.py`:

```python
"custom_template": {
    "name": "My Custom Report",
    "category": ReportCategory.SECURITY,
    "icon": "🔍",
    "sections": ["executive_summary", "findings", "recommendations"],
    "description": "Custom report for specific use case",
    "standards": "Internal Policy XYZ",
    "defaults": {
        "title": "Custom Report - {{project_name}}",
        "objectives": [
            "Objective 1",
            "Objective 2"
        ]
    }
}
```

### Extending the GUI

The GUI is modular and built with tkinter. To add new tabs or widgets:

1. Edit `reportify_gui.py`
2. Add new form fields in `_create_form()`
3. Update `_collect_data()` and `_populate_form()` methods
4. Test with `python src/reportify_gui.py`

---

## 📋 Template Standards & Frameworks

Each template follows industry-standard frameworks:

| Template | Standard/Framework |
|----------|-------------------|
| Vulnerability Assessment | NIST CSF, CIS Benchmarks, CVSS v3.1 |
| Penetration Testing | OWASP Top 10, PTES |
| Incident Response | NIST SP 800-61 r2, ISO 27001 A.16 |
| IAM Audit | NIST SP 800-63 |
| Cloud Migration | AWS Well-Architected Framework |
| Cost Optimization | FinOps Framework |
| System Audit | CIS Benchmarks |
| QA Test Report | IEEE 829 |
| Compliance Audit | ISO 27001, SOC 2, GDPR |

---

## 🧪 Examples

### Example 1: Vulnerability Assessment

**Input (JSON):**
```json
{
  "template_key": "vulnerability_assessment",
  "title": "Q4 2024 Production Vulnerability Assessment",
  "company_name": "Acme Corp",
  "author": "Security Team",
  "executive_summary": "Identified 23 vulnerabilities across production infrastructure...",
  "findings": [
    "Critical: CVE-2024-1234 in Apache web server (CVSS 9.8)",
    "High: Outdated SSL/TLS configurations on 5 load balancers",
    "Medium: Missing security headers on API endpoints"
  ],
  "recommendations": [
    "Patch CVE-2024-1234 within 48 hours",
    "Upgrade TLS to 1.3 across all load balancers",
    "Implement Content-Security-Policy headers"
  ],
  "tags": ["security", "vulnerability", "Q4-2024"]
}
```

**Output:** Professional 10-page Word document with:
- Branded cover page
- Table of contents
- Executive summary
- Detailed findings with CVSS ratings
- Prioritized recommendations
- Appendices with technical details

### Example 2: Cloud Migration Assessment

See `templates/examples/cloud_migration_example.json`.

---

## 🔧 Configuration

### Customizing Styles

Edit the `_setup_styles()` method in `reportify_pro.py`:

```python
@staticmethod
def _setup_styles(doc: Document):
    heading_color = RGBColor(31, 78, 120)  # Change to your brand color
    # ... customize fonts, sizes, spacing
```

### Logging

Reportify Pro logs to `reportify.log`:

```python
# Change log level in reportify_pro.py
logging.basicConfig(level=logging.DEBUG)  # More verbose
logging.basicConfig(level=logging.WARNING)  # Less verbose
```

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Add PDF export via `python-docx` + `docx2pdf`
- [ ] Add HTML export with CSS styling
- [ ] Create more example templates
- [ ] Add unit tests for document generation
- [ ] Implement dark mode for GUI
- [ ] Add multi-language support
- [ ] Create VS Code extension for inline editing

---

## 📝 License

MIT License - see LICENSE file for details.

---

## 🙋 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/Portfolio-Project/issues)
- **Documentation**: This README + inline docstrings
- **Examples**: See `templates/examples/` directory

---

## 🗺️ Roadmap

### v2.2 (Planned)
- [ ] PDF export support
- [ ] Email integration (send reports directly)
- [ ] Template marketplace (community templates)
- [ ] Collaboration features (multi-user editing)

### v3.0 (Future)
- [ ] Web-based interface (Flask/FastAPI)
- [ ] Real-time collaboration
- [ ] Version control for reports
- [ ] Integration with Jira, ServiceNow, etc.

---

## 📊 Stats

- **25+ Templates** across 7+ domains
- **1500+ Lines** of Python code
- **Professional Formatting** - Cover pages, tables, appendices
- **Smart Automation** - Variables, defaults, auto-population
- **Battle-Tested** - Used for real security assessments, audits, and project reports

---

## 🎓 Use Cases

### Security Teams
- Vulnerability assessment reports for stakeholders
- Penetration test executive summaries
- Incident response documentation
- Compliance audit reports

### DevOps Engineers
- Infrastructure design documents
- Deployment post-mortems
- Performance tuning reports
- PoC validation documents

### System Administrators
- System audit reports
- Capacity planning forecasts
- Patch management status
- Technology assessment reports

### Project Managers
- Project status updates
- Executive proposals
- Closure reports with lessons learned
- Monthly operational KPI tracking

### Cloud Architects
- Migration assessments
- Cost optimization analyses
- Multi-cloud strategy documents
- Well-Architected Framework reviews

---

## 💡 Tips & Best Practices

1. **Use Templates** - Start with the closest template and customize
2. **Smart Variables** - Define common terms once for consistency
3. **Save Often** - Use the JSON save feature to preserve work
4. **Tag Everything** - Tags make reports searchable and filterable
5. **Executive Summaries First** - Write these last but place them first
6. **Risk Matrices** - Always include impact, likelihood, and mitigation
7. **Appendices** - Use for technical details, preserving executive readability
8. **Version Control** - Store JSON project files in Git for change tracking
9. **Batch Generation** - Use CLI for recurring monthly/quarterly reports
10. **Customize Styles** - Match your organization's brand colors and fonts

---

**Built with ❤️ for IT professionals who value quality documentation.**

For questions or feedback, open an issue or reach out via LinkedIn.
python src/generate_report.py generate-all -o ./reports
```

### Scheduled Reports
```bash
# 1. Configure email and schedules
vi config/scheduler.yml

# 2. Start scheduler (runs continuously)
python src/scheduler.py --config config/scheduler.yml

# 3. Check logs for scheduled job execution
# Reports will be generated and emailed automatically
```

## Evidence

### 2026-01-22 Report Generation Run
- Run notes: [`evidence/2026-01-22/run-notes.md`](evidence/2026-01-22/run-notes.md)
- Install log: [`evidence/2026-01-22/pip-install.log`](evidence/2026-01-22/pip-install.log)
- Generation log: [`evidence/2026-01-22/generate-all.log`](evidence/2026-01-22/generate-all.log)
- Reports (HTML): [`evidence/2026-01-22/reports/`](evidence/2026-01-22/reports/)
- Timed reports (HTML): [`evidence/2026-01-22/timed-reports/`](evidence/2026-01-22/timed-reports/)
- Timing data: [`evidence/2026-01-22/report-timings.csv`](evidence/2026-01-22/report-timings.csv)

## 🔧 Configuration

### Gmail Setup
For Gmail SMTP:
1. Enable 2-factor authentication
2. Generate app-specific password
3. Use in `smtp_password` field

### Custom SMTP
```yaml
email:
  smtp_server: mail.yourcompany.com
  smtp_port: 587
  smtp_user: reports@yourcompany.com
  smtp_password: your-password
```

### Schedule Customization
Use cron-style scheduling:
```yaml
schedules:
  custom_job:
    day_of_week: tue,thu  # Tuesday and Thursday
    hour: 14              # 2 PM
    minute: 30            # :30
```


## Code Generation Prompts

This section contains AI-assisted code generation prompts that can help you recreate or extend project components. These prompts are designed to work with AI coding assistants like Claude, GPT-4, or GitHub Copilot.

### Code Components

#### 1. Core Functionality
```
Create the main application logic for [specific feature], including error handling, logging, and configuration management
```

#### 2. API Integration
```
Generate code to integrate with [external service] API, including authentication, rate limiting, and retry logic
```

#### 3. Testing
```
Write comprehensive tests for [component], covering normal operations, edge cases, and error scenarios
```

### How to Use These Prompts

1. **Copy the prompt** from the code block above
2. **Customize placeholders** (replace [bracketed items] with your specific requirements)
3. **Provide context** to your AI assistant about:
   - Your development environment and tech stack
   - Existing code patterns and conventions in this project
   - Any constraints or requirements specific to your use case
4. **Review and adapt** the generated code before using it
5. **Test thoroughly** and adjust as needed for your specific scenario

### Best Practices

- Always review AI-generated code for security vulnerabilities
- Ensure generated code follows your project's coding standards
- Add appropriate error handling and logging
- Write tests for AI-generated components
- Document any assumptions or limitations
- Keep sensitive information (credentials, keys) in environment variables
