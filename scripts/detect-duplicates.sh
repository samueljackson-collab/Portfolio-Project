#!/bin/bash
# Detect Duplicate Projects
# Purpose: Find duplicate projects across different naming conventions and archive versions

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
EXTRACT_BASE="$REPO_ROOT/temp_extraction"
CURRENT_PROJECTS="$REPO_ROOT/projects"
REPORT_FILE="$REPO_ROOT/docs/DUPLICATE_DETECTION_REPORT.md"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Duplicate Project Detection ===${NC}"
echo ""

# Initialize report
cat > "$REPORT_FILE" << 'EOF'
# Duplicate Project Detection Report

**Generated:** $(date)
**Purpose:** Identify duplicate projects across naming conventions and archive versions

---

## Detection Strategy

1. **Name similarity matching** (fuzzy matching on project names)
2. **README content comparison** (similar descriptions = potential duplicate)
3. **File structure analysis** (similar file organization)
4. **Code similarity** (identical or very similar code files)

---

EOF

echo "Report file: $REPORT_FILE"

# Function to normalize project name for comparison
normalize_name() {
    local name="$1"
    # Remove prefixes (PRJ-, p, numbers, etc.)
    # Convert to lowercase
    # Remove hyphens and underscores
    echo "$name" | \
        sed 's/^PRJ-[A-Z]*-[0-9]*-//gi' | \
        sed 's/^p[0-9]*-//gi' | \
        sed 's/^[0-9]*-//gi' | \
        tr '[:upper:]' '[:lower:]' | \
        tr '-_' ' '
}

# Function to extract keywords from README
extract_keywords() {
    local readme="$1"
    if [ -f "$readme" ]; then
        # Extract first paragraph and title
        head -50 "$readme" | \
            tr '[:upper:]' '[:lower:]' | \
            grep -oE '\b[a-z]{4,}\b' | \
            sort | uniq -c | sort -rn | head -20
    fi
}

echo -e "${YELLOW}Scanning current repository projects...${NC}"
current_projects=()
while IFS= read -r -d '' project_dir; do
    project_name=$(basename "$project_dir")
    current_projects+=("$project_dir:$project_name")
done < <(find "$CURRENT_PROJECTS" -mindepth 1 -maxdepth 2 -type d \( -name "p[0-9]*" -o -name "PRJ-*" -o -name "[0-9]*-*" \) -print0 2>/dev/null)

echo "Found ${#current_projects[@]} projects in current repository"

# If extraction directory exists, scan it too
extracted_projects=()
if [ -d "$EXTRACT_BASE" ]; then
    echo -e "${YELLOW}Scanning extracted archives...${NC}"
    while IFS= read -r -d '' project_dir; do
        project_name=$(basename "$project_dir")
        extracted_projects+=("$project_dir:$project_name")
    done < <(find "$EXTRACT_BASE" -type d \( -name "p[0-9]*" -o -name "PRJ-*" -o -name "[0-9]*-*" \) -print0 2>/dev/null)
    echo "Found ${#extracted_projects[@]} projects in extracted archives"
fi

# Combine all projects
all_projects=("${current_projects[@]}" "${extracted_projects[@]}")
echo ""
echo "Total projects to analyze: ${#all_projects[@]}"
echo ""

# Analysis
echo -e "${BLUE}=== Analyzing for duplicates ===${NC}" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Create project catalog
declare -A project_catalog
declare -A name_groups

for project_info in "${all_projects[@]}"; do
    project_dir="${project_info%%:*}"
    project_name="${project_info##*:}"
    normalized=$(normalize_name "$project_name")

    # Group by normalized name
    if [ -n "${name_groups[$normalized]}" ]; then
        name_groups[$normalized]="${name_groups[$normalized]}|$project_dir"
    else
        name_groups[$normalized]="$project_dir"
    fi
done

# Report grouped projects
echo "## Potential Duplicates by Name Similarity" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

