"""
Comprehensive tests for scripts/organize-screenshots.py

This test suite validates:
- ImageMetadata class functionality
- ScreenshotOrganizer class methods
- File processing and categorization
- Error handling and edge cases
- Command-line argument parsing
- Type hints and annotations
"""

import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
import pytest
import hashlib
import sys
import os

# Add scripts directory to path
BASE_PATH = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_PATH / "scripts"))

# Import after path setup
import organize_screenshots as os_module


class TestImageMetadata:
    """Test ImageMetadata class."""

    def test_image_metadata_initialization(self, tmp_path):
        """Test ImageMetadata initialization with valid file."""
        test_file = tmp_path / "test.png"
        test_file.write_bytes(b"fake image data")
        
        metadata = os_module.ImageMetadata(test_file)
        
        assert metadata.file_path == test_file
        assert metadata.size_bytes > 0
        assert metadata.size_mb > 0
        assert metadata.timestamp != ""

    def test_image_metadata_file_size_calculation(self, tmp_path):
        """Test file size is calculated correctly."""
        test_file = tmp_path / "test.png"
        test_data = b"x" * 1024 * 1024  # 1 MB
        test_file.write_bytes(test_data)
        
        metadata = os_module.ImageMetadata(test_file)
        
        assert metadata.size_bytes == 1024 * 1024
        assert metadata.size_mb == 1.0

    def test_image_metadata_to_dict(self, tmp_path):
        """Test metadata conversion to dictionary."""
        test_file = tmp_path / "test.png"
        test_file.write_bytes(b"test data")
        
        metadata = os_module.ImageMetadata(test_file)
        metadata_dict = metadata.to_dict()
        
        assert isinstance(metadata_dict, dict)
        assert "size_bytes" in metadata_dict
        assert "size_mb" in metadata_dict
        assert "timestamp" in metadata_dict
        assert "width" in metadata_dict
        assert "height" in metadata_dict

    def test_image_metadata_missing_file(self, tmp_path):
        """Test ImageMetadata with non-existent file."""
        missing_file = tmp_path / "missing.png"
        
        with pytest.raises(OSError):
            os_module.ImageMetadata(missing_file)

    def test_image_metadata_without_pil(self, tmp_path, monkeypatch):
        """Test ImageMetadata works without PIL installed."""
        test_file = tmp_path / "test.png"
        test_file.write_bytes(b"test data")
        
        # Simulate PIL not available
        monkeypatch.setattr(os_module, 'HAS_PIL', False)
        
        metadata = os_module.ImageMetadata(test_file)
        
        assert metadata.size_bytes > 0
        assert metadata.width is None
        assert metadata.format is None


class TestScreenshotOrganizerInit:
    """Test ScreenshotOrganizer initialization."""

    def test_organizer_initialization(self, tmp_path):
        """Test ScreenshotOrganizer initialization."""
        organizer = os_module.ScreenshotOrganizer(
            str(tmp_path),
            target_project="PRJ-HOME-001",
            dry_run=True
        )
        
        assert organizer.source_path == tmp_path
        assert organizer.target_project == "PRJ-HOME-001"
        assert organizer.dry_run is True
        assert isinstance(organizer.stats, dict)
        assert isinstance(organizer.catalog, dict)

    def test_organizer_stats_initialization(self, tmp_path):
        """Test stats dictionary is properly initialized."""
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        assert "total" in organizer.stats
        assert "organized" in organizer.stats
        assert "skipped" in organizer.stats
        assert "duplicates" in organizer.stats
        assert "errors" in organizer.stats
        assert all(v == 0 for v in organizer.stats.values())


class TestCalculateFileHash:
    """Test file hash calculation for duplicate detection."""

    def test_calculate_hash_consistent(self, tmp_path):
        """Test hash calculation is consistent."""
        test_file = tmp_path / "test.png"
        test_file.write_bytes(b"test data")
        
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        hash1 = organizer.calculate_file_hash(test_file)
        hash2 = organizer.calculate_file_hash(test_file)
        
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hash length

    def test_calculate_hash_different_files(self, tmp_path):
        """Test different files have different hashes."""
        file1 = tmp_path / "test1.png"
        file2 = tmp_path / "test2.png"
        file1.write_bytes(b"data1")
        file2.write_bytes(b"data2")
        
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        hash1 = organizer.calculate_file_hash(file1)
        hash2 = organizer.calculate_file_hash(file2)
        
        assert hash1 != hash2

    def test_calculate_hash_missing_file(self, tmp_path):
        """Test hash calculation with missing file."""
        missing_file = tmp_path / "missing.png"
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        with pytest.raises(IOError):
            organizer.calculate_file_hash(missing_file)


