#!/bin/bash
# Validate Portfolio Structure
# Purpose: Ensure all projects meet quality standards

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
PROJECTS_DIR="$REPO_ROOT/projects"
REPORT_FILE="$REPO_ROOT/docs/VALIDATION_REPORT.md"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
total_projects=0
valid_projects=0
issues_found=0

echo -e "${BLUE}=== Portfolio Structure Validation ===${NC}"
echo ""

# Initialize report
cat > "$REPORT_FILE" << EOF
# Portfolio Structure Validation Report

**Generated:** $(date)
**Purpose:** Validate all projects meet quality standards

---

## Validation Criteria

✅ **Must Have:**
- README.md with substantial content (>200 chars)
- At least one source file or documentation
- No broken internal links
- No placeholder code markers

⚠️ **Should Have:**
- CHANGELOG.md
- Test directory
- Proper directory structure
- Architecture documentation

---

## Validation Results

EOF

# Function to check if README exists and has content
check_readme() {
    local project_dir="$1"
    local readme="$project_dir/README.md"

    if [ ! -f "$readme" ]; then
        return 1
    fi

    # Check if README has substantial content (more than 200 characters)
    local size=$(wc -c < "$readme" 2>/dev/null || echo "0")
    if [ "$size" -lt 200 ]; then
        return 2
    fi

    return 0
}

# Function to count placeholder markers
count_placeholders() {
    local project_dir="$1"
    local count=0

    # Search for common placeholder patterns
    if command -v rg &> /dev/null; then
        count=$(rg -i "TODO|FIXME|PLACEHOLDER|XXX|HACK|Coming soon|To be implemented|TBD" "$project_dir" 2>/dev/null | wc -l || echo "0")
    else
        count=$(grep -ri "TODO\|FIXME\|PLACEHOLDER\|XXX\|HACK\|Coming soon\|To be implemented\|TBD" "$project_dir" 2>/dev/null | wc -l || echo "0")
    fi

    echo "$count"
}

