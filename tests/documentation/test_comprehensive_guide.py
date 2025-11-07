"""
Tests for docs/COMPREHENSIVE_PORTFOLIO_IMPLEMENTATION_GUIDE.md

This test suite validates:
- Document structure and organization
- Content completeness
- Section consistency
- Project coverage
- Code block formatting
"""

import re
from pathlib import Path
import pytest


@pytest.fixture
def guide_path():
    """Return path to comprehensive guide."""
    return Path("docs/COMPREHENSIVE_PORTFOLIO_IMPLEMENTATION_GUIDE.md")


class TestGuideExistence:
    """Test guide file properties."""

    def test_guide_exists(self, guide_path):
        """Verify comprehensive guide exists."""
        assert guide_path.exists(), "Comprehensive guide should exist"

    def test_guide_not_empty(self, guide_path):
        """Verify guide has substantial content."""
        content = guide_path.read_text()
        word_count = len(content.split())
        assert word_count >= 1000, \
               f"Guide should be comprehensive (at least 1000 words), got {word_count}"


class TestGuideStructure:
    """Test guide structure and organization."""

    def test_has_title(self, guide_path):
        """Verify guide has a main title."""
        content = guide_path.read_text()
        assert re.search(r'^#\s+', content, re.MULTILINE), "Should have H1 title"

    def test_has_table_of_contents(self, guide_path):
        """Verify guide has table of contents."""
        content = guide_path.read_text()
        assert "table of contents" in content.lower() or "## table" in content.lower(), \
               "Should have table of contents"

    def test_has_multiple_projects(self, guide_path):
        """Verify guide covers multiple projects."""
        content = guide_path.read_text()
        # Should have multiple project sections
        project_count = len(re.findall(r'(?:PROJECT|PRJ)\s+\d+', content, re.IGNORECASE))
        assert project_count >= 5, f"Should cover at least 5 projects, found {project_count}"

    def test_has_consistent_project_sections(self, guide_path):
        """Verify projects follow consistent structure."""
        content = guide_path.read_text()
        
        # Should have standard sections
        standard_sections = [
            "learning objectives",
            "architecture",
            "implementation",
        ]
        
        found_sections = sum(1 for section in standard_sections 
                           if section in content.lower())
        
        assert found_sections >= 2, \
               "Projects should follow consistent section structure"


class TestContentQuality:
    """Test content quality and completeness."""

    def test_has_code_examples(self, guide_path):
        """Verify guide includes code examples."""
        content = guide_path.read_text()
        assert "```" in content, "Should include code blocks"
        
        code_block_count = content.count("```")
        assert code_block_count >= 4, "Should have multiple code examples"

    def test_has_architecture_diagrams(self, guide_path):
        """Verify guide includes or references architecture diagrams."""
        content = guide_path.read_text()
        assert "architecture" in content.lower() or "diagram" in content.lower(), \
               "Should discuss architecture"

    def test_covers_multiple_domains(self, guide_path):
        """Verify guide covers multiple technical domains."""
        content = guide_path.read_text()
        
        domains = [
            "devops", "cloud", "security", "network", "qa", "test"
        ]
        
        found_domains = sum(1 for domain in domains if domain in content.lower())
        assert found_domains >= 3, \
               f"Should cover multiple domains, found {found_domains}"

    def test_mentions_aws_services(self, guide_path):
        """Verify guide mentions AWS services."""
        content = guide_path.read_text()
        
        aws_services = ["rds", "ec2", "s3", "cloudformation", "lambda", "eks"]
        found_services = sum(1 for service in aws_services if service in content.lower())
        
        assert found_services >= 2, "Should mention multiple AWS services"


class TestPracticalValue:
    """Test that guide provides practical value."""

    def test_has_deployment_instructions(self, guide_path):
        """Verify guide includes deployment instructions."""
        content = guide_path.read_text()
        assert any(keyword in content.lower() 
                  for keyword in ["deploy", "deployment", "install", "setup"]), \
               "Should include deployment instructions"

    def test_has_troubleshooting_guidance(self, guide_path):
        """Verify guide includes troubleshooting information."""
        content = guide_path.read_text()
        assert any(keyword in content.lower() 
                  for keyword in ["troubleshoot", "problem", "error", "issue", "fix"]), \
               "Should include troubleshooting guidance"

    def test_has_best_practices(self, guide_path):
        """Verify guide includes best practices."""
        content = guide_path.read_text()
        assert "best practice" in content.lower() or \
               "recommendation" in content.lower(), \
               "Should include best practices"