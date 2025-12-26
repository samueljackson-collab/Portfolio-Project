# Portfolio Demo Scripts

Comprehensive demonstration scripts to showcase the Portfolio Project capabilities.

## Quick Start

```bash
# Make the script executable (first time only)
chmod +x demo-scripts.sh

# View all available commands
./demo-scripts.sh help

# First time setup - installs dependencies
./demo-scripts.sh setup

# Generate sample reports
./demo-scripts.sh generate

# Run interactive demo menu
./demo-scripts.sh demo

# Run tests
./demo-scripts.sh test

# Clean up generated artifacts
./demo-scripts.sh clean
```

## Available Commands

### `setup`
Installs all required dependencies and prepares the demo environment.

- Creates Python virtual environment
- Installs required Python packages (python-docx, pydantic, pillow, jinja2, weasyprint)
- Creates necessary directories (demo-output, reports, sample-data)

**Usage:**
```bash
./demo-scripts.sh setup
```

### `generate`
Generates sample professional reports demonstrating the report generation capabilities.

**Sample Reports Created:**
- **Vulnerability Assessment Report** - Security vulnerability analysis
- **Cloud Migration Report** - AWS cloud migration assessment
- **Incident Response Report** - Security incident documentation
- **AWS Infrastructure Report** - Infrastructure architecture documentation

**Output Location:** `./reports/`

**Usage:**
```bash
./demo-scripts.sh generate
```

### `demo`
Launches an interactive menu to explore all portfolio projects.

**Featured Projects:**
1. Report Generator - Professional report generation system
2. AWS Infrastructure Automation - Terraform-managed cloud infrastructure
3. IAM Security Hardening - Zero-trust security implementation
4. Kubernetes on EKS - Production-grade container orchestration
5. Serverless API Platform - Event-driven serverless architecture
6. AI/ML Tab Organization App - Cross-platform AI application
7. Multi-Region Disaster Recovery - Global DR solution
8. DevSecOps Pipeline - Secure CI/CD implementation

**Usage:**
```bash
./demo-scripts.sh demo
```

### `test`
Runs the test suite to verify setup and functionality.

**Tests Include:**
- Sample data validation
- JSON file integrity checks
- Directory structure verification
- Project structure validation

**Usage:**
```bash
./demo-scripts.sh test
```

### `reportify`
Launches the Report Generator application.

**Usage:**
```bash
./demo-scripts.sh reportify
```

### `clean`
Removes all generated demo artifacts and temporary files.

**Cleaned Items:**
- Generated reports
- Sample data files
- Test files
- Python cache files

**Usage:**
```bash
./demo-scripts.sh clean
```

## Features

### Color-Coded Output
The script uses ANSI color codes for clear, readable output:
- 🔵 **Blue** - Headers and sections
- 🟢 **Green** - Success messages
- 🟡 **Yellow** - Information and progress
- 🔴 **Red** - Errors and warnings

### Sample Report Templates

#### Vulnerability Assessment Report
Demonstrates security vulnerability analysis and remediation planning:
- CVSS scoring and risk classification
- Compliance requirements (SOC 2, PCI DSS, ISO 27001)
- Prioritized remediation roadmap
- Executive summary with key metrics

#### Cloud Migration Report
Showcases cloud migration planning and assessment:
- Current infrastructure analysis
- Cloud readiness assessment
- Cost comparison and TCO analysis
- Phased migration strategy

#### Incident Response Report
Illustrates security incident documentation:
- Timeline and incident metadata
- Attack pattern analysis
- Impact assessment
- Remediation recommendations

#### AWS Infrastructure Report
Documents cloud infrastructure architecture:
- Multi-tier architecture design
- High availability configuration
- Cost optimization strategies
- Infrastructure as Code implementation

## Directory Structure

```
Portfolio-Project/
├── demo-scripts.sh          # Main demo script
├── DEMO_SCRIPTS_README.md   # This file
├── sample-data/             # Generated sample JSON data
│   ├── vuln-assessment.json
│   ├── cloud-migration.json
│   ├── incident-response.json
│   └── aws-infrastructure.json
├── reports/                 # Generated reports
│   ├── vuln-assessment-report.txt
│   ├── cloud-migration-report.txt
│   ├── incident-response-report.txt
│   └── aws-infrastructure-report.txt
├── demo-output/            # Additional demo outputs
└── venv/                   # Python virtual environment
```

## Requirements

### System Requirements
- **Python 3.7+** - Core scripting language
- **pip3** - Python package manager
- **bash** - Shell environment

### Python Dependencies
Automatically installed by the `setup` command:
- `python-docx` - DOCX file generation
- `pydantic` - Data validation
- `pillow` - Image processing
- `jinja2` - Template engine
- `weasyprint` - PDF generation
- `pytest` - Testing framework (for tests)
- `pytest-cov` - Test coverage (for tests)

## Examples

### Complete Workflow Example

```bash
# 1. First time setup
./demo-scripts.sh setup

# 2. Generate sample reports
./demo-scripts.sh generate

# 3. View generated reports
ls -lh reports/
cat reports/vuln-assessment-report.txt

# 4. Run tests to verify
./demo-scripts.sh test

# 5. Clean up when done
./demo-scripts.sh clean
```

### Interactive Demo Example

```bash
# Launch interactive menu
./demo-scripts.sh demo

# Follow the prompts:
# - Select a project (1-8)
# - View project details
# - Return to menu or exit
```

## Troubleshooting

### Virtual Environment Issues
If you encounter virtual environment issues:
```bash
# Remove existing venv
rm -rf venv/

# Re-run setup
./demo-scripts.sh setup
```

### Permission Denied Error
If you get a "permission denied" error:
```bash
# Make script executable
chmod +x demo-scripts.sh
```

### Missing Dependencies
If dependencies are missing:
```bash
# Re-run setup command
./demo-scripts.sh setup

# Or manually install
source venv/bin/activate
pip install python-docx pydantic pillow jinja2 weasyprint
```

### Python Version Issues
Ensure Python 3.7 or higher is installed:
```bash
python3 --version

# If too old, install newer version
# (instructions vary by OS)
```

## Integration with Portfolio Projects

The demo scripts integrate with actual portfolio projects:

- **Project 24** - Report Generator (`projects/24-report-generator/`)
- **Project 1** - AWS Infrastructure (`projects/1-aws-infrastructure-automation/`)
- **Project 3** - Kubernetes (`projects/3-kubernetes-cicd/`)
- **Project P02** - IAM Security (`projects/p02-iam-hardening/`)
- **Project P11** - Serverless (`projects/p11-serverless/`)
- **Project 07** - AI/ML App (`projects/07-aiml-automation/PRJ-AIML-002/`)
- And many more!

## Contributing

This is a portfolio demonstration project. To contribute or suggest improvements:

1. Review the script functionality
2. Test the commands
3. Report issues or suggest enhancements
4. Follow the project's contribution guidelines

## License

This is a portfolio demonstration project. See the main repository LICENSE file for details.

## Contact

**Samuel Jackson**
- GitHub: [samueljackson-collab](https://github.com/samueljackson-collab)
- LinkedIn: [sams-jackson](https://www.linkedin.com/in/sams-jackson)

## Changelog

### Version 1.0.0 (2025-11-10)
- Initial release
- Complete setup and installation process
- Sample report generation (4 report types)
- Interactive demo menu
- Test suite implementation
- Cleanup functionality
- Comprehensive documentation

---

**Last Updated:** 2025-11-10
**Status:** Production Ready
**Next Steps:** Integrate with additional portfolio projects and templates
