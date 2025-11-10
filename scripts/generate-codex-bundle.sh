#!/bin/bash
# Generate ChatGPT Codex Documentation Bundle
# Purpose: Create properly formatted documentation bundle for upload to ChatGPT Codex

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$REPO_ROOT/codex_bundle"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BUNDLE_NAME="portfolio_codex_bundle_$TIMESTAMP"
BUNDLE_DIR="$OUTPUT_DIR/$BUNDLE_NAME"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== ChatGPT Codex Bundle Generator ===${NC}"
echo ""

# Create bundle directory
mkdir -p "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR/projects"
mkdir -p "$BUNDLE_DIR/docs"
mkdir -p "$BUNDLE_DIR/guides"

echo -e "${YELLOW}Creating bundle: $BUNDLE_NAME${NC}"
echo ""

# Function to sanitize markdown for Codex
sanitize_markdown() {
    local input_file="$1"
    local output_file="$2"

    # Copy file and add metadata
    {
        echo "<!-- Source: ${input_file#$REPO_ROOT/} -->"
        echo "<!-- Generated: $(date) -->"
        echo ""
        cat "$input_file"
    } > "$output_file"
}

# Copy main README
echo "📄 Copying main README..."
sanitize_markdown "$REPO_ROOT/README.md" "$BUNDLE_DIR/README.md"

# Create comprehensive index
echo "📑 Generating index..."
cat > "$BUNDLE_DIR/INDEX.md" << 'EOF'
# Portfolio Documentation Index

**Generated:** $(date)
**Purpose:** Master index for ChatGPT Codex

---

## Navigation

### Main Documentation
- [README](./README.md) - Portfolio overview
- [Structure Analysis](./docs/STRUCTURE_ANALYSIS_AND_MERGE_PLAN.md)
- [Projects Overview](./PROJECTS_OVERVIEW.md)

### Project Categories

1. **SDE/DevOps Projects**
   - Located in: `./projects/01-sde-devops/`

2. **Cloud Architecture**
   - Located in: `./projects/02-cloud-architecture/`

3. **Cybersecurity**
   - Located in: `./projects/03-cybersecurity/`

4. **QA/Testing**
   - Located in: `./projects/04-qa-testing/`

5. **Homelab**
   - Located in: `./projects/06-homelab/`

6. **Data Engineering**
   - Located in: `./projects/07-data-engineering/`

7. **AI/ML**
   - Located in: `./projects/08-aiml/`

8. **Advanced Topics**
   - Located in: `./projects/10-advanced-topics/`

### Guides & Documentation
- [Wiki.js Setup Guide](./guides/wiki-js-setup-guide.md)
- [GitHub Repository Setup](./guides/github-repository-setup-guide.md)

---

## File Structure