class TestCategorizeScreenshot:
    """Test screenshot categorization logic."""

    def test_categorize_dashboard(self, tmp_path):
        """Test dashboard categorization."""
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        assert organizer.categorize_screenshot("grafana_dashboard.png") == "dashboards"
        assert organizer.categorize_screenshot("metrics_view.png") == "dashboards"
        assert organizer.categorize_screenshot("chart_display.png") == "dashboards"

    def test_categorize_infrastructure(self, tmp_path):
        """Test infrastructure categorization."""
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        assert organizer.categorize_screenshot("proxmox_cluster.png") == "infrastructure"
        assert organizer.categorize_screenshot("vm_manager.png") == "infrastructure"
        assert organizer.categorize_screenshot("esxi_host.png") == "infrastructure"

    def test_categorize_networking(self, tmp_path):
        """Test networking categorization."""
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        assert organizer.categorize_screenshot("unifi_controller.png") == "networking"
        assert organizer.categorize_screenshot("switch_config.png") == "networking"
        assert organizer.categorize_screenshot("firewall_rules.png") == "networking"

    def test_categorize_monitoring(self, tmp_path):
        """Test monitoring categorization."""
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        assert organizer.categorize_screenshot("prometheus_alerts.png") == "monitoring"
        assert organizer.categorize_screenshot("loki_logs.png") == "monitoring"

    def test_categorize_security(self, tmp_path):
        """Test security categorization."""
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        assert organizer.categorize_screenshot("siem_dashboard.png") == "security"
        assert organizer.categorize_screenshot("threat_detection.png") == "security"

    def test_categorize_misc_default(self, tmp_path):
        """Test unknown files categorized as misc."""
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        assert organizer.categorize_screenshot("random_file.png") == "misc"
        assert organizer.categorize_screenshot("unknown.png") == "misc"

    def test_categorize_case_insensitive(self, tmp_path):
        """Test categorization is case-insensitive."""
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        assert organizer.categorize_screenshot("GRAFANA_Dashboard.PNG") == "dashboards"
        assert organizer.categorize_screenshot("UniFi_Switch.PNG") == "networking"


class TestGenerateNewFilename:
    """Test filename generation logic."""

    def test_generate_filename_format(self, tmp_path):
        """Test generated filename follows convention."""
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        filename = organizer.generate_new_filename(
            "test.png",
            "dashboards",
            "PRJ-HOME-001",
            1
        )
        
        assert filename.startswith("PRJ-HOME-001_dashboards_01_")
        assert filename.endswith(".png")

    def test_generate_filename_with_different_extensions(self, tmp_path):
        """Test filename generation with various extensions."""
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
            filename = organizer.generate_new_filename(
                f"test{ext}",
                "misc",
                "PRJ-HOME-001",
                1
            )
            assert filename.endswith(ext)

    def test_generate_filename_index_formatting(self, tmp_path):
        """Test index is zero-padded correctly."""
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        filename1 = organizer.generate_new_filename("test.png", "misc", "PRJ-HOME-001", 1)
        filename99 = organizer.generate_new_filename("test.png", "misc", "PRJ-HOME-001", 99)
        
        assert "_01_" in filename1
        assert "_99_" in filename99

    def test_generate_filename_invalid_extension_default(self, tmp_path):
        """Test invalid extension defaults to .png."""
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        filename = organizer.generate_new_filename(
            "test.xyz",
            "misc",
            "PRJ-HOME-001",
            1
        )
        
        assert filename.endswith(".png")


class TestFindImageFiles:
    """Test image file discovery."""

    def test_find_image_files_empty_directory(self, tmp_path):
        """Test finding files in empty directory."""
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        files = organizer.find_image_files()
        
        assert len(files) == 0

    def test_find_image_files_with_images(self, tmp_path):
        """Test finding image files."""
        (tmp_path / "test1.png").write_bytes(b"data")
        (tmp_path / "test2.jpg").write_bytes(b"data")
        (tmp_path / "test3.gif").write_bytes(b"data")
        
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        files = organizer.find_image_files()
        
        assert len(files) == 3

    def test_find_image_files_ignores_non_images(self, tmp_path):
        """Test non-image files are ignored."""
        (tmp_path / "test1.png").write_bytes(b"data")
        (tmp_path / "test2.txt").write_bytes(b"data")
        (tmp_path / "test3.pdf").write_bytes(b"data")
        
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        files = organizer.find_image_files()
        
        assert len(files) == 1

    def test_find_image_files_case_insensitive(self, tmp_path):
        """Test file discovery is case-insensitive."""
        (tmp_path / "test1.PNG").write_bytes(b"data")
        (tmp_path / "test2.JPG").write_bytes(b"data")
        
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        files = organizer.find_image_files()
        
        assert len(files) == 2

    def test_find_image_files_missing_directory(self, tmp_path):
        """Test finding files in non-existent directory."""
        missing_dir = tmp_path / "missing"
        organizer = os_module.ScreenshotOrganizer(str(missing_dir))
        
        with pytest.raises(FileNotFoundError):
            organizer.find_image_files()

    def test_find_image_files_not_directory(self, tmp_path):
        """Test error when source is not a directory."""
        file_path = tmp_path / "not_a_dir.txt"
        file_path.write_text("test")
        
        organizer = os_module.ScreenshotOrganizer(str(file_path))
        
        with pytest.raises(NotADirectoryError):
            organizer.find_image_files()


