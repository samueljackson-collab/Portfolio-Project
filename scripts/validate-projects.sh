#!/bin/bash
set -euo pipefail

# Project Validation Script
# Validates all 20 projects for completeness and standards compliance

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CANONICAL_PROJECTS_DIR="${SCRIPT_DIR}/../projects-new"
PROJECTS_DIR="${CANONICAL_PROJECTS_DIR}"

# Color output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
total_checks=0
passed_checks=0
failed_checks=0

# Function to check if file exists
check_file() {
    local file="$1"
    local description="$2"

    total_checks=$((total_checks + 1))

    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $description"
        passed_checks=$((passed_checks + 1))
        return 0
    else
        echo -e "  ${RED}✗${NC} $description (missing: $file)"
        failed_checks=$((failed_checks + 1))
        return 1
    fi
}

# Function to check if directory exists
check_dir() {
    local dir="$1"
    local description="$2"

    total_checks=$((total_checks + 1))

    if [ -d "$dir" ]; then
        echo -e "  ${GREEN}✓${NC} $description"
        passed_checks=$((passed_checks + 1))
        return 0
    else
        echo -e "  ${RED}✗${NC} $description (missing: $dir)"
        failed_checks=$((failed_checks + 1))
        return 1
    fi
}

# Function to validate a single project
validate_project() {
    local project_dir="$1"
    local project_name=$(basename "$project_dir")

    echo -e "\n${BLUE}Validating ${project_name}${NC}"

    # Check documentation files
    check_file "${project_dir}/README.md" "README.md exists"
    check_file "${project_dir}/docs/HANDBOOK.md" "HANDBOOK.md exists"
    check_file "${project_dir}/docs/RUNBOOK.md" "RUNBOOK.md exists"
    check_file "${project_dir}/docs/PLAYBOOK.md" "PLAYBOOK.md exists"
    check_file "${project_dir}/docs/ARCHITECTURE.md" "ARCHITECTURE.md exists"

    # Check configuration files
    check_file "${project_dir}/Makefile" "Makefile exists"
    check_file "${project_dir}/.env.example" ".env.example exists"
    check_file "${project_dir}/.gitignore" ".gitignore exists"
    check_file "${project_dir}/Dockerfile" "Dockerfile exists"

    # Check Python files
    check_file "${project_dir}/requirements.txt" "requirements.txt exists"
    check_file "${project_dir}/requirements-dev.txt" "requirements-dev.txt exists"

    # Check directory structure
    check_dir "${project_dir}/src" "src/ directory exists"
    check_dir "${project_dir}/tests" "tests/ directory exists"
    check_dir "${project_dir}/tests/unit" "tests/unit/ directory exists"
    check_dir "${project_dir}/scripts" "scripts/ directory exists"
    check_dir "${project_dir}/infrastructure" "infrastructure/ directory exists"
    check_dir "${project_dir}/infrastructure/terraform" "infrastructure/terraform/ directory exists"
    check_dir "${project_dir}/ci" "ci/ directory exists"

    # Check source files
    check_file "${project_dir}/src/main.py" "src/main.py exists"
    check_file "${project_dir}/tests/unit/test_main.py" "tests/unit/test_main.py exists"

    # Check IaC files
    check_file "${project_dir}/infrastructure/terraform/main.tf" "Terraform main.tf exists"
    check_file "${project_dir}/infrastructure/terraform/variables.tf" "Terraform variables.tf exists"

    # Check CI/CD
    check_file "${project_dir}/ci/ci-cd.yml" "CI/CD workflow exists"

    # Check README content
    if [ -f "${project_dir}/README.md" ]; then
        total_checks=$((total_checks + 3))

        if grep -q "Quick Start" "${project_dir}/README.md"; then
            echo -e "  ${GREEN}✓${NC} README contains Quick Start section"
            passed_checks=$((passed_checks + 1))
        else
            echo -e "  ${YELLOW}⚠${NC} README missing Quick Start section"
            failed_checks=$((failed_checks + 1))
        fi

        if grep -q "Features" "${project_dir}/README.md"; then
            echo -e "  ${GREEN}✓${NC} README contains Features section"
            passed_checks=$((passed_checks + 1))
        else
            echo -e "  ${YELLOW}⚠${NC} README missing Features section"
            failed_checks=$((failed_checks + 1))
        fi

        if grep -q "Documentation" "${project_dir}/README.md"; then
            echo -e "  ${GREEN}✓${NC} README contains Documentation section"
            passed_checks=$((passed_checks + 1))
        else
            echo -e "  ${YELLOW}⚠${NC} README missing Documentation section"
            failed_checks=$((failed_checks + 1))
        fi
    fi

    # Check HANDBOOK content
    if [ -f "${project_dir}/docs/HANDBOOK.md" ]; then
        total_checks=$((total_checks + 3))

        if grep -q "Code Standards" "${project_dir}/docs/HANDBOOK.md"; then
            echo -e "  ${GREEN}✓${NC} HANDBOOK contains Code Standards"
            passed_checks=$((passed_checks + 1))
        else
            echo -e "  ${YELLOW}⚠${NC} HANDBOOK missing Code Standards"
            failed_checks=$((failed_checks + 1))
        fi

        if grep -q "Testing Requirements" "${project_dir}/docs/HANDBOOK.md"; then
            echo -e "  ${GREEN}✓${NC} HANDBOOK contains Testing Requirements"
            passed_checks=$((passed_checks + 1))
        else
            echo -e "  ${YELLOW}⚠${NC} HANDBOOK missing Testing Requirements"
            failed_checks=$((failed_checks + 1))
        fi

        if grep -q "Security Guidelines" "${project_dir}/docs/HANDBOOK.md"; then
            echo -e "  ${GREEN}✓${NC} HANDBOOK contains Security Guidelines"
            passed_checks=$((passed_checks + 1))
        else
            echo -e "  ${YELLOW}⚠${NC} HANDBOOK missing Security Guidelines"
            failed_checks=$((failed_checks + 1))
        fi
    fi

    # Check RUNBOOK content
    if [ -f "${project_dir}/docs/RUNBOOK.md" ]; then
        total_checks=$((total_checks + 3))

        if grep -q "Deployment Procedures" "${project_dir}/docs/RUNBOOK.md"; then
            echo -e "  ${GREEN}✓${NC} RUNBOOK contains Deployment Procedures"
            passed_checks=$((passed_checks + 1))
        else
            echo -e "  ${YELLOW}⚠${NC} RUNBOOK missing Deployment Procedures"
            failed_checks=$((failed_checks + 1))
        fi

        if grep -q "Troubleshooting" "${project_dir}/docs/RUNBOOK.md"; then
            echo -e "  ${GREEN}✓${NC} RUNBOOK contains Troubleshooting"
            passed_checks=$((passed_checks + 1))
        else
            echo -e "  ${YELLOW}⚠${NC} RUNBOOK missing Troubleshooting"
            failed_checks=$((failed_checks + 1))
        fi

        if grep -q "Incident Response" "${project_dir}/docs/RUNBOOK.md"; then
            echo -e "  ${GREEN}✓${NC} RUNBOOK contains Incident Response"
            passed_checks=$((passed_checks + 1))
        else
            echo -e "  ${YELLOW}⚠${NC} RUNBOOK missing Incident Response"
            failed_checks=$((failed_checks + 1))
        fi
    fi
}