\`\`\`
portfolio_codex_bundle/
├── INDEX.md (this file)
├── README.md
├── PROJECTS_OVERVIEW.md
├── docs/
│   ├── STRUCTURE_ANALYSIS_AND_MERGE_PLAN.md
│   ├── VALIDATION_REPORT.md
│   └── DUPLICATE_DETECTION_REPORT.md
├── projects/
│   ├── [all project documentation]
│   └── [organized by category]
└── guides/
    └── [setup and usage guides]
\`\`\`

---

## Using This Bundle

This bundle contains all portfolio documentation in markdown format, optimized for:
- ChatGPT Codex knowledge upload
- Code review and analysis
- Project structure understanding
- Documentation generation

**Note:** Code files are referenced but not included to keep bundle size manageable.
For full code, see: https://github.com/samueljackson-collab/Portfolio-Project

---

**Last Updated:** $(date)
EOF

# Generate projects overview
echo "📊 Generating projects overview..."
cat > "$BUNDLE_DIR/PROJECTS_OVERVIEW.md" << 'EOF'
# Portfolio Projects Overview

**Generated:** $(date)

---

## Project Categories

EOF

# Function to process project directory
process_project_category() {
    local category_dir="$1"
    local category_name="$2"
    local output_cat_dir="$BUNDLE_DIR/projects/$(basename "$category_dir")"

    if [ ! -d "$category_dir" ]; then
        return
    fi

    echo "  📁 Processing: $category_name"

    mkdir -p "$output_cat_dir"

    # Find all project subdirectories
    find "$category_dir" -mindepth 1 -maxdepth 2 -type d \( -name "PRJ-*" -o -name "p[0-9]*" -o -name "[0-9]*-*" \) 2>/dev/null | while read -r proj_dir; do
        local proj_name=$(basename "$proj_dir")
        local output_proj_dir="$output_cat_dir/$proj_name"

        mkdir -p "$output_proj_dir"

        # Copy README
        if [ -f "$proj_dir/README.md" ]; then
            sanitize_markdown "$proj_dir/README.md" "$output_proj_dir/README.md"
        fi

        # Copy other key documentation
        for doc_file in CHANGELOG.md HANDBOOK.md RUNBOOK.md ARCHITECTURE.md; do
            if [ -f "$proj_dir/$doc_file" ]; then
                sanitize_markdown "$proj_dir/$doc_file" "$output_proj_dir/$doc_file"
            fi
        done

        # Copy docs directory if exists
        if [ -d "$proj_dir/docs" ]; then
            find "$proj_dir/docs" -name "*.md" -type f | while read -r doc; do
                rel_path="${doc#$proj_dir/docs/}"
                output_doc="$output_proj_dir/docs/$rel_path"
                mkdir -p "$(dirname "$output_doc")"
                sanitize_markdown "$doc" "$output_doc"
            done
        fi

        # Add to overview
        echo "- [$proj_name](./$category_name/$proj_name/README.md)" >> "$BUNDLE_DIR/PROJECTS_OVERVIEW.md"
    done
}

# Process each category
echo ""
echo "📂 Processing project categories..."

process_project_category "$REPO_ROOT/projects/01-sde-devops" "01-sde-devops"
process_project_category "$REPO_ROOT/projects/02-cloud-architecture" "02-cloud-architecture"
process_project_category "$REPO_ROOT/projects/03-cybersecurity" "03-cybersecurity"
process_project_category "$REPO_ROOT/projects/04-qa-testing" "04-qa-testing"
process_project_category "$REPO_ROOT/projects/05-networking-datacenter" "05-networking-datacenter"
process_project_category "$REPO_ROOT/projects/06-homelab" "06-homelab"
process_project_category "$REPO_ROOT/projects/07-data-engineering" "07-data-engineering"
process_project_category "$REPO_ROOT/projects/07-aiml-automation" "07-aiml-automation"
process_project_category "$REPO_ROOT/projects/08-aiml" "08-aiml"
process_project_category "$REPO_ROOT/projects/08-web-data" "08-web-data"
process_project_category "$REPO_ROOT/projects/09-web-applications" "09-web-applications"
process_project_category "$REPO_ROOT/projects/10-advanced-topics" "10-advanced-topics"

# Copy guides
echo ""
echo "📚 Copying guides..."
if [ -d "$REPO_ROOT/docs" ]; then
    find "$REPO_ROOT/docs" -name "*.md" -type f | while read -r guide; do
        guide_name=$(basename "$guide")
        echo "  📄 $guide_name"
        sanitize_markdown "$guide" "$BUNDLE_DIR/guides/$guide_name"
    done
fi

# Copy main docs
echo ""
echo "📋 Copying main documentation..."
for doc in STRUCTURE_ANALYSIS_AND_MERGE_PLAN.md VALIDATION_REPORT.md DUPLICATE_DETECTION_REPORT.md VERSION_COMPARISON_REPORT.md; do
    if [ -f "$REPO_ROOT/docs/$doc" ]; then
        echo "  📄 $doc"
        sanitize_markdown "$REPO_ROOT/docs/$doc" "$BUNDLE_DIR/docs/$doc"
    fi
done

# Generate metadata file
echo ""
echo "📊 Generating metadata..."
cat > "$BUNDLE_DIR/METADATA.json" << EOF
{
  "bundle_name": "$BUNDLE_NAME",
  "generated_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "repository": "https://github.com/samueljackson-collab/Portfolio-Project",
  "version": "1.0",
  "format": "markdown",
  "purpose": "ChatGPT Codex upload",
  "file_count": $(find "$BUNDLE_DIR" -type f | wc -l),
  "total_size_bytes": $(du -sb "$BUNDLE_DIR" | cut -f1),
  "categories": [
    "01-sde-devops",
    "02-cloud-architecture",
    "03-cybersecurity",
    "04-qa-testing",
    "06-homelab",
    "07-aiml",
    "08-web-data",
    "10-advanced-topics"
  ]
}
EOF

# Create archive
echo ""
echo -e "${YELLOW}Creating archive...${NC}"
cd "$OUTPUT_DIR"
tar -czf "${BUNDLE_NAME}.tar.gz" "$BUNDLE_NAME"
zip -qr "${BUNDLE_NAME}.zip" "$BUNDLE_NAME"

# Calculate sizes
tar_size=$(du -h "${BUNDLE_NAME}.tar.gz" | cut -f1)
zip_size=$(du -h "${BUNDLE_NAME}.zip" | cut -f1)
dir_size=$(du -sh "$BUNDLE_NAME" | cut -f1)

# Summary
echo ""
echo -e "${BLUE}=== Bundle Generated ===${NC}"
echo ""
echo -e "${GREEN}✓ Bundle created successfully${NC}"
echo ""
echo "Bundle name: $BUNDLE_NAME"
echo "Location: $OUTPUT_DIR"
echo ""
echo "Sizes:"
echo "  Directory: $dir_size"
echo "  TAR.GZ:    $tar_size"
echo "  ZIP:       $zip_size"
echo ""
echo "Files included:"
find "$BUNDLE_DIR" -type f | wc -l | xargs echo "  Total files:"
find "$BUNDLE_DIR" -name "*.md" | wc -l | xargs echo "  Markdown files:"
echo ""
echo -e "${GREEN}Formats available:${NC}"
echo "  1. Directory: $OUTPUT_DIR/$BUNDLE_NAME/"
echo "  2. Archive:   $OUTPUT_DIR/${BUNDLE_NAME}.tar.gz"
echo "  3. Archive:   $OUTPUT_DIR/${BUNDLE_NAME}.zip"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Review bundle: cd $BUNDLE_DIR"
echo "  2. Upload to ChatGPT Codex: Use the .zip or .tar.gz file"
echo "  3. Or upload individual markdown files from the directory"
echo ""
echo -e "${GREEN}✓ Ready for ChatGPT Codex upload!${NC}"

exit 0