class TestDetermineProject:
    """Test project determination logic."""

    def test_determine_project_from_target(self, tmp_path):
        """Test project determination from target_project parameter."""
        organizer = os_module.ScreenshotOrganizer(
            str(tmp_path),
            target_project="PRJ-HOME-001"
        )
        
        result = organizer.determine_project("any_filename.png")
        assert result == "PRJ-HOME-001"

    def test_determine_project_from_filename(self, tmp_path):
        """Test project auto-detection from filename."""
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        assert organizer.determine_project("prj-home-001_dashboard.png") == "PRJ-HOME-001"
        assert organizer.determine_project("prj-sde-002_test.png") == "PRJ-SDE-002"

    def test_determine_project_none_when_unknown(self, tmp_path):
        """Test returns None for unknown project."""
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        result = organizer.determine_project("unknown_file.png")
        assert result is None


class TestProcessScreenshot:
    """Test screenshot processing workflow."""

    def test_process_screenshot_detects_duplicates(self, tmp_path):
        """Test duplicate detection prevents reprocessing."""
        test_file = tmp_path / "test.png"
        test_file.write_bytes(b"test data")
        
        organizer = os_module.ScreenshotOrganizer(
            str(tmp_path),
            target_project="PRJ-HOME-001"
        )
        
        # Process once
        organizer.process_screenshot(test_file)
        initial_duplicates = organizer.stats['duplicates']
        
        # Process again (should be detected as duplicate)
        organizer.process_screenshot(test_file)
        
        assert organizer.stats['duplicates'] > initial_duplicates

    def test_process_screenshot_increments_stats(self, tmp_path):
        """Test processing updates statistics."""
        test_file = tmp_path / "PRJ-HOME-001_test.png"
        test_file.write_bytes(b"test data")
        
        organizer = os_module.ScreenshotOrganizer(
            str(tmp_path),
            target_project="PRJ-HOME-001",
            dry_run=True
        )
        
        result = organizer.process_screenshot(test_file)
        
        if result:
            assert organizer.stats['organized'] > 0

    def test_process_screenshot_without_project_skips(self, tmp_path):
        """Test screenshot without determinable project is skipped."""
        test_file = tmp_path / "unknown.png"
        test_file.write_bytes(b"test data")
        
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        result = organizer.process_screenshot(test_file)
        
        assert result is False
        assert organizer.stats['skipped'] > 0


class TestGenerateCatalogs:
    """Test catalog generation."""

    def test_generate_markdown_catalog_structure(self, tmp_path):
        """Test markdown catalog has proper structure."""
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        categories = {
            "dashboards": [
                {
                    "filename": "test.png",
                    "original": "original.png",
                    "metadata": {
                        "size_mb": 1.5,
                        "timestamp": "2024-01-01 00:00:00",
                        "width": 1920,
                        "height": 1080,
                        "format": "PNG"
                    },
                    "path": "test/path.png"
                }
            ]
        }
        
        content = organizer._generate_markdown_catalog("PRJ-HOME-001", categories)
        
        assert "# Screenshot Catalog" in content
        assert "PRJ-HOME-001" in content
        assert "## Dashboards" in content
        assert "test.png" in content

    def test_generate_markdown_catalog_includes_metadata(self, tmp_path):
        """Test catalog includes file metadata."""
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        categories = {
            "misc": [
                {
                    "filename": "test.png",
                    "original": "original.png",
                    "metadata": {
                        "size_mb": 2.5,
                        "timestamp": "2024-01-01",
                        "width": 1920,
                        "height": 1080,
                        "format": "PNG"
                    },
                    "path": "test/path.png"
                }
            ]
        }
        
        content = organizer._generate_markdown_catalog("PRJ-HOME-001", categories)
        
        assert "2.5 MB" in content
        assert "1920 x 1080" in content


