# Runbook — Project 24 (Portfolio Report Generator)

## Overview

Production operations runbook for the Portfolio Report Generator service. This runbook covers automated report generation, template management, PDF/HTML rendering operations, scheduling, and distribution of portfolio status reports using Jinja2 templates and WeasyPrint.

**System Components:**
- Python report generation engine
- Jinja2 templating system
- WeasyPrint PDF renderer
- Report scheduling system
- Template management
- Data aggregation layer
- Distribution service (email/S3/webhook)

---

## SLOs/SLIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Report generation success rate** | 99% | Successful report completions |
| **Report generation time (p95)** | < 60 seconds | Template render → output file |
| **Template validation success** | 100% | Valid Jinja2 syntax |
| **Scheduled report delivery** | 99.5% | On-time report delivery |
| **PDF rendering success rate** | 98% | Successful WeasyPrint conversions |
| **Data aggregation latency** | < 30 seconds | Source data collection time |
| **Report file size (p95)** | < 5MB | Generated report file size |

---

## Dashboards & Alerts

### Dashboards

#### Service Health Dashboard
```bash
# Check service status
systemctl status report-generator.service

# Check recent report generations
ls -lth /var/lib/report-generator/reports/ | head -10

# Check service logs
journalctl -u report-generator.service -n 50

# Check process health
ps aux | grep generate_report.py
```

#### Report Generation Dashboard
```bash
# List recent reports
python -c "
from src.generate_report import list_recent_reports
reports = list_recent_reports(limit=20)
for r in reports:
    print(f'{r.timestamp} - {r.template} - {r.status} - {r.output_file}')"

# Check generation statistics
python -c "
from src.generate_report import get_generation_stats
stats = get_generation_stats()
print(f'Success rate: {stats.success_rate}%')
print(f'Average duration: {stats.avg_duration}s')
print(f'Total reports: {stats.total_count}')"

# View scheduled reports
crontab -l | grep generate_report
```

#### Template Health Dashboard
```bash
# List available templates
ls -lh /var/lib/report-generator/templates/

# Validate all templates
python -c "
from src.generate_report import validate_all_templates
validate_all_templates()"

# Check template usage
python -c "
from src.generate_report import get_template_usage_stats
stats = get_template_usage_stats()
for template, count in stats.items():
    print(f'{template}: {count} reports')"
```

### Alerts

| Severity | Condition | Response Time | Action |
|----------|-----------|---------------|--------|
| **P0** | All scheduled reports failing | Immediate | Restart service, check dependencies |
| **P0** | Data source unreachable | Immediate | Restore connectivity, check credentials |
| **P1** | Report generation success rate < 95% | 30 minutes | Investigate failures, check templates |
| **P1** | Scheduled report missed delivery | 1 hour | Manually generate, investigate scheduler |
| **P2** | Slow report generation (>2 min) | 2 hours | Optimize templates, check resources |
| **P2** | PDF rendering failures (>5%) | 2 hours | Check WeasyPrint, validate HTML |
| **P3** | Individual report failure | 4 hours | Review logs, fix template |
| **P3** | Template validation warnings | 8 hours | Update template syntax |

#### Alert Queries

```bash
# Check service health
if ! systemctl is-active --quiet report-generator.service; then
  echo "ALERT: Report generator service is down"
  exit 1
fi

# Check recent failures
FAILURE_COUNT=$(find /var/lib/report-generator/reports/ -name "*.error" -mtime -1 | wc -l)
if [ $FAILURE_COUNT -gt 5 ]; then
  echo "ALERT: $FAILURE_COUNT report generation failures in last 24 hours"
fi

# Check scheduled report execution
EXPECTED_REPORTS=3  # Daily + Weekly + Monthly
ACTUAL_REPORTS=$(find /var/lib/report-generator/reports/ -name "*.html" -mtime -1 | wc -l)
if [ $ACTUAL_REPORTS -lt $EXPECTED_REPORTS ]; then
  echo "ALERT: Only $ACTUAL_REPORTS reports generated (expected $EXPECTED_REPORTS)"
fi

# Check disk space for reports
DISK_USAGE=$(df -h /var/lib/report-generator/reports | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
  echo "ALERT: Report storage at ${DISK_USAGE}% capacity"
fi
```

---

## Standard Operations

### Service Management