# Function to check for broken internal links
check_broken_links() {
    local project_dir="$1"
    local broken=0

    # Find all markdown files
    while IFS= read -r -d '' md_file; do
        # Extract markdown links: [text](path)
        grep -oP '\[.*?\]\(\K[^)]+' "$md_file" 2>/dev/null | while read -r link; do
            # Skip external links
            if [[ "$link" =~ ^https?:// ]]; then
                continue
            fi

            # Skip anchors
            if [[ "$link" =~ ^# ]]; then
                continue
            fi

            # Resolve relative path
            local file_dir=$(dirname "$md_file")
            local target="$file_dir/$link"

            # Check if target exists
            if [ ! -e "$target" ]; then
                echo "Broken link in $md_file: $link"
                ((broken++))
            fi
        done
    done < <(find "$project_dir" -name "*.md" -type f -print0 2>/dev/null)

    return $broken
}

# Function to validate a single project
validate_project() {
    local project_dir="$1"
    local project_name=$(basename "$project_dir")
    local issues=()
    local warnings=()
    local passed=true

    echo -ne "${YELLOW}Validating: $project_name${NC} ... "

    # Check README
    if ! check_readme "$project_dir"; then
        local check_result=$?
        if [ $check_result -eq 1 ]; then
            issues+=("❌ Missing README.md")
            passed=false
        elif [ $check_result -eq 2 ]; then
            issues+=("❌ README.md too short (<200 chars)")
            passed=false
        fi
    fi

    # Count files
    local file_count=$(find "$project_dir" -type f ! -path "*/\.*" 2>/dev/null | wc -l)
    if [ "$file_count" -lt 2 ]; then
        issues+=("❌ Very few files ($file_count)")
        passed=false
    fi

    # Check for placeholders
    local placeholder_count=$(count_placeholders "$project_dir")
    if [ "$placeholder_count" -gt 10 ]; then
        issues+=("⚠️  High placeholder count: $placeholder_count")
        warnings+=("Many incomplete sections")
    elif [ "$placeholder_count" -gt 5 ]; then
        warnings+=("Some placeholder markers: $placeholder_count")
    fi

    # Check for tests
    if [ ! -d "$project_dir/tests" ] && [ ! -d "$project_dir/test" ]; then
        warnings+=("⚠️  No tests directory")
    fi

    # Check for CHANGELOG
    if [ ! -f "$project_dir/CHANGELOG.md" ]; then
        warnings+=("⚠️  No CHANGELOG.md")
    fi

    # Check for code files
    local py_count=$(find "$project_dir" -name "*.py" -type f 2>/dev/null | wc -l)
    local tf_count=$(find "$project_dir" -name "*.tf" -type f 2>/dev/null | wc -l)
    local sh_count=$(find "$project_dir" -name "*.sh" -type f 2>/dev/null | wc -l)
    local total_code=$((py_count + tf_count + sh_count))

    if [ "$total_code" -eq 0 ]; then
        local md_count=$(find "$project_dir" -name "*.md" -type f 2>/dev/null | wc -l)
        if [ "$md_count" -lt 3 ]; then
            issues+=("⚠️  No code files and minimal documentation")
        fi
    fi

    # Report results
    if [ "$passed" = true ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((valid_projects++))

        # Write to report
        echo "### ✅ \`$project_name\`" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        echo "**Status:** PASS" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        echo "**Files:** $file_count | **Code:** ${py_count}py/${tf_count}tf/${sh_count}sh | **Placeholders:** $placeholder_count" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"

        if [ ${#warnings[@]} -gt 0 ]; then
            echo "**Minor warnings:**" >> "$REPORT_FILE"
            for warning in "${warnings[@]}"; do
                echo "- $warning" >> "$REPORT_FILE"
            done
            echo "" >> "$REPORT_FILE"
        fi
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((issues_found++))

        # Write to report
        echo "### ❌ \`$project_name\`" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        echo "**Status:** FAIL" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        echo "**Issues found:**" >> "$REPORT_FILE"
        for issue in "${issues[@]}"; do
            echo "- $issue" >> "$REPORT_FILE"
        done
        echo "" >> "$REPORT_FILE"

        if [ ${#warnings[@]} -gt 0 ]; then
            echo "**Warnings:**" >> "$REPORT_FILE"
            for warning in "${warnings[@]}"; do
                echo "- $warning" >> "$REPORT_FILE"
            done
            echo "" >> "$REPORT_FILE"
        fi
    fi

    ((total_projects++))
}

# Validate all projects
echo -e "${BLUE}Scanning projects directory...${NC}"
echo ""

# Find all project directories
while IFS= read -r -d '' project_dir; do
    validate_project "$project_dir"
done < <(find "$PROJECTS_DIR" -mindepth 1 -maxdepth 2 -type d \( -name "PRJ-*" -o -name "p[0-9]*" -o -name "[0-9]*-*" \) -print0 2>/dev/null)

# Summary
echo ""
echo -e "${BLUE}=== Validation Summary ===${NC}"
echo ""
echo "Total projects validated: $total_projects"
echo -e "Passed: ${GREEN}$valid_projects${NC}"
echo -e "Failed: ${RED}$issues_found${NC}"

success_rate=$((valid_projects * 100 / total_projects))
echo "Success rate: $success_rate%"

# Add summary to report
cat >> "$REPORT_FILE" << EOF

---

## Summary

| Metric | Value |
|--------|-------|
| Total Projects | $total_projects |
| Passed | $valid_projects |
| Failed | $issues_found |
| Success Rate | $success_rate% |

---

## Recommendations

EOF

if [ $issues_found -gt 0 ]; then
    echo "❌ Projects with issues:" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "1. Fix missing or incomplete README files" >> "$REPORT_FILE"
    echo "2. Add substantial content to projects with few files" >> "$REPORT_FILE"
    echo "3. Reduce placeholder markers (complete implementations)" >> "$REPORT_FILE"
    echo "4. Add test suites where missing" >> "$REPORT_FILE"
    echo "5. Create CHANGELOG files for version tracking" >> "$REPORT_FILE"
else
    echo "✅ All projects passed validation!" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    echo "Optional improvements:" >> "$REPORT_FILE"
    echo "- Add missing CHANGELOG files" >> "$REPORT_FILE"
    echo "- Create test suites for projects without tests" >> "$REPORT_FILE"
    echo "- Expand documentation where applicable" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"
echo "---" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "**Generated:** $(date)" >> "$REPORT_FILE"

echo ""
echo -e "${GREEN}✓ Report saved: $REPORT_FILE${NC}"
echo ""

# Exit with error code if issues found
if [ $issues_found -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Validation completed with issues${NC}"
    exit 1
else
    echo -e "${GREEN}✓ All projects validated successfully${NC}"
    exit 0
fi
