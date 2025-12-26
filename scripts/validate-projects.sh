
#!/bin/bash
set -euo pipefail

# Project Validation Script
# Validates the P01–P20 canonical projects under `projects/`.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECTS_DIR="${SCRIPT_DIR}/../projects"

GREEN='[0;32m'
RED='[0;31m'
YELLOW='[1;33m'
BLUE='[0;34m'
NC='[0m'

required_files=("README.md" "CHANGELOG.md" "Makefile" ".env.example")
optional_files=("RUNBOOK.md" "PLAYBOOK.md" "HANDBOOK.md")

total_checks=0
passed_checks=0
failed_checks=0
warning_checks=0
project_count=0

check_required_file() {
    local path="$1"
    local label="$2"
    total_checks=$((total_checks + 1))
    if [[ -f "$path" ]]; then
        echo -e "  ${GREEN}✓${NC} ${label}"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "  ${RED}✗${NC} ${label} (missing: ${path})"
        failed_checks=$((failed_checks + 1))
    fi
}

check_optional_file() {
    local path="$1"
    local label="$2"
    total_checks=$((total_checks + 1))
    if [[ -f "$path" ]]; then
        echo -e "  ${GREEN}✓${NC} ${label}"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "  ${YELLOW}⚠${NC} ${label} (optional)"
        warning_checks=$((warning_checks + 1))
    fi
}

check_dir() {
    local path="$1"
    local label="$2"
    total_checks=$((total_checks + 1))
    if [[ -d "$path" ]]; then
        echo -e "  ${GREEN}✓${NC} ${label}"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "  ${YELLOW}⚠${NC} ${label}"
        warning_checks=$((warning_checks + 1))
    fi
}

validate_project() {
    local project_dir="$1"
    local project_name=$(basename "$project_dir")
    echo -e "
${BLUE}Validating ${project_name}${NC}"

    for file in "${required_files[@]}"; do
        check_required_file "${project_dir}/${file}" "${file} present"
    done

    for file in "${optional_files[@]}"; do
        check_optional_file "${project_dir}/${file}" "${file} present"
    done

    if [[ -f "${project_dir}/requirements.txt" ]]; then
        check_required_file "${project_dir}/requirements-dev.txt" "requirements-dev.txt present"
    fi

    if [[ -d "${project_dir}/src" ]]; then
        check_dir "${project_dir}/tests" "tests/ directory"
        check_dir "${project_dir}/tests/integration" "tests/integration directory"
        check_dir "${project_dir}/tests/e2e" "tests/e2e directory"
    fi
}

if [[ ! -d "${PROJECTS_DIR}" ]]; then
    echo -e "${RED}Projects directory not found: ${PROJECTS_DIR}${NC}"
    exit 1
fi

mapfile -t project_dirs < <(find "${PROJECTS_DIR}" -maxdepth 1 -type d -name 'p[0-9][0-9]-*' | sort)

if [[ ${#project_dirs[@]} -eq 0 ]]; then
    echo -e "${RED}No P-series projects found under ${PROJECTS_DIR}${NC}"
    exit 1
fi

for dir in "${project_dirs[@]}"; do
    validate_project "$dir"
    project_count=$((project_count + 1))
    echo -e "  Path: ${dir}"
    echo -e "  Summary: $(head -n 1 "$dir/README.md" 2>/dev/null || echo 'README missing')"
    echo -e "${BLUE}-----------------------------${NC}"

done

echo -e "
${BLUE}=== Validation Summary ===${NC}"
echo -e "Projects validated: ${project_count}"
echo -e "Total checks: ${total_checks}"
echo -e "${GREEN}Passed: ${passed_checks}${NC}"
echo -e "${RED}Failed: ${failed_checks}${NC}"
echo -e "${YELLOW}Warnings: ${warning_checks}${NC}"

if [[ ${failed_checks} -gt 0 ]]; then
    exit 1
fi
exit 0