#### Start/Stop Service
```bash
# Start report generator service
sudo systemctl start report-generator.service

# Stop service
sudo systemctl stop report-generator.service

# Restart service
sudo systemctl restart report-generator.service

# Check status
sudo systemctl status report-generator.service

# Enable auto-start
sudo systemctl enable report-generator.service

# View logs
sudo journalctl -u report-generator.service -f
```

#### Manual Report Generation
```bash
# Activate Python environment
cd /opt/report-generator
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate report with default template
python src/generate_report.py \
  --template templates/weekly.html \
  --output reports/weekly-$(date +%Y%m%d).html

# Generate PDF report
python src/generate_report.py \
  --template templates/monthly.html \
  --output reports/monthly-$(date +%Y%m%d).pdf \
  --format pdf

# Generate with custom data
python src/generate_report.py \
  --template templates/custom.html \
  --data-file data/custom-data.json \
  --output reports/custom-report.html

# Generate with inline parameters
python src/generate_report.py \
  --template templates/summary.html \
  --param project_count=25 \
  --param reporting_period="November 2025" \
  --output reports/summary.html
```

#### Configure Service
```bash
# Edit service configuration
vim /etc/report-generator/config.yaml

# Example configuration:
cat > /etc/report-generator/config.yaml << 'EOF'
generator:
  template_dir: /var/lib/report-generator/templates
  output_dir: /var/lib/report-generator/reports
  data_sources:
    prometheus:
      url: http://localhost:9090
    github:
      api_url: https://api.github.com
      token: ${GITHUB_TOKEN}
    jira:
      url: https://company.atlassian.net
      credentials: ${JIRA_CREDENTIALS}

  pdf_settings:
    page_size: A4
    orientation: portrait
    margin: 2cm

  scheduling:
    daily_report:
      template: daily.html
      cron: "0 8 * * *"
      recipients: ["team@company.com"]
    weekly_report:
      template: weekly.html
      cron: "0 8 * * 1"
      recipients: ["management@company.com"]
    monthly_report:
      template: monthly.html
      cron: "0 8 1 * *"
      recipients: ["executives@company.com"]

  distribution:
    email:
      smtp_server: smtp.company.com
      smtp_port: 587
      from_address: reports@company.com
    s3:
      bucket: company-reports
      region: us-east-1
      prefix: portfolio/
EOF

# Validate configuration
python -c "from src.generate_report import validate_config; validate_config('/etc/report-generator/config.yaml')"

# Reload service
sudo systemctl restart report-generator.service
```

### Template Management

#### List Templates
```bash
# List all available templates
ls -lh /var/lib/report-generator/templates/

# Show template details
python -c "
from src.generate_report import list_templates
templates = list_templates()
for t in templates:
    print(f'{t.name}: {t.description}')"

# View template content
cat /var/lib/report-generator/templates/weekly.html

# Check template variables
python -c "
from src.generate_report import get_template_variables
vars = get_template_variables('weekly.html')
print('Required variables:', vars)"
```

#### Create/Update Template
```bash
# Create new template
cat > /var/lib/report-generator/templates/custom-report.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{{ report_title }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2cm; }
        h1 { color: #333; }
        .metric { margin: 1em 0; padding: 1em; background: #f5f5f5; }
        .metric-value { font-size: 2em; font-weight: bold; color: #0066cc; }
    </style>
</head>
<body>
    <h1>{{ report_title }}</h1>
    <p>Generated: {{ generation_time }}</p>

    <div class="metric">
        <h2>Total Projects</h2>
        <div class="metric-value">{{ project_count }}</div>
    </div>

    <div class="metric">
        <h2>Active Deployments</h2>
        <div class="metric-value">{{ deployment_count }}</div>
    </div>

    <h2>Project Status</h2>
    <table>
        <tr>
            <th>Project</th>
            <th>Status</th>
            <th>Health</th>
        </tr>
        {% for project in projects %}
        <tr>
            <td>{{ project.name }}</td>
            <td>{{ project.status }}</td>
            <td>{{ project.health }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
EOF

# Validate new template
python -c "from src.generate_report import validate_template; validate_template('custom-report.html')"

# Test render template
python src/generate_report.py \
  --template templates/custom-report.html \
  --param report_title="Test Report" \
  --param project_count=25 \
  --output /tmp/test-report.html \
  --dry-run

# If valid, generate actual report
python src/generate_report.py \
  --template templates/custom-report.html \
  --output reports/custom-$(date +%Y%m%d).html
```

