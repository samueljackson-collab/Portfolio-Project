#!/bin/bash
# Portfolio Demo Scripts - Quick Start Guide
# ==========================================
#
# Comprehensive demo scripts to showcase all portfolio projects
#
# Usage:
#   ./demo-scripts.sh [command]
#
# Commands:
#   setup       - Install all dependencies
#   reportify   - Launch Reportify Pro GUI
#   generate    - Generate sample reports
#   test        - Run all tests
#   demo        - Interactive demo menu
#   clean       - Clean up demo artifacts
#   help        - Show this help message

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_error "$1 is not installed"
        return 1
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# SETUP - Install Dependencies
# ═══════════════════════════════════════════════════════════════════════════

setup_environment() {
    print_header "Portfolio Demo Setup"

    print_info "Checking system dependencies..."

    # Check Python
    if check_command python3; then
        python3 --version
    else
        print_error "Python 3 is required. Install from: https://www.python.org/"
        exit 1
    fi

    # Check pip
    if ! check_command pip3; then
        print_error "pip3 is required. Installing..."
        python3 -m ensurepip --upgrade
    fi

    print_info "Installing Python dependencies..."

    # Create virtual environment
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install dependencies
    pip install --upgrade pip
    pip install python-docx pydantic pillow jinja2 weasyprint

    print_success "All dependencies installed!"

    # Create demo directories
    print_info "Creating demo directories..."
    mkdir -p demo-output
    mkdir -p reports
    mkdir -p sample-data

    print_success "Setup complete!"
    echo ""
    echo "Next steps:"
    echo "  ./demo-scripts.sh reportify   - Launch Reportify Pro GUI"
    echo "  ./demo-scripts.sh generate    - Generate sample reports"
    echo "  ./demo-scripts.sh demo        - Interactive demo menu"
}

# ═══════════════════════════════════════════════════════════════════════════
# REPORTIFY PRO - Report Generator
# ═══════════════════════════════════════════════════════════════════════════

