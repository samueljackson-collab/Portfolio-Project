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
    'PRJ-SDE-001': 'projects/01-sde-devops/PRJ-SDE-001',
    'PRJ-SDE-002': 'projects/01-sde-devops/PRJ-SDE-002',
    'PRJ-HOME-001': 'projects/06-homelab/PRJ-HOME-001',
    'PRJ-HOME-002': 'projects/06-homelab/PRJ-HOME-002',
    'PRJ-CYB-BLUE-001': 'projects/03-cybersecurity/PRJ-CYB-BLUE-001',
}

# Screenshot categories with keywords
CATEGORIES: Dict[str, List[str]] = {
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class ImageMetadata:
    """Image metadata container with validation"""

    def __init__(self, file_path: Path):
        """
        Create an ImageMetadata instance for the given image file and populate its metadata fields.
        
        Parameters:
            file_path (Path): Path to the image file whose metadata will be collected.
        
        Remarks:
            Initializes attributes such as `size_bytes`, `size_mb`, `timestamp`, `width`, `height`, `format`, and `mode`, and immediately extracts their values from the provided file.
        """
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
        """
        Populate instance fields with file size, modification timestamp, and image properties when available.
        
        Extracts and sets:
        - `size_bytes`: file size in bytes
        - `size_mb`: file size in megabytes rounded to two decimals
        - `timestamp`: last-modified time formatted as "YYYY-MM-DD HH:MM:SS"
        If Pillow is available, also sets `width`, `height`, `format`, and `mode`; if Pillow extraction fails those fields remain unset.
        
        Raises:
            OSError: If the file cannot be accessed to read size or modification time.
        """
        try:
            self.size_bytes = os.path.getsize(self.file_path)
            self.size_mb = round(self.size_bytes / 1024 / 1024, 2)
            self.timestamp = datetime.fromtimestamp(
                os.path.getmtime(self.file_path)
            ).strftime('%Y-%m-%d %H:%M:%S')

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
        """
        Return a dictionary containing extracted image metadata.
        
        Returns:
            dict: Mapping with keys:
                - `size_bytes`: file size in bytes
                - `size_mb`: file size in megabytes (float)
                - `timestamp`: last-modified timestamp (POSIX float)
                - `width`: image width in pixels or `None` if unavailable
                - `height`: image height in pixels or `None` if unavailable
                - `format`: image format string (e.g., "PNG") or `None` if unavailable
                - `mode`: image mode (e.g., "RGB") or `None` if unavailable
        """
        return {
            'size_bytes': self.size_bytes,
            'size_mb': self.size_mb,
            'timestamp': self.timestamp,
            'width': self.width,
            'height': self.height,
            'format': self.format,
            'mode': self.mode
        }


class ScreenshotOrganizer:
    """Main screenshot organization orchestrator"""

    def __init__(self, source_dir: str, target_project: Optional[str] = None, dry_run: bool = False):
        """
        Initialize the organizer with a source directory, optional fixed project target, and dry-run flag.
        
        Sets up internal state used during organization: resolved source path, optional target project override, dry-run mode, a map of seen file hashes for duplicate detection, an in-memory catalog keyed by project and category, and counters for operation statistics.
        
        Parameters:
            source_dir (str): Path to the directory containing screenshots to process.
            target_project (Optional[str]): If provided, force all screenshots to be organized under this project; if None, project will be inferred per file.
            dry_run (bool): When True, simulate actions without creating directories or copying files.
        
        Attributes initialized:
            source_path (Path): Resolved Path object for source_dir.
            target_project (Optional[str])
            dry_run (bool)
            seen_hashes (Dict[str, str]): MD5 hashes of processed files to detect duplicates.
            catalog (Dict[str, Dict[str, List[Dict]]]): In-memory catalog structured by project then category.
            stats (dict): Counters with keys 'total', 'organized', 'skipped', 'duplicates', and 'errors'.
        """
        self.source_path = Path(source_dir)
        self.target_project = target_project
        self.dry_run = dry_run
        self.seen_hashes: Dict[str, str] = {}
        self.catalog: Dict[str, Dict[str, List[Dict]]] = {}
        self.stats = {
            'total': 0,
            'organized': 0,
            'skipped': 0,
            'duplicates': 0,
            'errors': 0
        }

    def calculate_file_hash(self, file_path: Path) -> str:
        """
        Compute the MD5 hexadecimal digest of the given file's contents.
        
        Parameters:
            file_path (Path): Path to the file to hash.
        
        Returns:
            str: Hexadecimal MD5 digest of the file contents.
        
        Raises:
            IOError: If the file cannot be opened or read.
        """
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
        """
        Assigns a category name by matching the given filename against configured keyword lists.
        
        Parameters:
            filename (str): The filename or path string to inspect for category keywords.
        
        Returns:
            category (str): The matching category name from CATEGORIES, or 'misc' if no keywords match.
        """
        filename_lower = filename.lower()

        for category, keywords in CATEGORIES.items():
            if category == 'misc':
                continue
            for keyword in keywords:
                if keyword in filename_lower:
                    return category

        return 'misc'

    def generate_new_filename(self, original_name: str, category: str, project: str, index: int) -> str:
        """
        Builds a standardized filename for a screenshot using project, category, index, and the current date.
        
        If the original filename's extension is not a recognized image extension, `.png` is used and a warning is logged.
        
        Parameters:
            original_name (str): Original filename or path from which the extension will be derived.
            category (str): Category name to include in the filename.
            project (str): Project identifier to include in the filename.
            index (int): Numeric index for the file within the category; formatted with two digits.
        
        Returns:
            str: Generated filename in the form `PROJECT_CATEGORY_XX_YYYYMMDD.ext` (e.g., `myproj_ui_01_20251107.png`).
        """
        # Extract extension
        ext = Path(original_name).suffix.lower()
        valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'}

        if ext not in valid_extensions:
            logger.warning(f"Unknown extension {ext}, defaulting to .png")
            ext = '.png'

        # Generate timestamp
        timestamp = datetime.now().strftime('%Y%m%d')

        # Create new name: PROJECT_CATEGORY_INDEX_TIMESTAMP.ext
        new_name = f"{project}_{category}_{index:02d}_{timestamp}{ext}"

        return new_name

    def find_image_files(self) -> List[Path]:
        """
        Collect all image files in the source directory using common image file extensions.
        
        Searches the source directory for files with extensions .png, .jpg, .jpeg, .gif, .webp, and .bmp (case-insensitive) and returns a sorted, de-duplicated list of matching Path objects.
        
        Returns:
        	List[Path]: Sorted list of unique image file paths found in the source directory.
        
        Raises:
        	FileNotFoundError: If the configured source directory does not exist.
        	NotADirectoryError: If the configured source path exists but is not a directory.
        """
        if not self.source_path.exists():
            raise FileNotFoundError(f"Source directory not found: {self.source_path}")

        if not self.source_path.is_dir():
            raise NotADirectoryError(f"Source path is not a directory: {self.source_path}")

        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp']
        image_files: List[Path] = []

        for ext in image_extensions:
            image_files.extend(self.source_path.glob(f'*{ext}'))
            image_files.extend(self.source_path.glob(f'*{ext.upper()}'))

        return sorted(set(image_files))

    def determine_project(self, filename: str) -> Optional[str]:
        """
        Resolve the target project for a given filename.
        
        Parameters:
            filename (str): File name or path used to detect the project; matching is case-insensitive and succeeds if any known project ID appears anywhere in the string.
        
        Returns:
            project_id (Optional[str]): A known project key that matches the filename, or `None` if no project could be determined.
        """
        if self.target_project:
            return self.target_project

        # Try to auto-detect from filename
        for proj_id in PROJECTS.keys():
            if proj_id.lower() in filename.lower():
                return proj_id

        return None

    def process_screenshot(self, img_file: Path) -> bool:
        """
        Process a single screenshot file: validate, categorize, extract metadata, and (unless in dry-run) copy it into the project assets and record it in the in-memory catalog.
        
        Parameters:
            img_file (Path): Path to the screenshot file to process.
        
        Returns:
            bool: `True` if the screenshot was successfully organized and recorded, `False` otherwise.
        
        Notes:
            - Detects and skips duplicates based on file hash.
            - Determines target project (explicit or inferred) and category from the filename.
            - Updates internal statistics (`organized`, `skipped`, `duplicates`, `errors`) and the `catalog`.
            - Creates destination directories and copies the file when not in dry-run mode.
            - Returns `False` for any validation, metadata extraction, I/O, or unexpected errors.
        """
        try:
            logger.info(f"Processing: {img_file.name}")

            # Calculate hash for duplicate detection
            file_hash = self.calculate_file_hash(img_file)

            if file_hash in self.seen_hashes:
                logger.warning(f"Duplicate of {self.seen_hashes[file_hash]}")
                self.stats['duplicates'] += 1
                return False

            self.seen_hashes[file_hash] = img_file.name

            # Determine project
            project = self.determine_project(img_file.name)
            if not project:
                logger.warning(f"Could not determine project for {img_file.name}. Use --project flag.")
                self.stats['skipped'] += 1
                return False

            # Validate project exists
            if project not in PROJECTS:
                logger.error(f"Unknown project: {project}")
                self.stats['skipped'] += 1
                return False

            # Determine category
            category = self.categorize_screenshot(img_file.name)

            # Get metadata
            try:
                metadata = ImageMetadata(img_file)
            except Exception as e:
                logger.error(f"Failed to extract metadata: {e}")
                self.stats['errors'] += 1
                return False

            # Determine destination
            project_path = PORTFOLIO_ROOT / PROJECTS[project] / 'assets' / 'screenshots' / category

            # Create directory structure
            if not self.dry_run:
                try:
                    project_path.mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    logger.error(f"Failed to create directory {project_path}: {e}")
                    self.stats['errors'] += 1
                    return False

            # Generate new filename
            existing_files = list(project_path.glob(f'{project}_{category}_*')) if project_path.exists() else []
            index = len(existing_files) + 1
            new_filename = self.generate_new_filename(img_file.name, category, project, index)

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
                    self.stats['errors'] += 1
                    return False

                # Store catalog entry
                if project not in self.catalog:
                    self.catalog[project] = {}
                if category not in self.catalog[project]:
                    self.catalog[project][category] = []

                self.catalog[project][category].append({
                    'filename': new_filename,
                    'original': img_file.name,
                    'metadata': metadata.to_dict(),
                    'path': str(dest_file.relative_to(PORTFOLIO_ROOT))
                })

            self.stats['organized'] += 1
            return True

        except Exception as e:
            logger.error(f"Unexpected error processing {img_file.name}: {e}", exc_info=True)
            self.stats['errors'] += 1
            return False

    def organize(self) -> int:
        """
        Coordinate scanning of the source directory, per-file processing, and catalog generation for screenshots.
        
        This method finds image files, processes each through the organizer pipeline (duplicate detection, project/category determination, metadata extraction, and file copying unless in dry-run), generates project catalogs when not in dry-run, and prints a summary of operations.
        
        Returns:
            int: `0` when processing completed with no errors; `1` if the source path was invalid or any processing errors occurred.
        """
        try:
            image_files = self.find_image_files()
        except (FileNotFoundError, NotADirectoryError) as e:
            logger.error(str(e))
            return 1

        if not image_files:
            logger.warning(f"No image files found in {self.source_path}")
            return 0

        self.stats['total'] = len(image_files)
        logger.info(f"Found {len(image_files)} screenshot(s) to organize\n")

        # Process each screenshot
        for img_file in image_files:
            self.process_screenshot(img_file)

        # Generate catalog files
        if not self.dry_run and self.catalog:
            self.generate_catalogs()

        # Print summary
        self.print_summary()

        return 0 if self.stats['errors'] == 0 else 1

    def generate_catalogs(self) -> None:
        """Generate markdown catalogs for each project"""
        logger.info("\nGenerating screenshot catalogs...")

        for project, categories in self.catalog.items():
            try:
                project_path = PORTFOLIO_ROOT / PROJECTS[project] / 'assets' / 'screenshots'
                catalog_file = project_path / 'README.md'

                # Generate markdown content
                content = self._generate_markdown_catalog(project, categories)

                # Write catalog file
                with open(catalog_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                logger.info(f"  ✓ Created catalog: {catalog_file.relative_to(PORTFOLIO_ROOT)}")

                # Also create a JSON index
                json_file = project_path / 'screenshots-index.json'
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(self.catalog[project], f, indent=2)

                logger.info(f"  ✓ Created JSON index: {json_file.relative_to(PORTFOLIO_ROOT)}")

            except (IOError, OSError) as e:
                logger.error(f"Failed to generate catalog for {project}: {e}")

    def _generate_markdown_catalog(self, project: str, categories: Dict[str, List[Dict]]) -> str:
        """
        Builds a Markdown catalog describing screenshots organized for a project.
        
        Produces a Markdown document that includes a title, last-updated timestamp, total screenshot count, and one section per category. Each category lists screenshots (sorted by filename) with an embedded image reference and details: original filename, file size (MB), dimensions and format when available, and creation timestamp. The document also contains usage examples and the file-naming convention.
        
        Parameters:
            project (str): Project identifier used in the catalog title and explanatory text.
            categories (Dict[str, List[Dict]]): Mapping from category name to a list of screenshot records. Each screenshot record is expected to contain:
                - 'filename' (str): Organized filename stored in the category.
                - 'original' (str): Original source filename.
                - 'metadata' (dict): Metadata including at least 'size_mb' and 'timestamp'; may include 'width', 'height', and 'format'.
        
        Returns:
            str: The complete Markdown content for the project's screenshot catalog.
        """
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

            for screenshot in sorted(screenshots, key=lambda x: x['filename']):
                metadata = screenshot['metadata']
                content += f"### {screenshot['filename']}\n\n"

                # Relative path for markdown
                rel_path = f"{category}/{screenshot['filename']}"
                content += f"![{screenshot['filename']}]({rel_path})\n\n"

                content += "**Details:**\n"
                content += f"- Original filename: `{screenshot['original']}`\n"
                content += f"- File size: {metadata['size_mb']} MB\n"

                if metadata.get('width'):
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
        return content

    def print_summary(self) -> None:
        """
        Display a formatted summary of the organizer's statistics to standard output.
        
        Shows counts for total screenshots processed, organized, skipped, duplicates, and errors,
        and emits a final line indicating whether the run was a dry run (no files moved) or completed.
        """
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
    """
    Run the CLI to organize screenshots and return a process exit code.
    
    Parses command-line arguments (source directory, optional project, --dry-run, --verbose),
    instantiates and invokes ScreenshotOrganizer, and reports a concise exit status. Handles
    user cancellation and unexpected fatal errors by returning distinct exit codes.
    
    Returns:
        int: `0` on successful completion with no errors; `1` on fatal error; `130` if cancelled by the user (KeyboardInterrupt).
    """
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


if __name__ == '__main__':
    sys.exit(main())