#!/usr/bin/env bash
# Fix common HTML-escaped tokens introduced into Python files that break syntax.
# Replaces occurrences of "-\u003e", "-\\u003e", and similar encodings that
# might have been committed in place of the Python "->" annotation arrow.
# Also normalizes stray "- >" into "->".
#
# Usage: ./scripts/fix_unicode_arrows.sh [target ...]
# If no targets are provided, the current working directory is scanned.

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# print_header prints the repository root path and the list of scanning targets; if no targets are provided it indicates the current directory.
print_header() {
  local targets=("$@")
  printf 'Repository root: %s\n' "$SCRIPT_DIR/.."
  printf 'Scanning targets: %s\n' "${targets[*]:- (current directory)}"
}

# create_backup_if_missing creates a `.bak` backup of the given file if one does not already exist.
create_backup_if_missing() {
  local file="$1"
  local backup="${file}.bak"
  if [[ ! -f "$backup" ]]; then
    cp "$file" "$backup"
  fi
}

# restore_from_backup restores the specified file from its ".bak" backup if that backup file exists.
restore_from_backup() {
  local file="$1"
  local backup="${file}.bak"
  if [[ -f "$backup" ]]; then
    cp "$backup" "$file"
  fi
}

# patch_file normalizes common HTML-escaped Unicode arrow tokens in a Python file, validates the resulting file with the Python compiler, and preserves a .bak backup.
# It creates a .bak backup if one is missing, converts variants such as -\u003e, \\u002d\\u003e, &#45;&#62;, and '- >' into '->', and restores the backup if Python compilation fails.
# Args: file — path to the Python file to process.
patch_file() {
  local file="$1"
  echo "Checking $file"
  create_backup_if_missing "$file"

  sed -i \
    -e 's/-\\\\u003e/->/g' \
    -e 's/-\\u003e/->/g' \
    -e 's/\\u002d\\u003e/->/g' \
    -e 's/&#45;&#62;/->/g' \
    -e 's/-[[:space:]]\+>/->/g' \
    "$file"

  if ! python -m py_compile "$file" >/dev/null 2>&1; then
    echo "WARNING: $file fails Python compile after replacements. Restoring backup."
    restore_from_backup "$file"
    return
  fi

  echo "Patched and validated: $file"
}

# process_target processes a path: if it's a directory, recursively finds all `.py` files and runs `patch_file` on each; if it's a file, runs `patch_file` on it; otherwise emits a skip warning to stderr.
process_target() {
  local target="$1"
  if [[ -d "$target" ]]; then
    while IFS= read -r -d '' file; do
      patch_file "$file"
    done < <(find "$target" -type f -name '*.py' -print0)
  elif [[ -f "$target" ]]; then
    patch_file "$target"
  else
    echo "Skipping missing target: $target" >&2
  fi
}

# main is the script entry point; it collects targets (defaults to the current directory), prints the header, processes each target, and reports completion.
main() {
  local targets=("$@")
  if ((${#targets[@]} == 0)); then
    targets=("$PWD")
  fi

  print_header "${targets[@]}"
  for target in "${targets[@]}"; do
    process_target "$target"
  done
  echo "Done. Files that were changed have .bak backups for review."
}

main "$@"