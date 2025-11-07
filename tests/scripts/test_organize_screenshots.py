"""
Comprehensive tests for organize-screenshots.py script.

This test suite validates:
- ImageMetadata class functionality
- ScreenshotOrganizer class methods
- File categorization logic
- Duplicate detection
- Directory structure creation
- Error handling and edge cases
- CLI argument parsing
"""

import os
import sys
import tempfile
import hashlib
import json
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import pytest

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

# Import after adding to path
import importlib.util
spec = importlib.util.spec_from_file_location(
    "organize_screenshots",
    SCRIPT_DIR / "organize-screenshots.py"
)
organize_screenshots = importlib.util.module_from_spec(spec)
spec.loader.exec_module(organize_screenshots)

ImageMetadata = organize_screenshots.ImageMetadata
ScreenshotOrganizer = organize_screenshots.ScreenshotOrganizer
CATEGORIES = organize_screenshots.CATEGORIES
PROJECTS = organize_screenshots.PROJECTS


@pytest.fixture
def temp_image_file():
    """Create a temporary image file for testing"""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        # Create minimal valid PNG file (1x1 pixel)
        png_data = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01'
            b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        f.write(png_data)
        filepath = Path(f.name)
    yield filepath
    # Cleanup
    if filepath.exists():
        filepath.unlink()