#### Version Control Templates
```bash
# Templates are stored in Git
cd /var/lib/report-generator/templates

# View changes
git status
git diff

# Commit changes
git add *.html
git commit -m "feat: add custom report template"
git push

# Pull latest templates
git pull
```

### Report Generation

#### Generate Ad-Hoc Report
```bash
# Generate HTML report
python src/generate_report.py \
  --template templates/adhoc.html \
  --output reports/adhoc-$(date +%Y%m%d-%H%M).html

# Generate PDF report
python src/generate_report.py \
  --template templates/executive-summary.html \
  --output reports/executive-summary-$(date +%Y%m%d).pdf \
  --format pdf

# Generate with external data
python src/generate_report.py \
  --template templates/data-driven.html \
  --data-source prometheus \
  --query 'sum(up{job="portfolio"})' \
  --output reports/metrics-report.html

# Generate and email
python src/generate_report.py \
  --template templates/weekly.html \
  --output reports/weekly.html \
  --email recipient@company.com \
  --subject "Weekly Portfolio Report"
```

#### Schedule Report Generation
```bash
# View current scheduled reports
crontab -l | grep generate_report

# Add daily report
crontab -e
# Add line:
# 0 8 * * * cd /opt/report-generator && ./venv/bin/python src/generate_report.py --template templates/daily.html --output reports/daily-$(date +\%Y\%m\%d).html

# Add weekly report (Monday 8 AM)
# 0 8 * * 1 cd /opt/report-generator && ./venv/bin/python src/generate_report.py --template templates/weekly.html --output reports/weekly-$(date +\%Y\%m\%d).pdf --format pdf --email team@company.com

# Add monthly report (1st of month, 8 AM)
# 0 8 1 * * cd /opt/report-generator && ./venv/bin/python src/generate_report.py --template templates/monthly.html --output reports/monthly-$(date +\%Y\%m\%d).pdf --format pdf --email management@company.com

# Verify cron jobs
crontab -l
```

#### Test Report Generation
```bash
# Dry run (validate without generating)
python src/generate_report.py \
  --template templates/test.html \
  --dry-run

# Generate with verbose output
python src/generate_report.py \
  --template templates/test.html \
  --output /tmp/test.html \
  --verbose

# Generate with debug logging
LOGLEVEL=DEBUG python src/generate_report.py \
  --template templates/test.html \
  --output /tmp/test.html

# Benchmark generation time
time python src/generate_report.py \
  --template templates/complex.html \
  --output /tmp/benchmark.html
```

### Data Source Management

#### Configure Data Sources
```bash
# Add Prometheus data source
python -c "
from src.generate_report import add_data_source
add_data_source(
    name='prometheus',
    type='prometheus',
    url='http://localhost:9090',
    auth_type='bearer',
    token='${PROMETHEUS_TOKEN}'
)"

# Add GitHub data source
python -c "
from src.generate_report import add_data_source
add_data_source(
    name='github',
    type='github',
    api_url='https://api.github.com',
    token='${GITHUB_TOKEN}'
)"

# Test data source connection
python -c "
from src.generate_report import test_data_source
result = test_data_source('prometheus')
print(f'Connection test: {\"SUCCESS\" if result else \"FAILED\"}')"
```

#### Fetch Data for Reports
```bash
# Fetch Prometheus metrics
python -c "
from src.generate_report import fetch_prometheus_data
data = fetch_prometheus_data(
    query='sum(up{job=\"portfolio\"}) by (instance)',
    start='2025-11-09T00:00:00Z',
    end='2025-11-10T00:00:00Z'
)
print(data)"

# Fetch GitHub data
python -c "
from src.generate_report import fetch_github_data
data = fetch_github_data(
    repo='org/Portfolio-Project',
    endpoint='pulls',
    params={'state': 'all', 'per_page': 100}
)
print(f'Found {len(data)} pull requests')"

# Cache data for reuse
python scripts/cache-report-data.py --sources prometheus,github --period 7d
```

### Distribution Management

