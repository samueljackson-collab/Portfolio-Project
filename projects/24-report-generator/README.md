# Project 24: Portfolio Report Generator

**Status**: ✅ **100% Complete** - Production-Ready

## Overview

Comprehensive portfolio report generation system with automated scheduling, email delivery, and historical comparison. Generates professional HTML and PDF reports from customizable templates, with support for weekly/monthly automated delivery to stakeholders.

## 🎯 Features

### Core Components
- **Report Generation**: HTML and PDF reports using Jinja2 templates and WeasyPrint
- **Data Collection**: Automated portfolio scanning and metrics aggregation
- **Scheduled Generation**: APScheduler-based automation for weekly/monthly reports
- **Email Delivery**: SMTP-based email delivery with attachments
- **Historical Comparison**: Track trends and compare metrics over time

### Advanced Features
- ✅ **Scheduled Generation** - Weekly, monthly, and daily automated reports
- ✅ **Email Delivery** - Multi-recipient email with HTML/PDF attachments
- ✅ **Historical Comparison** - Trend analysis and metric deltas
- ✅ **Multiple Templates** - Executive summary, project status, technical docs
- ✅ **CLI Interface** - Rich command-line interface with Click
- ✅ **Configurable** - YAML-based configuration for schedules and recipients

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
pip install -r requirements.txt
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

