#!/usr/bin/env python3
"""
Screenshot Organization & Cataloging Tool
==========================================
Automatically organizes screenshots for portfolio projects with intelligent
naming, categorization, and catalog generation.

Features:
- Organizes screenshots by project and category
- Renames with consistent naming convention
- Extracts metadata (dimensions, file size, timestamp)
- Generates markdown catalog with thumbnails
- Creates screenshot index for easy reference
- Handles duplicates and validates image files

Usage:
    # Organize screenshots from a source directory
    python3 organize-screenshots.py /path/to/screenshots

    # Organize with specific project
    python3 organize-screenshots.py /path/to/screenshots --project PRJ-HOME-001

    # Dry run (preview without moving files)
    python3 organize-screenshots.py /path/to/screenshots --dry-run

Author: Portfolio Project Automation
"""

import os
import sys
import argparse
import shutil
from pathlib import Path
from datetime import datetime
import hashlib
import json

# Try to import PIL for image metadata
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("⚠ Warning: PIL not installed. Image metadata will be limited.")
    print("  Install with: pip install Pillow")

# Portfolio root directory
PORTFOLIO_ROOT = Path(__file__).parent.parent

# Project mapping
PROJECTS = {
    'PRJ-SDE-001': 'projects/01-sde-devops/PRJ-SDE-001',
    'PRJ-SDE-002': 'projects/01-sde-devops/PRJ-SDE-002',
    'PRJ-HOME-001': 'projects/06-homelab/PRJ-HOME-001',
    'PRJ-HOME-002': 'projects/06-homelab/PRJ-HOME-002',
    'PRJ-CYB-BLUE-001': 'projects/03-cybersecurity/PRJ-CYB-BLUE-001',
}

# Screenshot categories with keywords
CATEGORIES = {
    'dashboards': ['grafana', 'dashboard', 'metrics', 'graph', 'chart'],
    'infrastructure': ['proxmox', 'vcenter', 'esxi', 'cluster', 'node', 'vm'],
    'networking': ['unifi', 'switch', 'router', 'topology', 'network', 'vlan', 'firewall', 'pfsense'],
    'monitoring': ['prometheus', 'alert', 'loki', 'log', 'monitor'],
    'services': ['wikijs', 'homeassistant', 'immich', 'service', 'app', 'application'],
    'storage': ['truenas', 'nas', 'zfs', 'dataset', 'disk', 'storage'],
    'security': ['siem', 'opensearch', 'security', 'threat', 'detection'],
    'configuration': ['config', 'setting', 'setup', 'preferences'],
    'deployment': ['deploy', 'install', 'provision', 'terraform', 'ansible'],
    'misc': []  # Default category
}