#### Email Reports
```bash
# Send report via email
python src/generate_report.py \
  --template templates/weekly.html \
  --output reports/weekly.html \
  --email recipient@company.com \
  --subject "Weekly Portfolio Report" \
  --body "Please find attached the weekly portfolio status report."

# Send with attachments
python scripts/send-report.py \
  --report reports/weekly.html \
  --recipients team@company.com,manager@company.com \
  --subject "Weekly Report" \
  --attachments reports/metrics.csv

# Test email configuration
python -c "from src.generate_report import test_email_config; test_email_config()"
```

#### Upload to S3
```bash
# Upload report to S3
python src/generate_report.py \
  --template templates/monthly.html \
  --output reports/monthly.pdf \
  --format pdf \
  --s3-upload \
  --s3-bucket company-reports \
  --s3-key portfolio/monthly-$(date +%Y%m%d).pdf

# Or use upload script
python scripts/upload-report.py \
  --file reports/monthly.pdf \
  --bucket company-reports \
  --key portfolio/monthly-$(date +%Y%m%d).pdf \
  --public

# Verify upload
aws s3 ls s3://company-reports/portfolio/
```

#### Webhook Delivery
```bash
# Send report via webhook
python scripts/webhook-deliver.py \
  --report reports/daily.html \
  --webhook https://hooks.company.com/report-delivery \
  --metadata '{"type":"daily","date":"2025-11-10"}'

# Configure webhook
python -c "
from src.generate_report import configure_webhook
configure_webhook(
    url='https://hooks.company.com/report-delivery',
    auth_header='Bearer ${WEBHOOK_TOKEN}',
    retry_count=3
)"
```

---

## Incident Response

### Detection

**Automated Detection:**
- Service health check failures
- Scheduled report generation failures
- Data source connectivity failures
- PDF rendering errors
- Email delivery failures

**Manual Detection:**
```bash
# Check service health
systemctl status report-generator.service

# Check for errors
journalctl -u report-generator.service --since "1 hour ago" | grep -i "error\|failed"

# Check recent report generation
ls -lt /var/lib/report-generator/reports/ | head -20

# Check for error files
find /var/lib/report-generator/reports/ -name "*.error" -mtime -1

# Check scheduled reports executed
grep -i "report generation" /var/log/report-generator/scheduler.log
```

### Triage

#### Severity Classification

### P0: All Reports Failing
- Service completely down
- All scheduled reports failing
- Critical data sources unreachable
- Complete email delivery failure

### P1: Major Report Failure
- Critical scheduled report missed
- Multiple report generation failures
- PDF rendering completely broken
- Primary data source unavailable

### P2: Degraded Service
- Individual report failures
- Slow report generation (>2 min)
- Intermittent data source issues
- Some email deliveries failing

### P3: Minor Issues
- Template warnings
- Non-critical data source timeout
- Individual email failure
- Report file size large

### Incident Response Procedures

#### P0: Service Down

**Immediate Actions (0-2 minutes):**
```bash
# 1. Check service status
systemctl status report-generator.service

# 2. Attempt restart
sudo systemctl restart report-generator.service

# 3. Verify restart
sleep 5
systemctl is-active report-generator.service

# 4. Check logs for errors
journalctl -u report-generator.service -n 100 --no-pager
```

**Investigation (2-10 minutes):**
```bash
# Check Python errors
journalctl -u report-generator.service | grep -i "traceback\|exception" | tail -50

# Check dependencies
cd /opt/report-generator
source venv/bin/activate
pip check

# Check configuration
python -c "from src.generate_report import validate_config; validate_config('/etc/report-generator/config.yaml')"

# Check file permissions
ls -la /var/lib/report-generator/reports/
ls -la /var/lib/report-generator/templates/

# Check disk space
df -h /var/lib/report-generator
```

**Recovery:**
```bash
# Fix dependency issues
cd /opt/report-generator
source venv/bin/activate
pip install -r requirements.txt --force-reinstall

# Fix permissions
sudo chown -R report-generator:report-generator /var/lib/report-generator
sudo chmod 755 /var/lib/report-generator/reports

# Clear temporary files
rm -rf /tmp/report-generator/*

# Restart service
sudo systemctl restart report-generator.service

# Verify recovery
python src/generate_report.py --template templates/test.html --output /tmp/test.html
```

#### P0: Data Sources Unreachable

