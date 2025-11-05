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

# print_header prints the repository root path and the scanning targets; when no targets are provided, indicates the current directory.
print_header() {
  local targets=("$@")
  printf 'Repository root: %s\n' "$SCRIPT_DIR/.."
  printf 'Scanning targets: %s\n' "${targets[*]:- (current directory)}"
}

# create_backup_if_missing creates a `.bak` backup of the specified file if no backup exists and does not overwrite an existing `.bak` file.
create_backup_if_missing() {
  local file="$1"
  local backup="${file}.bak"
  if [[ ! -f "$backup" ]]; then
    cp "$file" "$backup"
  fi
}

# restore_from_backup restores a file from its `.bak` backup by copying `<file>.bak` over `<file>` if the backup exists.
restore_from_backup() {
  local file="$1"
  local backup="${file}.bak"
  if [[ -f "$backup" ]]; then
    cp "$backup" "$file"
  fi
}

# patch_file replaces common HTML-escaped or malformed Python "->" arrow variants in the given file, creating a `.bak` backup if missing, validating the patched file with Python compilation, and restoring the backup if validation fails.
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

# process_target processes the given path by patching Python files found at that location.
# If the argument is a directory, it recursively finds all `*.py` files and runs `patch_file` on each.
# If the argument is a file, it runs `patch_file` on that file.
# If the path does not exist, it writes a "Skipping missing target: <path>" message to stderr.
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

# main parses provided targets (or defaults to the current working directory), prints a header, processes each target, and reports completion noting that changed files have .bak backups for review.
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