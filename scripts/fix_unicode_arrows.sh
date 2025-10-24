#!/usr/bin/env bash
# Fix common HTML-escaped tokens introduced into Python files that break syntax.
# Replaces occurrences of "-\u003e", "-\\u003e", and similar encodings that
# might have been committed in place of the Python "->" annotation arrow.
#
# Usage: ./scripts/fix_unicode_arrows.sh
set -euo pipefail

ROOT_DIR="$(cd "
$(dirname "
${BASH_SOURCE[0]}")/.. && pwd)"

# Find .py files and perform in-place replacements with a safety backup extension
find "$ROOT_DIR" -type f -name '*.py' -print0 |
  while IFS= read -r -d '' file; do
    echo "Checking $file"
    # Create a backup (only if not exists) so we can review changes:
    cp -n "$file" "${file}.bak" || true

    # Replace common encodings with -> (safe idempotent replacement)
    # - replace literal sequences that represent HTML-encoded arrow variants
    sed -i -e 's/-\\u003e/->/g' \
           -e 's/-\\\\u003e/->/g' \
           -e 's/\\u002d\\u003e/->/g' \
           -e 's/\\u003e/>/g' \
           -e 's/&#45;&#62;/->/g' \
           -e 's/-\s\+>/-\>/g' \
           "$file"

    # Quick Python parse check: compile the file to ensure no immediate syntax error
    python -m py_compile "$file" 2>/dev/null || {
      echo "WARNING: $file fails Python compile after replacements. Restoring backup."
      mv "${file}.bak" "$file"
      continue
    }

    echo "Patched and validated: $file"
  done

echo "Done. Files that were changed have .bak backups for review."