**Investigation:**
```bash
# Test Prometheus connection
curl http://localhost:9090/-/healthy

# Test GitHub API
curl -H "Authorization: token ${GITHUB_TOKEN}" https://api.github.com/rate_limit

# Check network connectivity
ping -c 3 localhost
netstat -tlnp | grep :9090

# Check credentials
python -c "
from src.generate_report import test_all_data_sources
test_all_data_sources()"
```

**Recovery:**
```bash
# Restart Prometheus if down
sudo systemctl restart prometheus

# Update credentials if expired
vim /etc/report-generator/config.yaml
# Update GITHUB_TOKEN, PROMETHEUS_TOKEN, etc.

# Test connections
python -c "from src.generate_report import test_data_source; test_data_source('prometheus')"
python -c "from src.generate_report import test_data_source; test_data_source('github')"

# Retry failed reports
python scripts/retry-failed-reports.py --since=24h
```

#### P1: Critical Scheduled Report Missed

**Investigation:**
```bash
# Check cron execution
grep -i "generate_report" /var/log/cron | tail -20

# Check crontab
crontab -l | grep generate_report

# Check scheduler logs
cat /var/log/report-generator/scheduler.log | tail -50

# Check if report file exists
ls -lh /var/lib/report-generator/reports/ | grep $(date +%Y%m%d)
```

**Manual Generation:**
```bash
# Identify missed report
TEMPLATE="weekly.html"
OUTPUT_FILE="reports/weekly-$(date +%Y%m%d).html"

# Generate report manually
cd /opt/report-generator
source venv/bin/activate
python src/generate_report.py \
  --template templates/$TEMPLATE \
  --output $OUTPUT_FILE \
  --verbose

# Email report manually
python scripts/send-report.py \
  --report $OUTPUT_FILE \
  --recipients management@company.com \
  --subject "Weekly Portfolio Report (Manual Generation)"

# Verify cron job for future
crontab -e
# Verify schedule is correct

# Test cron job execution
./venv/bin/python src/generate_report.py --template templates/test.html --output /tmp/cron-test.html
```

#### P1: PDF Rendering Failures

**Investigation:**
```bash
# Check WeasyPrint installation
python -c "import weasyprint; print(weasyprint.__version__)"

# Test PDF rendering
python -c "
from weasyprint import HTML
HTML('<h1>Test</h1>').write_pdf('/tmp/test.pdf')
print('PDF test: SUCCESS')"

# Check system dependencies
dpkg -l | grep -E "libpango|libcairo|libgdk-pixbuf"

# Check error logs
grep -i "weasyprint\|pdf" /var/log/report-generator/errors.log | tail -50
```

**Recovery:**
```bash
# Reinstall WeasyPrint dependencies
sudo apt-get update
sudo apt-get install --reinstall \
  libpango-1.0-0 libpangoft2-1.0-0 \
  libcairo2 libgdk-pixbuf2.0-0

# Reinstall WeasyPrint
cd /opt/report-generator
source venv/bin/activate
pip uninstall -y weasyprint
pip install weasyprint

# Test PDF generation
python src/generate_report.py \
  --template templates/simple.html \
  --output /tmp/test.pdf \
  --format pdf

# If still failing, generate HTML instead
python src/generate_report.py \
  --template templates/weekly.html \
  --output reports/weekly-$(date +%Y%m%d).html \
  --format html

# Convert HTML to PDF manually if needed
wkhtmltopdf reports/weekly.html reports/weekly.pdf
```

#### P2: Slow Report Generation

**Investigation:**
```bash
# Profile report generation
python -m cProfile -o profile.stats src/generate_report.py \
  --template templates/slow-report.html \
  --output /tmp/test.html

# Analyze profile
python -c "
import pstats
stats = pstats.Stats('profile.stats')
stats.sort_stats('cumulative')
stats.print_stats(20)"

# Check data source query time
time python -c "from src.generate_report import fetch_prometheus_data; fetch_prometheus_data('up')"

# Check template complexity
wc -l /var/lib/report-generator/templates/slow-report.html
```

**Optimization:**
```bash
# Cache slow data source queries
python scripts/cache-report-data.py --sources prometheus --period 1h

# Optimize template
# - Reduce loops
# - Simplify CSS
# - Remove unused sections

# Use cached data
python src/generate_report.py \
  --template templates/optimized.html \
  --use-cache \
  --output reports/fast-report.html

# Increase timeout if necessary
python src/generate_report.py \
  --template templates/complex.html \
  --timeout 300 \
  --output reports/report.html
```

