#!/usr/bin/env bash
set -euo pipefail

# Release Build Script - Enterprise Portfolio
# Creates distribution archives with manifest for portfolio releases

# Configuration
ROOT_DIR="${ROOT_DIR:-enterprise-portfolio}"
VERSION="${VERSION:-0.3.0}"
OUTPUT_DIR="${OUTPUT_DIR:-./dist}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Main build process
main() {
    echo ""
    echo "============================================"
    echo "  Enterprise Portfolio - Release Build"
    echo "============================================"
    echo ""
    echo "Version: v$VERSION"
    echo "Output:  $OUTPUT_DIR"
    echo ""

    # Create output directory
    mkdir -p "$OUTPUT_DIR"

    log_info "Cleaning previous builds..."
    rm -f "$OUTPUT_DIR"/*.{zip,tar.gz,txt,json} || true

    # Generate file manifest
    log_info "Generating file manifest..."
    python3 - <<'PYTHON_SCRIPT'
import os
import json
import hashlib
import pathlib
from datetime import datetime

def calculate_sha256(file_path):
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def generate_manifest(root_dir, output_file):
    """Generate a manifest of all files"""
    manifest = {
        "version": os.getenv("VERSION", "0.3.0"),
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "root": root_dir,
        "files": []
    }

    excluded_patterns = {
        '.git', 'node_modules', 'venv', '__pycache__',
        '.pytest_cache', 'dist', 'build', '*.pyc',
        '.DS_Store', 'Thumbs.db', '*.swp', '.env'
    }

    total_size = 0
    file_count = 0

    for path in pathlib.Path('.').rglob('*'):
        # Skip excluded patterns
        if any(excluded in str(path) for excluded in excluded_patterns):
            continue

        if path.is_file():
            file_size = path.stat().st_size
            total_size += file_size

            file_info = {
                "path": str(path),
                "size": file_size,
                "sha256": calculate_sha256(path)
            }

            manifest["files"].append(file_info)
            file_count += 1

    manifest["summary"] = {
        "total_files": file_count,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2)
    }

    with open(output_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated manifest: {file_count} files, {round(total_size / (1024 * 1024), 2)} MB")

if __name__ == "__main__":
    output_dir = os.getenv("OUTPUT_DIR", "./dist")
    version = os.getenv("VERSION", "0.3.0")
    manifest_file = f"{output_dir}/enterprise-portfolio-v{version}_manifest.json"
    generate_manifest(".", manifest_file)
PYTHON_SCRIPT

    # Create concatenated text file
    log_info "Creating concatenated text file..."
    TXT_FILE="$OUTPUT_DIR/enterprise-portfolio-v${VERSION}_ALL.txt"

    cat > "$TXT_FILE" <<'HEADER'
================================================================================
                     Enterprise Portfolio - Complete Source
================================================================================

This file contains the complete source code and documentation
for the Enterprise Portfolio project.

Version: v${VERSION}
Generated: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

================================================================================

HEADER

    # Find and concatenate all text files
    find . -type f \( \
        -name "*.md" -o \
        -name "*.py" -o \
        -name "*.sh" -o \
        -name "*.yml" -o \
        -name "*.yaml" -o \
        -name "*.json" -o \
        -name "*.tf" -o \
        -name "*.js" -o \
        -name "*.ts" \
        \) \
        ! -path "*/node_modules/*" \
        ! -path "*/.git/*" \
        ! -path "*/venv/*" \
        ! -path "*/__pycache__/*" \
        ! -path "*/dist/*" \
        -print | while read -r file; do
        echo "" >> "$TXT_FILE"
        echo "===== FILE: $file =====" >> "$TXT_FILE"
        echo "" >> "$TXT_FILE"
        cat "$file" >> "$TXT_FILE" 2>/dev/null || echo "[Binary or unreadable file]" >> "$TXT_FILE"
        echo "" >> "$TXT_FILE"
    done

    log_success "Created: $TXT_FILE"

    # Create TAR.GZ archive
    log_info "Creating TAR.GZ archive..."
    TAR_FILE="$OUTPUT_DIR/enterprise-portfolio-v${VERSION}.tar.gz"

    tar -czf "$TAR_FILE" \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='.pytest_cache' \
        --exclude='dist' \
        --exclude='*.pyc' \
        --exclude='.DS_Store' \
        --exclude='Thumbs.db' \
        --exclude='*.swp' \
        --exclude='.env' \
        .

    log_success "Created: $TAR_FILE ($(du -h "$TAR_FILE" | cut -f1))"

    # Create ZIP archive
    log_info "Creating ZIP archive..."
    ZIP_FILE="$OUTPUT_DIR/enterprise-portfolio-v${VERSION}.zip"

    zip -rq "$ZIP_FILE" . \
        -x '*.git*' \
        -x '*node_modules*' \
        -x '*venv*' \
        -x '*__pycache__*' \
        -x '*.pytest_cache*' \
        -x '*dist*' \
        -x '*.pyc' \
        -x '.DS_Store' \
        -x 'Thumbs.db' \
        -x '*.swp' \
        -x '.env'

    log_success "Created: $ZIP_FILE ($(du -h "$ZIP_FILE" | cut -f1))"

    # Summary
    echo ""
    echo "============================================"
    echo "  Build Complete!"
    echo "============================================"
    echo ""
    echo "Release artifacts created in: $OUTPUT_DIR"
    echo ""
    ls -lh "$OUTPUT_DIR"
    echo ""
    log_info "To create a GitHub release, run:"
    echo ""
    echo "  gh release create v${VERSION} \\"
    echo "    $OUTPUT_DIR/*.tar.gz \\"
    echo "    $OUTPUT_DIR/*.zip \\"
    echo "    $OUTPUT_DIR/*_manifest.json \\"
    echo "    --notes 'Release v${VERSION}'"
    echo ""
}

# Run main function
main "$@"