launch_reportify() {
    print_header "Launching Reportify Pro"

    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found. Run: ./demo-scripts.sh setup"
        exit 1
    fi

    source venv/bin/activate

    print_info "Starting Reportify Pro Report Generator..."

    # Check if the report generator exists
    if [ -f "projects/24-report-generator/src/generate_report.py" ]; then
        print_info "Using Project 24 Report Generator"
        cd projects/24-report-generator
        python3 src/generate_report.py --help 2>/dev/null || print_info "Report generator ready"
        cd ../..
    else
        print_error "Report generator not found!"
        print_info "Demonstrating report generation capabilities instead..."
        generate_sample_reports
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# GENERATE SAMPLE REPORTS
# ═══════════════════════════════════════════════════════════════════════════

generate_sample_reports() {
    print_header "Generating Sample Reports"

    source venv/bin/activate 2>/dev/null || true

    # Create sample data directory if it doesn't exist
    mkdir -p sample-data
    mkdir -p reports

    # Sample 1: Vulnerability Assessment
    print_info "Creating Vulnerability Assessment Report..."
    cat > sample-data/vuln-assessment.json << 'EOF'
{
  "template_key": "vulnerability_assessment",
  "category": "Security",
  "title": "Q4 2024 Vulnerability Assessment - Production Infrastructure",
  "subtitle": "Comprehensive Security Assessment and Remediation Plan",
  "author": "Senior Security Engineer - Demo User",
  "company_name": "TechCorp Industries",
  "executive_summary": "This vulnerability assessment examined 47 production systems across our cloud infrastructure, identifying 156 total vulnerabilities. Critical findings include 8 high-severity vulnerabilities requiring immediate remediation. The overall security posture has improved 23% since the last quarterly assessment.",
  "objectives": [
    "Identify and classify security vulnerabilities using CVSS v3.1 scoring",
    "Assess risk levels and potential business impact",
    "Ensure compliance with SOC 2, PCI DSS, and ISO 27001",
    "Provide prioritized remediation roadmap with timeline"
  ],
  "findings": [
    "CRITICAL: 3 instances of Apache Log4j vulnerability (CVE-2021-44228) - CVSS 10.0",
    "HIGH: 5 publicly accessible database endpoints without authentication",
    "HIGH: 12 systems running end-of-life operating systems",
    "MEDIUM: 34 servers with outdated SSL/TLS configurations"
  ],
  "recommendations": [
    "IMMEDIATE (0-7 days): Patch all Apache Log4j vulnerabilities - 16 hours effort",
    "HIGH PRIORITY (7-14 days): Upgrade end-of-life operating systems - 80 hours",
    "MEDIUM PRIORITY (14-30 days): Implement security headers across web applications",
    "ONGOING: Establish vulnerability management program with monthly reporting"
  ],
  "tags": ["security", "vulnerability", "critical", "compliance"]
}
EOF

    # Sample 2: Cloud Migration Assessment
    print_info "Creating Cloud Migration Assessment Report..."
    cat > sample-data/cloud-migration.json << 'EOF'
{
  "template_key": "cloud_migration",
  "category": "Cloud",
  "title": "Enterprise E-Commerce Platform - AWS Cloud Migration Assessment",
  "subtitle": "Strategic Cloud Migration Roadmap and Implementation Plan",
  "author": "Cloud Solutions Architect - Demo User",
  "company_name": "RetailMax Corporation",
  "executive_summary": "This assessment evaluates migration of our legacy e-commerce platform to AWS cloud infrastructure. Financial analysis projects 42% reduction in infrastructure costs ($2.1M annually) while improving system reliability from 99.5% to 99.95% uptime.",
  "objectives": [
    "Assess current infrastructure cloud-readiness and identify migration blockers",
    "Design target AWS architecture optimized for cost and performance",
    "Develop phased migration strategy with minimal business disruption",
    "Project 3-year TCO comparison between on-premises and AWS"
  ],
  "findings": [
    "Current environment: 85 VMs, 12 database servers, 200TB storage - $2.1M annual cost",
    "Cloud readiness: 72% of applications cloud-ready with minimal modifications",
    "Projected AWS cost: $780K annually (63% reduction in year 1)",
    "Data migration challenge: 3-week sync window for 45TB Oracle database"
  ],
  "recommendations": [
    "PHASE 1 (Months 1-2): Establish AWS Organization and landing zone - $45K",
    "PHASE 2 (Months 2-3): Pilot migration of 12 non-critical applications",
    "PHASE 3 (Months 3-4): Application tier migration to ECS/EKS",
    "PHASE 4 (Month 4): Database migration using AWS DMS with minimal downtime"
  ],
  "tags": ["cloud-migration", "aws", "transformation", "cost-optimization"]
}
EOF

    # Sample 3: Incident Response Report
    print_info "Creating Incident Response Report..."
    cat > sample-data/incident-response.json << 'EOF'
{
  "template_key": "incident_response",
  "category": "Security",
  "title": "Security Incident Report - IR-2024-1015",
  "subtitle": "Unauthorized Access Attempt - Production API Gateway",
  "author": "Security Operations Center - Demo User",
  "company_name": "TechCorp Industries",
  "executive_summary": "On October 15, 2024, our monitoring systems detected suspicious API activity indicating a credential stuffing attack against our production API gateway. The incident was contained within 8 minutes with no data exposure. Root cause: Lack of rate limiting on authentication endpoints.",
  "metadata": {
    "incident_id": "IR-2024-1015",
    "severity": "Severity 2",
    "detection_time": "2024-10-15 03:42 UTC",
    "containment_time": "2024-10-15 03:50 UTC",
    "affected_systems": "API Gateway, Authentication Service"
  },
  "findings": [
    "15,000 failed authentication attempts from 200 IP addresses in 5 minutes",
    "Attack pattern consistent with credential stuffing using leaked password databases",
    "No successful account compromises detected",
    "WAF rules not optimized for authentication endpoints"
  ],
  "recommendations": [
    "IMMEDIATE: Implement rate limiting on /auth endpoints (10 requests/minute per IP)",
    "HIGH: Enable AWS WAF Bot Control for automated bot detection",
    "MEDIUM: Implement adaptive authentication with risk scoring",
    "ONGOING: Monthly security training on incident response procedures"
  ],
  "tags": ["incident", "security", "credential-stuffing", "api-gateway"]
}
EOF

    # Sample 4: AWS Infrastructure Report
    print_info "Creating AWS Infrastructure Report..."
    cat > sample-data/aws-infrastructure.json << 'EOF'
{
  "template_key": "infrastructure",
  "category": "Cloud",
  "title": "AWS Multi-Tier Infrastructure - Architecture Report",
  "subtitle": "Production-Grade Terraform-Managed Infrastructure",
  "author": "DevOps Engineer - Demo User",
  "company_name": "TechCorp Industries",
  "executive_summary": "Deployed highly available, multi-tier AWS infrastructure using Terraform IaC. The architecture supports 100K+ daily active users with 99.95% uptime. Achieved 40% cost reduction through auto-scaling and reserved instances.",
  "objectives": [
    "Design scalable, highly available AWS architecture",
    "Implement Infrastructure as Code using Terraform",
    "Establish CI/CD pipeline for infrastructure deployment",
    "Optimize costs while maintaining performance and reliability"
  ],
  "findings": [
    "Architecture: Multi-AZ VPC with public/private subnets across 3 availability zones",
    "Compute: Auto-scaling EC2 instances (t3.medium) with Application Load Balancer",
    "Database: RDS PostgreSQL Multi-AZ with read replicas for high availability",
    "Cost Savings: 40% reduction through reserved instances and auto-scaling policies"
  ],
  "recommendations": [
    "Implement CloudWatch detailed monitoring for all critical resources",
    "Set up AWS Backup for automated RDS and EBS snapshots",
    "Enable AWS Config for compliance and governance tracking",
    "Implement AWS WAF for enhanced security on ALB"
  ],
  "tags": ["aws", "terraform", "infrastructure", "devops"]
}
EOF

    print_success "Sample data files created!"

    # Generate simple text reports since we may not have the full report generator
    print_info "Generating text-based reports..."

    for json_file in sample-data/*.json; do
        base_name=$(basename "$json_file" .json)
        output_file="reports/${base_name}-report.txt"

        print_info "Generating: $output_file"

        cat > "$output_file" << EOF
═══════════════════════════════════════════════════════════
  PORTFOLIO PROJECT REPORT
═══════════════════════════════════════════════════════════

Generated from: $json_file
Date: $(date)

Report Content:
$(cat "$json_file" | python3 -m json.tool 2>/dev/null || cat "$json_file")

═══════════════════════════════════════════════════════════
End of Report
═══════════════════════════════════════════════════════════
EOF
        print_success "Generated: $output_file"
    done

    print_success "Sample reports generated in ./reports/ directory!"

    # List generated files
    echo ""
    print_info "Generated Reports:"
    ls -lh reports/
}

# ═══════════════════════════════════════════════════════════════════════════
# RUN TESTS
# ═══════════════════════════════════════════════════════════════════════════

run_tests() {
    print_header "Running Portfolio Tests"

    source venv/bin/activate 2>/dev/null || {
        print_error "Virtual environment not found. Run: ./demo-scripts.sh setup"
        exit 1
    }

    print_info "Installing test dependencies..."
    pip install pytest==7.4.3 pytest-cov==4.1.0 2>/dev/null || print_info "Pytest already installed"

    # Create simple test file
    print_info "Creating test suite..."
    cat > test_portfolio.py << 'EOF'
import pytest
from pathlib import Path
import json

def test_sample_data_exists():
    """Verify sample data files exist"""
    assert Path("sample-data").exists(), "sample-data directory not found"
    json_files = list(Path("sample-data").glob("*.json"))
    assert len(json_files) > 0, "No sample JSON files found"

def test_json_validity():
    """Verify JSON files are valid"""
    json_files = Path("sample-data").glob("*.json")
    for json_file in json_files:
        with open(json_file) as f:
            data = json.load(f)
            assert isinstance(data, dict), f"{json_file} is not a valid JSON object"

def test_reports_directory():
    """Verify reports directory exists"""
    reports_dir = Path("reports")
    assert reports_dir.exists(), "reports directory not found"

def test_project_structure():
    """Verify key project directories exist"""
    assert Path("projects").exists(), "projects directory not found"
    assert Path("scripts").exists(), "scripts directory not found"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
EOF

    print_info "Running tests..."
    python3 -m pytest test_portfolio.py -v || {
        print_error "Some tests failed, but continuing..."
    }

    print_success "Test execution complete!"
}

# ═══════════════════════════════════════════════════════════════════════════
# CLEANUP
# ═══════════════════════════════════════════════════════════════════════════

cleanup() {
    print_header "Cleaning Up Demo Artifacts"

    print_info "Removing generated files..."
    rm -rf demo-output/
    rm -f reports/*.txt
    rm -f sample-data/*.json
    rm -f test_portfolio.py
    rm -rf __pycache__/
    rm -rf .pytest_cache/

    print_success "Cleanup complete!"
}

# ═══════════════════════════════════════════════════════════════════════════
# INTERACTIVE DEMO
# ═══════════════════════════════════════════════════════════════════════════

interactive_demo() {
    print_header "Portfolio Interactive Demo"

    echo "Welcome to the Portfolio Projects Demo!"
    echo ""
    echo "Available Projects:"
    echo "  1) Report Generator - Professional Report Generation"
    echo "  2) AWS Infrastructure Automation (Terraform)"
    echo "  3) IAM Security Hardening"
    echo "  4) Kubernetes on EKS"
    echo "  5) Serverless API Platform"
    echo "  6) AI/ML Tab Organization App"
    echo "  7) Multi-Region Disaster Recovery"
    echo "  8) DevSecOps Pipeline"
    echo ""
    echo "  0) Exit"
    echo ""

    read -p "Select a project to demo (0-8): " choice

    case $choice in
        1)
            print_header "Report Generator Demo"
            echo "Professional report generator for portfolio projects."
            echo ""
            echo "Features:"
            echo "  • Multiple professional templates"
            echo "  • JSON-based data input"
            echo "  • Multi-format export (HTML, PDF)"
            echo "  • Automated report generation"
            echo ""
            read -p "Generate sample reports? (y/n): " launch
            if [ "$launch" = "y" ]; then
                generate_sample_reports
            fi
            ;;
        2)
            print_header "AWS Infrastructure Automation"
            echo "Production-grade AWS infrastructure using Terraform."
            echo ""
            echo "Achievements:"
            echo "  • 70% faster provisioning (days → hours)"
            echo "  • 40% cost reduction through optimization"
            echo "  • 99.95% infrastructure reliability"
            echo ""
            echo "Architecture:"
            echo "  • Multi-tier VPC with auto-scaling"
            echo "  • RDS Multi-AZ, ElastiCache, DynamoDB"
            echo "  • Complete CI/CD with GitHub Actions"
            echo ""
            echo "Location: projects/1-aws-infrastructure-automation/"
            ;;
        3)
            print_header "IAM Security Hardening"
            echo "Zero-trust IAM security implementation."
            echo ""
            echo "Results:"
            echo "  • 85% reduction in over-privileged accounts"
            echo "  • 100% MFA adoption across organization"
            echo "  • Zero IAM-related security incidents"
            echo ""
            echo "Features:"
            echo "  • Just-in-time access provisioning"
            echo "  • Real-time anomaly detection"
            echo "  • Automated compliance monitoring"
            echo ""
            echo "Location: projects/p02-iam-hardening/"
            ;;
        4)
            print_header "Kubernetes on EKS"
            echo "Production EKS cluster with advanced features."
            echo ""
            echo "Metrics:"
            echo "  • 99.99% uptime (four nines)"
            echo "  • 60% cost reduction with spot instances"
            echo "  • 75% faster deployments with GitOps"
            echo ""
            echo "Stack:"
            echo "  • EKS 1.28 with managed node groups"
            echo "  • GitOps deployment with ArgoCD"
            echo "  • Prometheus + Grafana monitoring"
            echo ""
            echo "Location: projects/3-kubernetes-cicd/"
            ;;
        5)
            print_header "Serverless API Platform"
            echo "Event-driven serverless architecture."
            echo ""
            echo "Impact:"
            echo "  • 75% cost reduction ($180K → $45K/year)"
            echo "  • Infinite scalability (0-100K RPS)"
            echo "  • 10x faster deployments"
            echo ""
            echo "Technologies:"
            echo "  • AWS Lambda, API Gateway, DynamoDB"
            echo "  • EventBridge, SQS, Cognito"
            echo "  • AWS SAM for IaC"
            echo ""
            echo "Location: projects/p11-serverless/"
            ;;
        6)
            print_header "AI/ML Tab Organization App"
            echo "Cross-platform AI-powered tab management."
            echo ""
            echo "Features:"
            echo "  • AI-powered tab categorization"
            echo "  • Cross-platform support (Android, Windows, macOS)"
            echo "  • Multi-browser compatibility"
            echo "  • Real-time cloud sync"
            echo ""
            echo "Tech Stack:"
            echo "  • Flutter for cross-platform UI"
            echo "  • TensorFlow Lite for ML"
            echo "  • Firebase for sync"
            echo ""
            echo "Location: projects/07-aiml-automation/PRJ-AIML-002/"
            ;;
        7)
            print_header "Multi-Region Disaster Recovery"
            echo "Global DR architecture with automated failover."
            echo ""
            echo "Capabilities:"
            echo "  • Multi-region active-passive setup"
            echo "  • RTO < 15 minutes, RPO < 5 minutes"
            echo "  • Automated health checks and failover"
            echo ""
            echo "Location: projects/9-multi-region-disaster-recovery/"
            ;;
        8)
            print_header "DevSecOps Pipeline"
            echo "Secure CI/CD with integrated security scanning."
            echo ""
            echo "Security Features:"
            echo "  • SAST, DAST, SCA scanning"
            echo "  • Container image scanning"
            echo "  • Automated vulnerability remediation"
            echo ""
            echo "Location: projects/4-devsecops/"
            ;;
        0)
            print_info "Exiting demo. Thanks for visiting!"
            exit 0
            ;;
        *)
            print_error "Invalid choice. Please select 0-8."
            interactive_demo
            ;;
    esac

    echo ""
    read -p "Press Enter to return to menu..."
    interactive_demo
}

# ═══════════════════════════════════════════════════════════════════════════
# HELP
# ═══════════════════════════════════════════════════════════════════════════

show_help() {
    cat << EOF
Portfolio Demo Scripts - Quick Start Guide
==========================================

Usage:
    ./demo-scripts.sh [command]

Commands:
    setup       Install all dependencies and prepare environment
    reportify   Launch Report Generator
    generate    Generate sample reports (Vuln Assessment, Cloud Migration, etc.)
    test        Run test suite to verify setup
    demo        Interactive demo menu for all projects
    clean       Remove generated files and artifacts
    help        Show this help message

Examples:
    # First time setup
    ./demo-scripts.sh setup

    # Generate sample reports
    ./demo-scripts.sh generate

    # Run interactive demo
    ./demo-scripts.sh demo

    # Run tests
    ./demo-scripts.sh test

Project Portfolio Highlights:
    1. Report Generator - Professional report generation system
    2. AWS Infrastructure - Terraform-managed cloud infrastructure
    3. IAM Security - Zero-trust security hardening
    4. Kubernetes EKS - Production-grade container orchestration
    5. Serverless API - Event-driven serverless architecture
    6. AI/ML App - Cross-platform tab organization
    7. Disaster Recovery - Multi-region DR solution
    8. DevSecOps - Secure CI/CD pipeline

For more information:
    • GitHub: https://github.com/samueljackson-collab
    • LinkedIn: https://www.linkedin.com/in/sams-jackson

EOF
}

# ═══════════════════════════════════════════════════════════════════════════
# MAIN COMMAND ROUTER
# ═══════════════════════════════════════════════════════════════════════════

main() {
    case "${1:-help}" in
        setup)
            setup_environment
            ;;
        reportify)
            launch_reportify
            ;;
        generate)
            generate_sample_reports
            ;;
        test)
            run_tests
            ;;
        demo)
            interactive_demo
            ;;
        clean)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown command: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
