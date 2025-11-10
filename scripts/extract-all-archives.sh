#!/bin/bash
# Extract All Portfolio Archives
# Purpose: Extract all archive files to organized temp directory structure

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
EXTRACT_BASE="$REPO_ROOT/temp_extraction"
MANIFEST_FILE="$EXTRACT_BASE/extraction_manifest.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Portfolio Archive Extraction Tool ===${NC}"
echo "Repository: $REPO_ROOT"
echo "Extract to: $EXTRACT_BASE"
echo ""

# Create extraction base directory
mkdir -p "$EXTRACT_BASE"

# Initialize manifest
echo "# Archive Extraction Manifest" > "$MANIFEST_FILE"
echo "# Generated: $(date)" >> "$MANIFEST_FILE"
echo "" >> "$MANIFEST_FILE"

# Function to extract an archive
extract_archive() {
    local archive_path="$1"
    local archive_name=$(basename "$archive_path")
    local extract_dir="$EXTRACT_BASE/${archive_name%.*}"

    echo -e "${YELLOW}Processing: $archive_name${NC}"

    # Create extraction directory
    mkdir -p "$extract_dir"

    # Detect archive type and extract
    case "$archive_path" in
        *.tar.gz|*.tgz)
            echo "  Extracting tar.gz archive..."
            tar -xzf "$archive_path" -C "$extract_dir" 2>&1 | head -10
            ;;
        *.tar)
            echo "  Extracting tar archive..."
            tar -xf "$archive_path" -C "$extract_dir" 2>&1 | head -10
            ;;
        *.zip)
            echo "  Extracting zip archive..."
            unzip -q "$archive_path" -d "$extract_dir" 2>&1 | head -10
            ;;
        *)
            echo -e "  ${RED}Unknown archive type, skipping${NC}"
            return 1
            ;;
    esac

    # Count contents
    local file_count=$(find "$extract_dir" -type f | wc -l)
    local dir_count=$(find "$extract_dir" -type d | wc -l)

    echo -e "  ${GREEN}✓ Extracted: $file_count files, $dir_count directories${NC}"

    # Add to manifest
    echo "## $archive_name" >> "$MANIFEST_FILE"
    echo "Location: $extract_dir" >> "$MANIFEST_FILE"
    echo "Files: $file_count" >> "$MANIFEST_FILE"
    echo "Directories: $dir_count" >> "$MANIFEST_FILE"
    echo "Extracted: $(date)" >> "$MANIFEST_FILE"
    echo "" >> "$MANIFEST_FILE"

    # List top-level contents
    echo "### Top-level contents:" >> "$MANIFEST_FILE"
    ls -la "$extract_dir" 2>/dev/null | head -20 >> "$MANIFEST_FILE"
    echo "" >> "$MANIFEST_FILE"

    # Find README files
    echo "### README files found:" >> "$MANIFEST_FILE"
    find "$extract_dir" -name "README.md" -type f >> "$MANIFEST_FILE"
    echo "" >> "$MANIFEST_FILE"

    # Find project directories
    echo "### Project directories:" >> "$MANIFEST_FILE"
    find "$extract_dir" -type d -name "p[0-9]*" -o -name "PRJ-*" -o -name "[0-9]*-*" 2>/dev/null | sort >> "$MANIFEST_FILE"
    echo "" >> "$MANIFEST_FILE"
    echo "---" >> "$MANIFEST_FILE"
    echo "" >> "$MANIFEST_FILE"

    return 0
}

# Find all archives
echo -e "${BLUE}Searching for archive files...${NC}"
archives_found=0

# Search in common locations
search_locations=(
    "$REPO_ROOT"
    "$REPO_ROOT/downloads"
    "$REPO_ROOT/archives"
    "$(pwd)"
)

for location in "${search_locations[@]}"; do
    if [ -d "$location" ]; then
        echo "Searching: $location"
        while IFS= read -r -d '' archive; do
            extract_archive "$archive"
            ((archives_found++))
        done < <(find "$location" -maxdepth 1 \( -name "*.zip" -o -name "*.tar.gz" -o -name "*.tar" -o -name "*.tgz" \) -type f -print0 2>/dev/null)
    fi
done

echo ""
echo -e "${BLUE}=== Extraction Complete ===${NC}"
echo -e "Archives processed: ${GREEN}$archives_found${NC}"
echo -e "Manifest file: ${GREEN}$MANIFEST_FILE${NC}"
echo -e "Extraction directory: ${GREEN}$EXTRACT_BASE${NC}"

if [ $archives_found -eq 0 ]; then
    echo ""
    echo -e "${RED}⚠ No archive files found!${NC}"
    echo ""
    echo "Expected archive files:"
    echo "  - fixed_bundle_20251021_135306.zip"
    echo "  - Homelab project.zip"
    echo "  - Portfolio v2.zip"
    echo "  - portfolio_docs_v3_bundle.zip"
    echo "  - homelab_diagrams_and_photos.tar.gz"
    echo "  - homelab_diagrams_v9_1.tar.gz"
    echo "  - portfolio_repo_unified_20251001-170421.tar.gz"
    echo "  - RedTeam_Bundle.tar.gz"
    echo "  - Deep_Research_Plan_Execution - Copy.zip"
    echo "  - Portfolio.zip"
    echo "  - portfolio_final_bundle.zip"
    echo "  - files (1).zip, files (2).zip, files (3).zip, files (4).zip"
    echo "  - Twisted_Monk_Suite_v1_export.zip"
    echo "  - twisted_monk_suite_repo.zip"
    echo ""
    echo "Please place archive files in one of these locations:"
    for loc in "${search_locations[@]}"; do
        echo "  - $loc"
    done
    exit 1
fi

echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. Review manifest: cat $MANIFEST_FILE"
echo "2. Run duplicate detection: ./scripts/detect-duplicates.sh"
echo "3. Compare versions: ./scripts/compare-versions.py"

# Generate summary
echo ""
echo -e "${BLUE}=== Extraction Summary ===${NC}"
find "$EXTRACT_BASE" -mindepth 1 -maxdepth 1 -type d | while read -r dir; do
    dirname=$(basename "$dir")
    file_count=$(find "$dir" -type f | wc -l)
    echo -e "${GREEN}$dirname${NC}: $file_count files"
done

exit 0
