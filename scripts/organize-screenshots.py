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
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
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
PROJECTS: Dict[str, str] = {
    "PRJ-SDE-001": "projects/01-sde-devops/PRJ-SDE-001",
    "PRJ-SDE-002": "projects/01-sde-devops/PRJ-SDE-002",
    "PRJ-HOME-001": "projects/06-homelab/PRJ-HOME-001",
    "PRJ-HOME-002": "projects/06-homelab/PRJ-HOME-002",
    "PRJ-CYB-BLUE-001": "projects/03-cybersecurity/PRJ-CYB-BLUE-001",
}

# Screenshot categories with keywords
CATEGORIES: Dict[str, List[str]] = {
    "dashboards": ["grafana", "dashboard", "metrics", "graph", "chart"],
    "infrastructure": ["proxmox", "vcenter", "esxi", "cluster", "node", "vm"],
    "networking": [
        "unifi",
        "switch",
        "router",
        "topology",
        "network",
        "vlan",
        "firewall",
        "pfsense",
    ],
    "monitoring": ["prometheus", "alert", "loki", "log", "monitor"],
    "services": ["wikijs", "homeassistant", "immich", "service", "app", "application"],
    "storage": ["truenas", "nas", "zfs", "dataset", "disk", "storage"],
    "security": ["siem", "opensearch", "security", "threat", "detection"],
    "configuration": ["config", "setting", "setup", "preferences"],
    "deployment": ["deploy", "install", "provision", "terraform", "ansible"],
    "misc": [],  # Default category
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class ImageMetadata:
    """Image metadata container with validation"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.size_bytes: int = 0
        self.size_mb: float = 0.0
        self.timestamp: str = ""
        self.width: Optional[int] = None
        self.height: Optional[int] = None
        self.format: Optional[str] = None
        self.mode: Optional[str] = None
        self._extract_metadata()

    def _extract_metadata(self) -> None:
        """Extract metadata from image file"""
        try:
            self.size_bytes = os.path.getsize(self.file_path)
            self.size_mb = round(self.size_bytes / 1024 / 1024, 2)
            self.timestamp = datetime.fromtimestamp(
                os.path.getmtime(self.file_path)
            ).strftime("%Y-%m-%d %H:%M:%S")

            if HAS_PIL:
                try:
                    with Image.open(self.file_path) as img:
                        self.width = img.width
                        self.height = img.height
                        self.format = img.format
                        self.mode = img.mode
                except Exception as e:
                    logger.warning(f"Could not extract PIL metadata: {e}")
        except OSError as e:
            logger.error(f"Failed to read file metadata: {e}")
            raise

    def to_dict(self) -> Dict[str, any]:
        """Convert metadata to dictionary"""
        return {
            "size_bytes": self.size_bytes,
            "size_mb": self.size_mb,
            "timestamp": self.timestamp,
            "width": self.width,
            "height": self.height,
            "format": self.format,
            "mode": self.mode,
        }


class ScreenshotOrganizer:
    """Main screenshot organization orchestrator"""

    def __init__(
        self,
        source_dir: str,
        target_project: Optional[str] = None,
        dry_run: bool = False,
    ):
        self.source_path = Path(source_dir)
        self.target_project = target_project
        self.dry_run = dry_run
        self.seen_hashes: Dict[str, str] = {}
        self.catalog: Dict[str, Dict[str, List[Dict]]] = {}
        self.stats = {
            "total": 0,
            "organized": 0,
            "skipped": 0,
            "duplicates": 0,
            "errors": 0,
        }

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file for duplicate detection"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except IOError as e:
            logger.error(f"Failed to calculate hash for {file_path}: {e}")
            raise

    def categorize_screenshot(self, filename: str) -> str:
        """Determine category based on filename keywords"""
        filename_lower = filename.lower()

        for category, keywords in CATEGORIES.items():
            if category == "misc":
                continue
            for keyword in keywords:
                if keyword in filename_lower:
                    return category

        return "misc"

    def generate_new_filename(
        self, original_name: str, category: str, project: str, index: int
    ) -> str:
        """Generate consistent filename with validation"""
        # Extract extension
        ext = Path(original_name).suffix.lower()
        valid_extensions = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}

        if ext not in valid_extensions:
            logger.warning(f"Unknown extension {ext}, defaulting to .png")
            ext = ".png"

        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d")

        # Create new name: PROJECT_CATEGORY_INDEX_TIMESTAMP.ext
        new_name = f"{project}_{category}_{index:02d}_{timestamp}{ext}"

        return new_name

    def find_image_files(self) -> List[Path]:
        """Find all image files in source directory"""
        if not self.source_path.exists():
            raise FileNotFoundError(f"Source directory not found: {self.source_path}")

        if not self.source_path.is_dir():
            raise NotADirectoryError(
                f"Source path is not a directory: {self.source_path}"
            )

        image_extensions = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"]
        image_files: List[Path] = []

        for ext in image_extensions:
            image_files.extend(self.source_path.glob(f"*{ext}"))
            image_files.extend(self.source_path.glob(f"*{ext.upper()}"))

        return sorted(set(image_files))

    def determine_project(self, filename: str) -> Optional[str]:
        """Determine target project from filename or configuration"""
        if self.target_project:
            return self.target_project

        # Try to auto-detect from filename
        for proj_id in PROJECTS.keys():
            if proj_id.lower() in filename.lower():
                return proj_id

        return None

    def process_screenshot(self, img_file: Path) -> bool:
        """Process a single screenshot file"""
        try:
            logger.info(f"Processing: {img_file.name}")

            # Calculate hash for duplicate detection
            file_hash = self.calculate_file_hash(img_file)

            if file_hash in self.seen_hashes:
                logger.warning(f"Duplicate of {self.seen_hashes[file_hash]}")
                self.stats["duplicates"] += 1
                return False

            self.seen_hashes[file_hash] = img_file.name

            # Determine project
            project = self.determine_project(img_file.name)
            if not project:
                logger.warning(
                    f"Could not determine project for {img_file.name}. Use --project flag."
                )
                self.stats["skipped"] += 1
                return False

            # Validate project exists
            if project not in PROJECTS:
                logger.error(f"Unknown project: {project}")
                self.stats["skipped"] += 1
                return False

            # Determine category
            category = self.categorize_screenshot(img_file.name)

            # Get metadata
            try:
                metadata = ImageMetadata(img_file)
            except Exception as e:
                logger.error(f"Failed to extract metadata: {e}")
                self.stats["errors"] += 1
                return False

            # Determine destination
            project_path = (
                PORTFOLIO_ROOT / PROJECTS[project] / "assets" / "screenshots" / category
            )

            # Create directory structure
            if not self.dry_run:
                try:
                    project_path.mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    logger.error(f"Failed to create directory {project_path}: {e}")
                    self.stats["errors"] += 1
                    return False

            # Generate new filename
            existing_files = (
                list(project_path.glob(f"{project}_{category}_*"))
                if project_path.exists()
                else []
            )
            index = len(existing_files) + 1
            new_filename = self.generate_new_filename(
                img_file.name, category, project, index
            )

            dest_file = project_path / new_filename

            logger.info(f"  → {project}/{category}/{new_filename}")
            logger.info(f"     Size: {metadata.size_mb} MB")
            if metadata.width:
                logger.info(f"     Dimensions: {metadata.width}x{metadata.height}")

            # Copy file
            if not self.dry_run:
                try:
                    shutil.copy2(img_file, dest_file)
                except (IOError, OSError) as e:
                    logger.error(f"Failed to copy file: {e}")
                    self.stats["errors"] += 1
                    return False

                # Store catalog entry
                if project not in self.catalog:
                    self.catalog[project] = {}
                if category not in self.catalog[project]:
                    self.catalog[project][category] = []

                self.catalog[project][category].append(
                    {
                        "filename": new_filename,
                        "original": img_file.name,
                        "metadata": metadata.to_dict(),
                        "path": str(dest_file.relative_to(PORTFOLIO_ROOT)),
                    }
                )

            self.stats["organized"] += 1
            return True

        except Exception as e:
            logger.error(
                f"Unexpected error processing {img_file.name}: {e}", exc_info=True
            )
            self.stats["errors"] += 1
            return False

    def organize(self) -> int:
        """Main organization workflow"""
        try:
            image_files = self.find_image_files()
        except (FileNotFoundError, NotADirectoryError) as e:
            logger.error(str(e))
            return 1

        if not image_files:
            logger.warning(f"No image files found in {self.source_path}")
            return 0

        self.stats["total"] = len(image_files)
        logger.info(f"Found {len(image_files)} screenshot(s) to organize\n")

        # Process each screenshot
        for img_file in image_files:
            self.process_screenshot(img_file)

        # Generate catalog files
        if not self.dry_run and self.catalog:
            self.generate_catalogs()

        # Print summary
        self.print_summary()

        return 0 if self.stats["errors"] == 0 else 1

    def generate_catalogs(self) -> None:
        """Generate markdown catalogs for each project"""
        logger.info("\nGenerating screenshot catalogs...")

        for project, categories in self.catalog.items():
            try:
                project_path = (
                    PORTFOLIO_ROOT / PROJECTS[project] / "assets" / "screenshots"
                )
                catalog_file = project_path / "README.md"

                # Generate markdown content
                content = self._generate_markdown_catalog(project, categories)

                # Write catalog file
                with open(catalog_file, "w", encoding="utf-8") as f:
                    f.write(content)

                logger.info(
                    f"  ✓ Created catalog: {catalog_file.relative_to(PORTFOLIO_ROOT)}"
                )

                # Also create a JSON index
                json_file = project_path / "screenshots-index.json"
                with open(json_file, "w", encoding="utf-8") as f:
                    json.dump(self.catalog[project], f, indent=2)

                logger.info(
                    f"  ✓ Created JSON index: {json_file.relative_to(PORTFOLIO_ROOT)}"
                )

            except (IOError, OSError) as e:
                logger.error(f"Failed to generate catalog for {project}: {e}")

    def _generate_markdown_catalog(
        self, project: str, categories: Dict[str, List[Dict]]
    ) -> str:
        """Generate markdown content for catalog"""
        content = f"""# Screenshot Catalog - {project}
{'=' * 50}

This directory contains organized screenshots for the {project} project.

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Screenshots:** {sum(len(files) for files in categories.values())}

---

"""

        for category, screenshots in sorted(categories.items()):
            content += f"\n## {category.title()}\n\n"
            content += f"**Count:** {len(screenshots)}\n\n"

            for screenshot in sorted(screenshots, key=lambda x: x["filename"]):
                metadata = screenshot["metadata"]
                content += f"### {screenshot['filename']}\n\n"

                # Relative path for markdown
                rel_path = f"{category}/{screenshot['filename']}"
                content += f"![{screenshot['filename']}]({rel_path})\n\n"

                content += "**Details:**\n"
                content += f"- Original filename: `{screenshot['original']}`\n"
                content += f"- File size: {metadata['size_mb']} MB\n"

                if metadata.get("width"):
                    content += (
                        f"- Dimensions: {metadata['width']} x {metadata['height']} px\n"
                    )
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
        return content

    def print_summary(self) -> None:
        """Print organization summary"""
        print("=" * 60)
        print("ORGANIZATION SUMMARY")
        print("=" * 60)
        print(f"Total screenshots: {self.stats['total']}")
        print(f"Organized: {self.stats['organized']}")
        print(f"Skipped: {self.stats['skipped']}")
        print(f"Duplicates: {self.stats['duplicates']}")
        print(f"Errors: {self.stats['errors']}")
        print("=" * 60)

        if self.dry_run:
            print("\n⚠ DRY RUN - No files were actually moved")
        else:
            print("\n✓ Screenshot organization complete!")


def main() -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Organize portfolio screenshots with intelligent categorization",
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
        """,
    )

    parser.add_argument("source", help="Source directory containing screenshots")
    parser.add_argument(
        "--project",
        choices=list(PROJECTS.keys()),
        help="Target project (auto-detected if not specified)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview organization without moving files",
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    print("=" * 60)
    print("  Screenshot Organization Tool")
    print("=" * 60)
    print()

    if args.dry_run:
        print("⚠ DRY RUN MODE - No files will be moved\n")

    try:
        organizer = ScreenshotOrganizer(args.source, args.project, args.dry_run)
        return organizer.organize()
    except KeyboardInterrupt:
        logger.warning("\nOperation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