# Main execution
echo -e "${BLUE}=== Project Validation Tool ===${NC}"
echo -e "Validating 20 projects in ${PROJECTS_DIR}"

if [ ! -d "${PROJECTS_DIR}" ]; then
    echo -e "${RED}Error: Projects directory not found: ${PROJECTS_DIR}${NC}"
    exit 1
fi

# Find and validate all projects
project_count=0
for project_dir in "${PROJECTS_DIR}"/P*; do
    if [ -d "$project_dir" ]; then
        validate_project "$project_dir"
        project_count=$((project_count + 1))
    fi
done

# Summary
echo -e "\n${BLUE}=== Validation Summary ===${NC}"
echo -e "Projects validated: ${project_count}"
echo -e "Total checks: ${total_checks}"
echo -e "${GREEN}Passed: ${passed_checks}${NC}"
echo -e "${RED}Failed: ${failed_checks}${NC}"

# Calculate pass rate
if [ $total_checks -gt 0 ]; then
    pass_rate=$((100 * passed_checks / total_checks))
    echo -e "Pass rate: ${pass_rate}%"

    if [ $pass_rate -ge 95 ]; then
        echo -e "\n${GREEN}✓ All projects meet quality standards!${NC}"
        exit 0
    elif [ $pass_rate -ge 80 ]; then
        echo -e "\n${YELLOW}⚠ Projects mostly compliant, some improvements needed${NC}"
        exit 0
    else
        echo -e "\n${RED}✗ Projects need significant improvements${NC}"
        exit 1
    fi
else
    echo -e "\n${RED}✗ No checks performed${NC}"
    exit 1
fi