def calculate_file_hash(file_path):
    """Calculate MD5 hash of file for duplicate detection"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def get_image_metadata(file_path):
    """Extract image metadata"""
    metadata = {
        'size_bytes': os.path.getsize(file_path),
        'size_mb': round(os.path.getsize(file_path) / 1024 / 1024, 2),
        'timestamp': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
    }

    if HAS_PIL:
        try:
            with Image.open(file_path) as img:
                metadata['width'] = img.width
                metadata['height'] = img.height
                metadata['format'] = img.format
                metadata['mode'] = img.mode
        except Exception as e:
            print(f"  ⚠ Could not extract image metadata: {e}")

    return metadata

def categorize_screenshot(filename):
    """Determine category based on filename"""
    filename_lower = filename.lower()

    for category, keywords in CATEGORIES.items():
        if category == 'misc':
            continue
        for keyword in keywords:
            if keyword in filename_lower:
                return category

    return 'misc'

def generate_new_filename(original_name, category, project, index):
    """Generate consistent filename"""
    # Extract extension
    ext = Path(original_name).suffix.lower()
    if ext not in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
        ext = '.png'

    # Generate timestamp
    timestamp = datetime.now().strftime('%Y%m%d')

    # Create new name: PROJECT_CATEGORY_INDEX_TIMESTAMP.ext
    new_name = f"{project}_{category}_{index:02d}_{timestamp}{ext}"

    return new_name

def organize_screenshots(source_dir, project=None, dry_run=False):
    """Main organization logic"""
    source_path = Path(source_dir)

    if not source_path.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return 1

    # Find all image files
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp']
    image_files = []

    for ext in image_extensions:
        image_files.extend(source_path.glob(f'*{ext}'))
        image_files.extend(source_path.glob(f'*{ext.upper()}'))

    if not image_files:
        print(f"⚠ No image files found in {source_dir}")
        return 0

    print(f"Found {len(image_files)} screenshot(s) to organize\n")

    # Track statistics
    stats = {
        'total': len(image_files),
        'organized': 0,
        'skipped': 0,
        'duplicates': 0,
        'errors': 0
    }

    # Track file hashes for duplicate detection
    seen_hashes = {}

    # Catalog data
    catalog = {}

    for img_file in image_files:
        print(f"Processing: {img_file.name}")

        try:
            # Calculate hash for duplicate detection
            file_hash = calculate_file_hash(img_file)

            if file_hash in seen_hashes:
                print(f"  ⚠ Duplicate of {seen_hashes[file_hash]}")
                stats['duplicates'] += 1
                continue

            seen_hashes[file_hash] = img_file.name

            # Determine project
            target_project = project
            if not target_project:
                # Try to auto-detect from filename
                for proj_id in PROJECTS.keys():
                    if proj_id.lower() in img_file.name.lower():
                        target_project = proj_id
                        break

                if not target_project:
                    print(f"  ⚠ Could not determine project. Use --project flag.")
                    stats['skipped'] += 1
                    continue

            # Determine category
            category = categorize_screenshot(img_file.name)

            # Get metadata
            metadata = get_image_metadata(img_file)

            # Determine destination
            project_path = PORTFOLIO_ROOT / PROJECTS[target_project] / 'assets' / 'screenshots' / category

            # Create directory structure
            if not dry_run:
                project_path.mkdir(parents=True, exist_ok=True)

            # Generate new filename
            existing_files = list(project_path.glob(f'{target_project}_{category}_*')) if project_path.exists() else []
            index = len(existing_files) + 1
            new_filename = generate_new_filename(img_file.name, category, target_project, index)

            dest_file = project_path / new_filename

            print(f"  → {target_project}/{category}/{new_filename}")
            print(f"     Size: {metadata['size_mb']} MB")
            if 'width' in metadata:
                print(f"     Dimensions: {metadata['width']}x{metadata['height']}")

            # Copy or move file
            if not dry_run:
                shutil.copy2(img_file, dest_file)

                # Store catalog entry
                if target_project not in catalog:
                    catalog[target_project] = {}
                if category not in catalog[target_project]:
                    catalog[target_project][category] = []

                catalog[target_project][category].append({
                    'filename': new_filename,
                    'original': img_file.name,
                    'metadata': metadata,
                    'path': str(dest_file.relative_to(PORTFOLIO_ROOT))
                })

            stats['organized'] += 1
            print()

        except Exception as e:
            print(f"  ❌ Error: {e}")
            stats['errors'] += 1
            print()

    # Generate catalog files
    if not dry_run and catalog:
        generate_catalogs(catalog)

    # Print summary
    print("=" * 60)
    print("ORGANIZATION SUMMARY")
    print("=" * 60)
    print(f"Total screenshots: {stats['total']}")
    print(f"Organized: {stats['organized']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"Duplicates: {stats['duplicates']}")
    print(f"Errors: {stats['errors']}")
    print("=" * 60)

    if dry_run:
        print("\n⚠ DRY RUN - No files were actually moved")
    else:
        print("\n✓ Screenshot organization complete!")

    return 0

def generate_catalogs(catalog):
    """Generate markdown catalogs for each project"""
    print("\nGenerating screenshot catalogs...")

    for project, categories in catalog.items():
        project_path = PORTFOLIO_ROOT / PROJECTS[project] / 'assets' / 'screenshots'
        catalog_file = project_path / 'README.md'

        # Generate markdown content
        content = f"""# Screenshot Catalog - {project}