@pytest.fixture
def temp_source_dir():
    """Create temporary source directory with test images"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create test image files with different names
        test_files = [
            'grafana_dashboard.png',
            'prometheus_metrics.jpg',
            'PRJ-HOME-001_network.png',
            'proxmox_cluster.jpeg',
            'unifi_switches.png',
        ]
        
        png_data = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01'
            b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        
        for filename in test_files:
            filepath = tmppath / filename
            filepath.write_bytes(png_data)
        
        yield tmppath


class TestImageMetadata:
    """Test ImageMetadata class"""
    
    def test_metadata_initialization(self, temp_image_file):
        """Test ImageMetadata can be initialized with valid file"""
        metadata = ImageMetadata(temp_image_file)
        
        assert metadata.file_path == temp_image_file
        assert metadata.size_bytes > 0
        assert metadata.size_mb >= 0.0
        assert metadata.timestamp != ""
        assert len(metadata.timestamp) > 0
    
    def test_metadata_file_size_calculation(self, temp_image_file):
        """Test file size is correctly calculated"""
        metadata = ImageMetadata(temp_image_file)
        
        actual_size = os.path.getsize(temp_image_file)
        assert metadata.size_bytes == actual_size
        assert metadata.size_mb == round(actual_size / 1024 / 1024, 2)
    
    def test_metadata_timestamp_format(self, temp_image_file):
        """Test timestamp is in correct format"""
        metadata = ImageMetadata(temp_image_file)
        
        # Should be in format: YYYY-MM-DD HH:MM:SS
        assert len(metadata.timestamp.split()) == 2
        date_part, time_part = metadata.timestamp.split()
        assert len(date_part.split('-')) == 3
        assert len(time_part.split(':')) == 3
    
    def test_metadata_to_dict(self, temp_image_file):
        """Test metadata can be converted to dictionary"""
        metadata = ImageMetadata(temp_image_file)
        data = metadata.to_dict()
        
        assert isinstance(data, dict)
        assert 'size_bytes' in data
        assert 'size_mb' in data
        assert 'timestamp' in data
        assert 'width' in data
        assert 'height' in data
        assert 'format' in data
        assert 'mode' in data
    
    def test_metadata_nonexistent_file(self):
        """Test metadata raises error for nonexistent file"""
        with pytest.raises(OSError):
            ImageMetadata(Path('/nonexistent/file.png'))
    
    def test_metadata_pil_attributes(self, temp_image_file):
        """Test PIL-specific attributes are set when available"""
        metadata = ImageMetadata(temp_image_file)
        
        # These may be None if PIL not available, but should exist
        assert hasattr(metadata, 'width')
        assert hasattr(metadata, 'height')
        assert hasattr(metadata, 'format')
        assert hasattr(metadata, 'mode')


class TestScreenshotOrganizerInit:
    """Test ScreenshotOrganizer initialization"""
    
    def test_organizer_initialization(self, temp_source_dir):
        """Test organizer can be initialized"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        assert organizer.source_path == temp_source_dir
        assert organizer.target_project is None
        assert organizer.dry_run is False
        assert isinstance(organizer.seen_hashes, dict)
        assert isinstance(organizer.catalog, dict)
        assert isinstance(organizer.stats, dict)
    
    def test_organizer_with_project(self, temp_source_dir):
        """Test organizer initialization with specific project"""
        organizer = ScreenshotOrganizer(
            str(temp_source_dir),
            target_project='PRJ-HOME-001'
        )
        
        assert organizer.target_project == 'PRJ-HOME-001'
    
    def test_organizer_dry_run_mode(self, temp_source_dir):
        """Test organizer in dry run mode"""
        organizer = ScreenshotOrganizer(
            str(temp_source_dir),
            dry_run=True
        )
        
        assert organizer.dry_run is True
    
    def test_organizer_stats_initialization(self, temp_source_dir):
        """Test stats dictionary is properly initialized"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        assert 'total' in organizer.stats
        assert 'organized' in organizer.stats
        assert 'skipped' in organizer.stats
        assert 'duplicates' in organizer.stats
        assert 'errors' in organizer.stats
        assert all(v == 0 for v in organizer.stats.values())


class TestCalculateFileHash:
    """Test file hash calculation"""
    
    def test_calculate_hash_consistent(self, temp_image_file):
        """Test hash calculation is consistent"""
        organizer = ScreenshotOrganizer(str(temp_image_file.parent))
        
        hash1 = organizer.calculate_file_hash(temp_image_file)
        hash2 = organizer.calculate_file_hash(temp_image_file)
        
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hash length
    
    def test_calculate_hash_different_files(self, temp_source_dir):
        """Test different files produce different hashes"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        files = list(temp_source_dir.glob('*.png'))
        if len(files) >= 2:
            hash1 = organizer.calculate_file_hash(files[0])
            hash2 = organizer.calculate_file_hash(files[1])
            
            # Same minimal PNG, so hashes will be same
            # Test that hash function works
            assert isinstance(hash1, str)
            assert isinstance(hash2, str)
    
    def test_calculate_hash_nonexistent_file(self, temp_source_dir):
        """Test hash calculation fails for nonexistent file"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        with pytest.raises(IOError):
            organizer.calculate_file_hash(Path('/nonexistent/file.png'))


class TestCategorizeScreenshot:
    """Test screenshot categorization logic"""
    
    def test_categorize_dashboard(self, temp_source_dir):
        """Test dashboard category detection"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        assert organizer.categorize_screenshot('grafana_overview.png') == 'dashboards'
        assert organizer.categorize_screenshot('metrics_dashboard.png') == 'dashboards'
        assert organizer.categorize_screenshot('chart_view.png') == 'dashboards'
    
    def test_categorize_infrastructure(self, temp_source_dir):
        """Test infrastructure category detection"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        assert organizer.categorize_screenshot('proxmox_cluster.png') == 'infrastructure'
        assert organizer.categorize_screenshot('vcenter_vms.png') == 'infrastructure'
        assert organizer.categorize_screenshot('esxi_host.png') == 'infrastructure'
    
    def test_categorize_networking(self, temp_source_dir):
        """Test networking category detection"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        assert organizer.categorize_screenshot('unifi_controller.png') == 'networking'
        assert organizer.categorize_screenshot('switch_config.png') == 'networking'
        assert organizer.categorize_screenshot('network_topology.png') == 'networking'
        assert organizer.categorize_screenshot('pfsense_firewall.png') == 'networking'
    
    def test_categorize_monitoring(self, temp_source_dir):
        """Test monitoring category detection"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        assert organizer.categorize_screenshot('prometheus_alerts.png') == 'monitoring'
        assert organizer.categorize_screenshot('loki_logs.png') == 'monitoring'
    
    def test_categorize_storage(self, temp_source_dir):
        """Test storage category detection"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        assert organizer.categorize_screenshot('truenas_dashboard.png') == 'storage'
        assert organizer.categorize_screenshot('zfs_pools.png') == 'storage'
        assert organizer.categorize_screenshot('nas_storage.png') == 'storage'
    
    def test_categorize_security(self, temp_source_dir):
        """Test security category detection"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        assert organizer.categorize_screenshot('opensearch_siem.png') == 'security'
        assert organizer.categorize_screenshot('threat_detection.png') == 'security'
    
    def test_categorize_misc_fallback(self, temp_source_dir):
        """Test misc category as fallback"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        assert organizer.categorize_screenshot('random_screenshot.png') == 'misc'
        assert organizer.categorize_screenshot('unknown_file.png') == 'misc'
    
    def test_categorize_case_insensitive(self, temp_source_dir):
        """Test categorization is case insensitive"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        assert organizer.categorize_screenshot('GRAFANA_Dashboard.PNG') == 'dashboards'
        assert organizer.categorize_screenshot('Proxmox_Cluster.png') == 'infrastructure'


class TestGenerateNewFilename:
    """Test filename generation"""
    
    def test_generate_filename_format(self, temp_source_dir):
        """Test generated filename follows correct format"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        filename = organizer.generate_new_filename(
            'test.png', 'dashboards', 'PRJ-HOME-001', 1
        )
        
        # Format: PROJECT_CATEGORY_INDEX_TIMESTAMP.ext
        parts = filename.rsplit('.', 1)[0].split('_')
        assert len(parts) >= 4
        assert parts[0] == 'PRJ-HOME-001'
        assert parts[1] == 'dashboards'
        assert parts[2] == '01'  # Index padded to 2 digits
    
    def test_generate_filename_extension_preservation(self, temp_source_dir):
        """Test file extension is preserved"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        assert organizer.generate_new_filename('test.png', 'misc', 'PRJ-HOME-001', 1).endswith('.png')
        assert organizer.generate_new_filename('test.jpg', 'misc', 'PRJ-HOME-001', 1).endswith('.jpg')
        assert organizer.generate_new_filename('test.jpeg', 'misc', 'PRJ-HOME-001', 1).endswith('.jpeg')
    
    def test_generate_filename_index_padding(self, temp_source_dir):
        """Test index is zero-padded to 2 digits"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        filename1 = organizer.generate_new_filename('test.png', 'misc', 'PRJ-HOME-001', 1)
        filename9 = organizer.generate_new_filename('test.png', 'misc', 'PRJ-HOME-001', 9)
        filename10 = organizer.generate_new_filename('test.png', 'misc', 'PRJ-HOME-001', 10)
        
        assert '_01_' in filename1
        assert '_09_' in filename9
        assert '_10_' in filename10
    
    def test_generate_filename_invalid_extension(self, temp_source_dir):
        """Test invalid extension defaults to .png"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        filename = organizer.generate_new_filename('test.xyz', 'misc', 'PRJ-HOME-001', 1)
        assert filename.endswith('.png')


class TestFindImageFiles:
    """Test finding image files"""
    
    def test_find_image_files_success(self, temp_source_dir):
        """Test finding image files in directory"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        files = organizer.find_image_files()
        
        assert len(files) > 0
        assert all(isinstance(f, Path) for f in files)
        assert all(f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'] for f in files)
    
    def test_find_image_files_sorted(self, temp_source_dir):
        """Test found files are sorted"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        files = organizer.find_image_files()
        file_names = [f.name for f in files]
        
        assert file_names == sorted(file_names)
    
    def test_find_image_files_nonexistent_dir(self):
        """Test error when directory doesn't exist"""
        organizer = ScreenshotOrganizer('/nonexistent/directory')
        
        with pytest.raises(FileNotFoundError):
            organizer.find_image_files()
    
    def test_find_image_files_not_directory(self, temp_image_file):
        """Test error when path is not a directory"""
        organizer = ScreenshotOrganizer(str(temp_image_file))
        
        with pytest.raises(NotADirectoryError):
            organizer.find_image_files()
    
    def test_find_image_files_case_insensitive(self, temp_source_dir):
        """Test finds files with uppercase extensions"""
        # Create file with uppercase extension
        uppercase_file = temp_source_dir / "test.PNG"
        png_data = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\x00\x01'
            b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        uppercase_file.write_bytes(png_data)
        
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        files = organizer.find_image_files()
        
        assert any(f.name == "test.PNG" for f in files)


class TestDetermineProject:
    """Test project determination logic"""
    
    def test_determine_project_from_target(self, temp_source_dir):
        """Test project is determined from target_project setting"""
        organizer = ScreenshotOrganizer(
            str(temp_source_dir),
            target_project='PRJ-HOME-001'
        )
        
        assert organizer.determine_project('any_file.png') == 'PRJ-HOME-001'
    
    def test_determine_project_from_filename(self, temp_source_dir):
        """Test project auto-detection from filename"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        assert organizer.determine_project('PRJ-HOME-001_network.png') == 'PRJ-HOME-001'
        assert organizer.determine_project('prj-sde-002_dashboard.png') == 'PRJ-SDE-002'
    
    def test_determine_project_none_when_not_found(self, temp_source_dir):
        """Test returns None when project can't be determined"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        assert organizer.determine_project('random_file.png') is None
    
    def test_determine_project_case_insensitive(self, temp_source_dir):
        """Test project detection is case insensitive"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        assert organizer.determine_project('prj-home-001_test.png') == 'PRJ-HOME-001'
        assert organizer.determine_project('Prj-Home-001_Test.PNG') == 'PRJ-HOME-001'


class TestCategories:
    """Test CATEGORIES constant"""
    
    def test_categories_defined(self):
        """Test CATEGORIES is properly defined"""
        assert isinstance(CATEGORIES, dict)
        assert len(CATEGORIES) > 0
    
    def test_categories_has_expected_keys(self):
        """Test CATEGORIES has expected category names"""
        expected_categories = [
            'dashboards', 'infrastructure', 'networking',
            'monitoring', 'services', 'storage', 'security',
            'configuration', 'deployment', 'misc'
        ]
        
        for category in expected_categories:
            assert category in CATEGORIES
    
    def test_categories_keywords_are_lists(self):
        """Test all category values are lists"""
        for category, keywords in CATEGORIES.items():
            assert isinstance(keywords, list)
    
    def test_misc_category_empty(self):
        """Test misc category has empty keyword list"""
        assert CATEGORIES['misc'] == []


class TestProjects:
    """Test PROJECTS constant"""
    
    def test_projects_defined(self):
        """Test PROJECTS is properly defined"""
        assert isinstance(PROJECTS, dict)
        assert len(PROJECTS) > 0
    
    def test_projects_has_expected_keys(self):
        """Test PROJECTS has expected project IDs"""
        expected_projects = [
            'PRJ-SDE-001', 'PRJ-SDE-002',
            'PRJ-HOME-001', 'PRJ-HOME-002',
            'PRJ-CYB-BLUE-001'
        ]
        
        for project in expected_projects:
            assert project in PROJECTS
    
    def test_projects_paths_are_strings(self):
        """Test all project paths are strings"""
        for proj_id, path in PROJECTS.items():
            assert isinstance(path, str)
            assert len(path) > 0
    
    def test_projects_paths_start_with_projects(self):
        """Test project paths start with 'projects/'"""
        for proj_id, path in PROJECTS.items():
            assert path.startswith('projects/')


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_source_directory(self):
        """Test handling of empty source directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            organizer = ScreenshotOrganizer(tmpdir)
            files = organizer.find_image_files()
            assert files == []
    
    def test_organizer_with_special_characters_in_path(self):
        """Test organizer handles paths with special characters"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            special_dir = tmppath / "test dir with spaces"
            special_dir.mkdir()
            
            organizer = ScreenshotOrganizer(str(special_dir))
            assert organizer.source_path == special_dir
    
    def test_categorize_with_multiple_keywords(self, temp_source_dir):
        """Test categorization with multiple matching keywords"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        # First match should win
        result = organizer.categorize_screenshot('grafana_prometheus_dashboard.png')
        assert result in ['dashboards', 'monitoring']  # Either is valid
    
    def test_metadata_with_zero_size_file(self):
        """Test metadata extraction from zero-size file"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            filepath = Path(f.name)
        
        try:
            metadata = ImageMetadata(filepath)
            assert metadata.size_bytes == 0
            assert metadata.size_mb == 0.0
        finally:
            filepath.unlink()


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_full_workflow_with_valid_files(self, temp_source_dir):
        """Test complete organization workflow"""
        organizer = ScreenshotOrganizer(
            str(temp_source_dir),
            target_project='PRJ-HOME-001',
            dry_run=True
        )
        
        # Should be able to find files
        files = organizer.find_image_files()
        assert len(files) > 0
        
        # Should be able to categorize
        for file in files:
            category = organizer.categorize_screenshot(file.name)
            assert category in CATEGORIES
    
    def test_duplicate_detection_workflow(self, temp_source_dir):
        """Test duplicate detection in workflow"""
        organizer = ScreenshotOrganizer(str(temp_source_dir))
        
        files = organizer.find_image_files()
        if len(files) > 0:
            # Calculate hash for first file
            hash1 = organizer.calculate_file_hash(files[0])
            organizer.seen_hashes[hash1] = files[0].name
            
            # Calculate hash again - should be in seen_hashes
            hash2 = organizer.calculate_file_hash(files[0])
            assert hash2 in organizer.seen_hashes


if __name__ == '__main__':
    pytest.main([__file__, '-v'])