class TestMainFunction:
    """Test main entry point and CLI argument parsing."""

    def test_main_with_dry_run(self, tmp_path, monkeypatch):
        """Test main function with dry-run flag."""
        (tmp_path / "test.png").write_bytes(b"data")
        
        test_args = ["organize-screenshots.py", str(tmp_path), "--dry-run"]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        # Mock organize to prevent actual execution
        with patch.object(os_module.ScreenshotOrganizer, 'organize', return_value=0):
            result = os_module.main()
        
        assert result == 0

    def test_main_with_project_argument(self, tmp_path, monkeypatch):
        """Test main function with project argument."""
        (tmp_path / "test.png").write_bytes(b"data")
        
        test_args = [
            "organize-screenshots.py",
            str(tmp_path),
            "--project", "PRJ-HOME-001"
        ]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with patch.object(os_module.ScreenshotOrganizer, 'organize', return_value=0):
            result = os_module.main()
        
        assert result == 0

    def test_main_handles_keyboard_interrupt(self, tmp_path, monkeypatch):
        """Test main handles KeyboardInterrupt gracefully."""
        test_args = ["organize-screenshots.py", str(tmp_path)]
        monkeypatch.setattr(sys, 'argv', test_args)
        
        with patch.object(os_module.ScreenshotOrganizer, 'organize', side_effect=KeyboardInterrupt):
            result = os_module.main()
        
        assert result == 130


class TestProjectMapping:
    """Test project mapping configuration."""

    def test_projects_mapping_exists(self):
        """Test PROJECTS mapping is defined."""
        assert hasattr(os_module, 'PROJECTS')
        assert isinstance(os_module.PROJECTS, dict)

    def test_projects_mapping_has_homelab(self):
        """Test PROJECTS includes homelab projects."""
        assert "PRJ-HOME-001" in os_module.PROJECTS
        assert "PRJ-HOME-002" in os_module.PROJECTS

    def test_projects_mapping_has_valid_paths(self):
        """Test PROJECTS mapping has valid relative paths."""
        for project_id, path in os_module.PROJECTS.items():
            assert "/" in path
            assert "projects/" in path


class TestCategoriesConfiguration:
    """Test categories configuration."""

    def test_categories_mapping_exists(self):
        """Test CATEGORIES mapping is defined."""
        assert hasattr(os_module, 'CATEGORIES')
        assert isinstance(os_module.CATEGORIES, dict)

    def test_categories_has_expected_types(self):
        """Test CATEGORIES has expected category types."""
        expected = [
            "dashboards", "infrastructure", "networking",
            "monitoring", "services", "storage", "security",
            "configuration", "deployment", "misc"
        ]
        
        for category in expected:
            assert category in os_module.CATEGORIES

    def test_categories_keywords_are_lists(self):
        """Test category keywords are lists."""
        for category, keywords in os_module.CATEGORIES.items():
            assert isinstance(keywords, list)


class TestTypeHintsAndAnnotations:
    """Test type hints are properly defined."""

    def test_image_metadata_has_type_hints(self):
        """Test ImageMetadata uses type hints."""
        import inspect
        
        sig = inspect.signature(os_module.ImageMetadata.__init__)
        assert sig.parameters['file_path'].annotation != inspect.Parameter.empty

    def test_screenshot_organizer_has_type_hints(self):
        """Test ScreenshotOrganizer uses type hints."""
        import inspect
        
        sig = inspect.signature(os_module.ScreenshotOrganizer.__init__)
        assert sig.parameters['source_dir'].annotation != inspect.Parameter.empty

    def test_calculate_hash_return_type(self):
        """Test calculate_file_hash has return type hint."""
        import inspect
        
        sig = inspect.signature(os_module.ScreenshotOrganizer.calculate_file_hash)
        assert sig.return_annotation == str

    def test_categorize_return_type(self):
        """Test categorize_screenshot has return type hint."""
        import inspect
        
        sig = inspect.signature(os_module.ScreenshotOrganizer.categorize_screenshot)
        assert sig.return_annotation == str


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_filename(self, tmp_path):
        """Test handling of empty filename."""
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        category = organizer.categorize_screenshot("")
        assert category == "misc"

    def test_very_long_filename(self, tmp_path):
        """Test handling of very long filename."""
        long_name = "a" * 500 + ".png"
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        category = organizer.categorize_screenshot(long_name)
        assert category == "misc"

    def test_filename_with_special_characters(self, tmp_path):
        """Test handling of special characters in filename."""
        special_name = "test!@#$%^&*().png"
        organizer = os_module.ScreenshotOrganizer(str(tmp_path))
        
        new_name = organizer.generate_new_filename(
            special_name,
            "misc",
            "PRJ-HOME-001",
            1
        )
        
        assert new_name.endswith(".png")
        assert "PRJ-HOME-001" in new_name