# {'=' * 50}

This directory contains organized screenshots for the {project} project.

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Screenshots:** {sum(len(files) for files in categories.values())}

---

"""

        for category, screenshots in sorted(categories.items()):
            content += f"\n## {category.title()}\n\n"
            content += f"**Count:** {len(screenshots)}\n\n"

            for screenshot in sorted(screenshots, key=lambda x: x['filename']):
                metadata = screenshot['metadata']
                content += f"### {screenshot['filename']}\n\n"

                # Relative path for markdown
                rel_path = f"{category}/{screenshot['filename']}"
                content += f"![{screenshot['filename']}]({rel_path})\n\n"

                content += "**Details:**\n"
                content += f"- Original filename: `{screenshot['original']}`\n"
                content += f"- File size: {metadata['size_mb']} MB\n"

                if 'width' in metadata:
                    content += f"- Dimensions: {metadata['width']} x {metadata['height']} px\n"
                    content += f"- Format: {metadata.get('format', 'Unknown')}\n"

                content += f"- Created: {metadata['timestamp']}\n"
                content += "\n---\n\n"

        content += """
## How to Use These Screenshots

### In Documentation
Reference screenshots in your project README using relative paths:
```markdown
![Description](./assets/screenshots/category/filename.png)
```

### In Presentations
Screenshots are organized by category for easy selection:
- **dashboards**: Monitoring and metrics visualizations
- **infrastructure**: VM/cluster management interfaces
- **networking**: Network topology and configuration
- **services**: Application interfaces

### File Naming Convention
Format: `PROJECT_CATEGORY_INDEX_TIMESTAMP.ext`

Example: `PRJ-HOME-001_dashboards_01_20241106.png`
- Project: PRJ-HOME-001
- Category: dashboards
- Index: 01 (first in category)
- Date: 2024-11-06

---

**Organized by:** Screenshot Organization Tool
**Tool:** `scripts/organize-screenshots.py`
"""

        # Write catalog file
        with open(catalog_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✓ Created catalog: {catalog_file.relative_to(PORTFOLIO_ROOT)}")

        # Also create a JSON index
        json_file = project_path / 'screenshots-index.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(catalog[project], f, indent=2)

        print(f"  ✓ Created JSON index: {json_file.relative_to(PORTFOLIO_ROOT)}")

def main():
    parser = argparse.ArgumentParser(
        description='Organize portfolio screenshots with intelligent categorization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Organize all screenshots
  python3 organize-screenshots.py /path/to/screenshots

  # Organize for specific project
  python3 organize-screenshots.py /path/to/screenshots --project PRJ-HOME-001

  # Preview without moving files
  python3 organize-screenshots.py /path/to/screenshots --dry-run

Categories:
  Screenshots are automatically categorized by filename keywords:
  - dashboards: Grafana, metrics, charts
  - infrastructure: Proxmox, VMs, clusters
  - networking: UniFi, switches, topology
  - monitoring: Prometheus, alerts, logs
  - services: Applications, web interfaces
  - storage: TrueNAS, NAS, ZFS
  - security: SIEM, security tools
  - configuration: Settings, configs
  - deployment: Terraform, Ansible
  - misc: Uncategorized
        """
    )

    parser.add_argument('source', help='Source directory containing screenshots')
    parser.add_argument('--project', choices=list(PROJECTS.keys()),
                        help='Target project (auto-detected if not specified)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview organization without moving files')
    parser.add_argument('--verbose', action='store_true',
                        help='Show detailed output')

    args = parser.parse_args()

    print("=" * 60)
    print("  Screenshot Organization Tool")
    print("=" * 60)
    print()

    if args.dry_run:
        print("⚠ DRY RUN MODE - No files will be moved\n")

    return organize_screenshots(args.source, args.project, args.dry_run)

if __name__ == '__main__':
    sys.exit(main())