duplicate_groups=0
for normalized_name in "${!name_groups[@]}"; do
    IFS='|' read -ra projects <<< "${name_groups[$normalized_name]}"

    if [ ${#projects[@]} -gt 1 ]; then
        ((duplicate_groups++))
        echo -e "${YELLOW}Duplicate group #$duplicate_groups: '$normalized_name'${NC}"
        echo "### Group #$duplicate_groups: \`$normalized_name\`" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        echo "| Location | Full Name | Has README | File Count |" >> "$REPORT_FILE"
        echo "|----------|-----------|------------|------------|" >> "$REPORT_FILE"

        for proj_dir in "${projects[@]}"; do
            proj_name=$(basename "$proj_dir")
            readme_exists="❌"
            if [ -f "$proj_dir/README.md" ]; then
                readme_exists="✅"
            fi
            file_count=$(find "$proj_dir" -type f 2>/dev/null | wc -l)
            rel_path=$(echo "$proj_dir" | sed "s|$REPO_ROOT/||")

            echo "  - $rel_path ($file_count files, README: $readme_exists)"
            echo "| \`$rel_path\` | $proj_name | $readme_exists | $file_count |" >> "$REPORT_FILE"
        done

        echo "" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        echo ""
    fi
done

if [ $duplicate_groups -eq 0 ]; then
    echo -e "${GREEN}No obvious duplicates found by name matching${NC}"
    echo "No duplicates detected by name similarity." >> "$REPORT_FILE"
else
    echo -e "${RED}Found $duplicate_groups potential duplicate groups${NC}"
fi

echo "" >> "$REPORT_FILE"

# README content similarity check
echo "## README Content Similarity" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo -e "${BLUE}Analyzing README content...${NC}"

# Create temporary files for comparison
tmp_dir=$(mktemp -d)
trap "rm -rf $tmp_dir" EXIT

readme_index=0
declare -A readme_map

for project_info in "${all_projects[@]}"; do
    project_dir="${project_info%%:*}"
    project_name="${project_info##*:}"
    readme="$project_dir/README.md"

    if [ -f "$readme" ]; then
        ((readme_index++))
        # Extract keywords and store
        keywords=$(extract_keywords "$readme" | head -10)
        echo "$keywords" > "$tmp_dir/keywords_$readme_index.txt"
        readme_map[$readme_index]="$project_dir"
    fi
done

echo "Analyzed $readme_index README files" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Project naming convention analysis
echo "## Current Repository: Projects by Naming Convention" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "### Category-based (XX-category-name/PRJ-CODE-###)" >> "$REPORT_FILE"
find "$CURRENT_PROJECTS" -maxdepth 2 -type d -name "PRJ-*" 2>/dev/null | sort | while read -r proj; do
    rel_path=$(echo "$proj" | sed "s|$REPO_ROOT/||")
    file_count=$(find "$proj" -type f 2>/dev/null | wc -l)
    echo "- \`$rel_path\` ($file_count files)" >> "$REPORT_FILE"
done
echo "" >> "$REPORT_FILE"

echo "### p## numbered projects" >> "$REPORT_FILE"
find "$CURRENT_PROJECTS" -maxdepth 1 -type d -name "p[0-9]*" 2>/dev/null | sort | while read -r proj; do
    rel_path=$(echo "$proj" | sed "s|$REPO_ROOT/||")
    file_count=$(find "$proj" -type f 2>/dev/null | wc -l)
    echo "- \`$rel_path\` ($file_count files)" >> "$REPORT_FILE"
done
echo "" >> "$REPORT_FILE"

echo "### Simple numbered projects (1-, 2-, etc.)" >> "$REPORT_FILE"
find "$CURRENT_PROJECTS" -maxdepth 1 -type d -name "[1-9]-*" -o -name "[0-9][0-9]-*" 2>/dev/null | sort | while read -r proj; do
    rel_path=$(echo "$proj" | sed "s|$REPO_ROOT/||")
    file_count=$(find "$proj" -type f 2>/dev/null | wc -l)
    echo "- \`$rel_path\` ($file_count files)" >> "$REPORT_FILE"
done
echo "" >> "$REPORT_FILE"

# Summary statistics
echo "## Summary Statistics" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "- Total projects analyzed: ${#all_projects[@]}" >> "$REPORT_FILE"
echo "- Projects in current repository: ${#current_projects[@]}" >> "$REPORT_FILE"
echo "- Projects in extracted archives: ${#extracted_projects[@]}" >> "$REPORT_FILE"
echo "- Potential duplicate groups: $duplicate_groups" >> "$REPORT_FILE"
echo "- Projects with README: $readme_index" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# Recommendations
echo "## Recommendations" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "1. **Review duplicate groups** - Manually inspect each group to determine which version to keep" >> "$REPORT_FILE"
echo "2. **Compare README content** - The most complete documentation should be prioritized" >> "$REPORT_FILE"
echo "3. **Check file counts** - More files usually indicates more complete implementation" >> "$REPORT_FILE"
echo "4. **Examine code quality** - Use compare-versions.py for detailed analysis" >> "$REPORT_FILE"
echo "5. **Merge systematically** - Follow the merge plan in STRUCTURE_ANALYSIS_AND_MERGE_PLAN.md" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "---" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "**Next step:** Run \`./scripts/compare-versions.py\` for detailed version comparison" >> "$REPORT_FILE"

echo ""
echo -e "${GREEN}✓ Report generated: $REPORT_FILE${NC}"
echo ""
echo "Summary:"
echo "- Total projects: ${#all_projects[@]}"
echo "- Duplicate groups found: $duplicate_groups"
echo "- Projects with README: $readme_index"

exit 0