### Post-Incident

**After Resolution:**
```bash
# Document incident
cat > /var/log/report-generator/incidents/incident-$(date +%Y%m%d-%H%M).md << 'EOF'
# Report Generator Incident Report

**Date:** $(date)
**Severity:** P1
**Duration:** 45 minutes
**Component:** PDF Rendering

## Timeline
- 08:00: Scheduled weekly report failed
- 08:15: Alert received for missed report
- 08:20: Investigation started
- 08:30: Identified WeasyPrint dependency issue
- 08:45: Dependencies reinstalled
- 09:00: Report successfully generated and delivered

## Root Cause
System update removed libcairo2 dependency required by WeasyPrint

## Mitigation
- Reinstalled system dependencies
- Regenerated and delivered missed report
- Added dependency health check

## Action Items
- [ ] Pin system dependencies
- [ ] Add pre-generation dependency check
- [ ] Implement fallback to HTML if PDF fails
- [ ] Add monitoring for dependency health
- [ ] Document WeasyPrint dependencies

EOF

# Update monitoring
# Add dependency health checks

# Update runbook
# Document new recovery procedures
```

---

## Troubleshooting

### Common Issues & Solutions

#### Issue: "Template not found"

**Symptoms:**
```bash
$ python src/generate_report.py --template custom.html
Error: Template 'custom.html' not found
```

**Diagnosis:**
```bash
# Check template directory
ls -la /var/lib/report-generator/templates/

# Check template path configuration
python -c "from src.generate_report import get_config; print(get_config()['template_dir'])"

# Check file permissions
ls -l /var/lib/report-generator/templates/custom.html
```

**Solution:**
```bash
# Create missing template
cp /var/lib/report-generator/templates/sample.html \
   /var/lib/report-generator/templates/custom.html

# Or fix template path
python src/generate_report.py \
  --template /var/lib/report-generator/templates/custom.html \
  --output report.html

# Or set TEMPLATE_DIR environment variable
export TEMPLATE_DIR=/var/lib/report-generator/templates
python src/generate_report.py --template custom.html --output report.html
```

---

#### Issue: "Jinja2TemplateSyntaxError"

**Symptoms:**
```bash
jinja2.exceptions.TemplateSyntaxError: unexpected end of statement
```

**Diagnosis:**
```bash
# Validate template syntax
python -c "
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('/var/lib/report-generator/templates'))
template = env.get_template('custom.html')
print('Template syntax: VALID')"

# Check for common syntax errors
grep -n "{% for\|{% if\|{% end" /var/lib/report-generator/templates/custom.html
```

**Solution:**
```bash
# Fix template syntax
vim /var/lib/report-generator/templates/custom.html

# Common fixes:
# - Ensure all {% for %} have {% endfor %}
# - Ensure all {% if %} have {% endif %}
# - Check for unclosed {{ }}
# - Verify variable names

# Validate fix
python -c "from src.generate_report import validate_template; validate_template('custom.html')"
```

---

#### Issue: Email delivery failure

**Symptoms:**
- Reports generated but not emailed
- SMTP connection errors

**Diagnosis:**
```bash
# Test SMTP configuration
python -c "
from src.generate_report import test_email_config
test_email_config()"

# Check SMTP server connectivity
telnet smtp.company.com 587

# Check email logs
grep -i "email\|smtp" /var/log/report-generator/errors.log | tail -20
```

**Solution:**
```bash
# Update SMTP configuration
vim /etc/report-generator/config.yaml
# Update smtp_server, smtp_port, credentials

# Test email sending
python scripts/send-test-email.py --recipient admin@company.com

# Send report manually
python scripts/send-report.py \
  --report reports/weekly.html \
  --recipients team@company.com \
  --subject "Weekly Report"
```

---

## Disaster Recovery & Backups

### RPO/RTO

- **RPO** (Recovery Point Objective): 24 hours (daily template/config backups)
- **RTO** (Recovery Time Objective): 30 minutes (service restoration)

### Backup Strategy

