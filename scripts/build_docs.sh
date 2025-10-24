#!/usr/bin/env bash
set -euo pipefail

DOCS_DIR=${DOCS_DIR:-docs}
OUTPUT_DIR=${OUTPUT_DIR:-build/docs}
FORMAT=${1:-html}
TITLE=${TITLE:-"Portfolio Research Docs"}

if ! command -v pandoc >/dev/null 2>&1; then
  cat <<'MSG'
Pandoc is required to bundle documentation.
Install it from https://pandoc.org/installing.html and ensure `pandoc` is on your PATH.
On macOS (Homebrew): `brew install pandoc`
On Debian/Ubuntu: `sudo apt-get install pandoc`
On Windows (winget): `winget install --id=JohnMacFarlane.Pandoc`
MSG
  exit 1
fi

DOC_FILES=()
while IFS= read -r file; do
  DOC_FILES+=("$file")
done < <(find "$DOCS_DIR" -type f -name '*.md' | sort)

if [[ ${#DOC_FILES[@]} -eq 0 ]]; then
  echo "No Markdown files found under $DOCS_DIR. Nothing to bundle."
  exit 0
fi

mkdir -p "$OUTPUT_DIR"

OUTPUT_FILE="$OUTPUT_DIR/research-docs.${FORMAT}"

case "$FORMAT" in
  html)
    pandoc "${DOC_FILES[@]}" --from markdown --toc --metadata title="$TITLE" -o "$OUTPUT_FILE"
    ;;
  pdf)
    pandoc "${DOC_FILES[@]}" --from markdown --toc --metadata title="$TITLE" -o "$OUTPUT_FILE"
    ;;
  *)
    echo "Unsupported format: $FORMAT. Use 'html' or 'pdf'."
    exit 1
    ;;
esac

echo "Bundled documentation saved to $OUTPUT_FILE"
