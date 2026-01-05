#!/usr/bin/env python3
"""
Create GitHub-viewable diagram files
=====================================
Since PNG conversion requires external APIs or browsers (blocked in sandbox),
this script creates .md files that GitHub can render natively with Mermaid.

GitHub supports native Mermaid rendering in markdown code blocks.
"""

import os
from pathlib import Path


def create_markdown_viewer(mermaid_file):
    """Create a markdown file that GitHub can render"""
    # Read the mermaid content
    try:
        with open(mermaid_file, "r", encoding="utf-8", errors="ignore") as f:
            mermaid_content = f.read()
    except Exception as e:
        print(f"  ✗ Failed to read: {e}")
        return False

    # Create markdown wrapper
    md_file = mermaid_file.with_suffix(".md")
    diagram_name = mermaid_file.stem.replace("-", " ").title()

    markdown_content = f"""# {diagram_name}

This diagram is rendered using Mermaid syntax. GitHub will render it automatically when viewing this file.

## Diagram

```mermaid
{mermaid_content.strip()}
```

## Source File

Original: `{mermaid_file.name}`

## Viewing Options

1. **GitHub Web Interface**: View this .md file on GitHub - the diagram will render automatically
2. **VS Code**: Install the "Markdown Preview Mermaid Support" extension
3. **Export to PNG**: Use <https://mermaid.live> to paste the code and export

---
*Auto-generated to enable GitHub native rendering*
"""

    # Write markdown file
    try:
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        return True
    except Exception as e:
        print(f"  ✗ Failed to write: {e}")
        return False


def main():
    root_dir = Path(__file__).parent.parent
    print("=" * 60)
    print("  Creating GitHub-Viewable Diagram Files")
    print("=" * 60)
    print()

    # Find all mermaid files
    mermaid_files = list(root_dir.rglob("*.mmd")) + list(root_dir.rglob("*.mermaid"))
    mermaid_files = sorted(mermaid_files)

    if not mermaid_files:
        print("No Mermaid files found!")
        return 1

    print(f"Found {len(mermaid_files)} diagram files\n")

    success = 0
    failed = 0

    for mermaid_file in mermaid_files:
        rel_path = mermaid_file.relative_to(root_dir)
        print(f"Processing: {rel_path}")

        if create_markdown_viewer(mermaid_file):
            md_file = mermaid_file.with_suffix(".md")
            rel_md = md_file.relative_to(root_dir)
            print(f"  ✓ Created: {rel_md.name}")
            success += 1
        else:
            failed += 1

        print()

    print("=" * 60)
    print(f"✓ Success: {success}")
    if failed > 0:
        print(f"✗ Failed: {failed}")
    print("=" * 60)
    print()
    print("GitHub will automatically render these .md files with diagrams!")
    print("View them on GitHub web interface to see the rendered diagrams.")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