**Template and Configuration Backup:**
```bash
# Automated daily backup
cat > /etc/cron.daily/report-generator-backup << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/report-generator/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup templates
tar czf $BACKUP_DIR/templates.tar.gz /var/lib/report-generator/templates/

# Backup configuration
cp /etc/report-generator/config.yaml $BACKUP_DIR/

# Backup generated reports (last 7 days)
find /var/lib/report-generator/reports/ -mtime -7 | \
  tar czf $BACKUP_DIR/recent-reports.tar.gz -T -

# Cleanup old backups
find /backup/report-generator/ -type d -mtime +30 -exec rm -rf {} +
EOF

chmod +x /etc/cron.daily/report-generator-backup
```

**Version Control Backup:**
```bash
# Backup templates to Git
cd /var/lib/report-generator/templates
git add *.html
git commit -m "backup: templates $(date +%Y-%m-%d)"
git push

# Backup scripts
cd /opt/report-generator
git add src/ scripts/ requirements.txt
git commit -m "backup: report generator $(date +%Y-%m-%d)"
git push
```

### Disaster Recovery Procedures

**Complete Service Loss:**
```bash
# 1. Restore code from Git
cd /opt
git clone https://github.com/org/report-generator.git
cd report-generator

# 2. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Restore templates
LATEST_BACKUP=$(ls -t /backup/report-generator/*/templates.tar.gz | head -1)
mkdir -p /var/lib/report-generator
tar xzf $LATEST_BACKUP -C /

# 4. Restore configuration
BACKUP_DATE=$(ls -t /backup/report-generator/ | head -1)
cp /backup/report-generator/$BACKUP_DATE/config.yaml /etc/report-generator/

# 5. Setup systemd service
sudo cp scripts/report-generator.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable report-generator.service
sudo systemctl start report-generator.service

# 6. Verify service
python src/generate_report.py --template templates/test.html --output /tmp/test.html
```

---

## Maintenance Procedures

### Daily Tasks
```bash
# Check service health
systemctl status report-generator.service

# Verify scheduled reports ran
ls -lt /var/lib/report-generator/reports/ | head -5

# Check for errors
journalctl -u report-generator.service --since "24 hours ago" | grep -i error

# Check disk usage
df -h /var/lib/report-generator/reports
```

### Weekly Tasks
```bash
# Review report generation success rate
python scripts/report-statistics.py --period 7d

# Validate all templates
python -c "from src.generate_report import validate_all_templates; validate_all_templates()"

# Test data source connections
python -c "from src.generate_report import test_all_data_sources; test_all_data_sources()"

# Clean old reports
find /var/lib/report-generator/reports/ -name "*.html" -mtime +30 -delete
find /var/lib/report-generator/reports/ -name "*.pdf" -mtime +90 -delete
```

### Monthly Tasks
```bash
# Update dependencies
cd /opt/report-generator
source venv/bin/activate
pip list --outdated
pip install --upgrade -r requirements.txt

# Review and optimize templates
python scripts/analyze-template-performance.py

# Test disaster recovery
# Follow DR drill procedure

# Update documentation
git pull
# Review and update this runbook
```

---

## Quick Reference

### Most Common Operations
```bash
# Check service status
systemctl status report-generator.service

# Generate report
python src/generate_report.py --template templates/weekly.html --output reports/weekly.html

# Generate PDF
python src/generate_report.py --template templates/monthly.html --output reports/monthly.pdf --format pdf

# View logs
journalctl -u report-generator.service -f

# List recent reports
ls -lth /var/lib/report-generator/reports/ | head -10

# Validate template
python -c "from src.generate_report import validate_template; validate_template('custom.html')"

# Test email
python scripts/send-test-email.py --recipient admin@company.com
```

### Emergency Response
```bash
# P0: Service down
sudo systemctl restart report-generator.service
journalctl -u report-generator.service -n 100

# P0: Data sources unreachable
python -c "from src.generate_report import test_all_data_sources; test_all_data_sources()"
# Fix connectivity issues

# P1: Missed scheduled report
python src/generate_report.py --template templates/weekly.html --output reports/weekly.html --email team@company.com

# P1: PDF rendering failed
pip install --force-reinstall weasyprint
python src/generate_report.py --template templates/test.html --output /tmp/test.pdf --format pdf
```

---

**Document Metadata:**
- **Version:** 1.0
- **Last Updated:** 2025-11-10
- **Owner:** Platform Engineering Team
- **Review Schedule:** Quarterly or after major incidents
- **Feedback:** Create issue or submit PR with updates
