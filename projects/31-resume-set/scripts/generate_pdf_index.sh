#!/usr/bin/env bash
# Generates index of all resume files with metadata
RESUME_DIR="$(dirname "$0")/../../professional/resume"
echo "=== Resume File Index ==="
echo "Generated: $(date)"
echo ""
printf "%-45s %-8s %-12s\n" "File" "Size" "Modified"
printf "%-45s %-8s %-12s\n" "----" "----" "--------"
for f in "$RESUME_DIR"/*.md; do
  name=$(basename "$f")
  size=$(wc -c < "$f" | tr -d ' ')
  modified=$(date -r "$f" +%Y-%m-%d 2>/dev/null || stat -c %y "$f" 2>/dev/null | cut -d' ' -f1)
  printf "%-45s %-8s %-12s\n" "$name" "${size}B" "$modified"
done
echo ""
echo "Total files: $(ls "$RESUME_DIR"/*.md | wc -l)"
