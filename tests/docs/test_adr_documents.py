"""
Comprehensive tests for Architecture Decision Records (ADRs)

This test suite validates:
- ADR file existence and structure
- Required sections presence
- Markdown syntax validity
- Internal link integrity
- Code block syntax
- Consistency across ADRs
- Metadata completeness
"""

import pytest
import re
import yaml
import json
from pathlib import Path
from typing import List, Dict, Set

BASE_PATH = Path(__file__).parent.parent.parent


class TestADRFileExistence:
    """Test that ADR files exist and are accessible"""

    def test_adr_directory_exists(self):
        """Verify the ADR directory exists"""
        adr_dir = BASE_PATH / "docs" / "adr"
        assert adr_dir.exists(), "ADR directory does not exist"
        assert adr_dir.is_dir(), "ADR path is not a directory"

    def test_adr_readme_exists(self):
        """Verify ADR README exists"""
        readme = BASE_PATH / "docs" / "adr" / "README.md"
        assert readme.exists(), "ADR README.md does not exist"
        assert readme.is_file(), "ADR README.md is not a file"

    @pytest.mark.parametrize("adr_file", [
        "ADR-004-multi-layer-caching-strategy.md",
        "ADR-005-comprehensive-observability-strategy.md",
        "ADR-006-zero-trust-security-architecture.md",
        "ADR-007-event-driven-architecture.md",
    ])
    def test_adr_files_exist(self, adr_file):
        """Verify individual ADR files exist"""
        file_path = BASE_PATH / "docs" / "adr" / adr_file
        assert file_path.exists(), f"ADR file {adr_file} does not exist"
        assert file_path.is_file(), f"{adr_file} is not a file"


class TestADRStructure:
    """Test ADR document structure and required sections"""

    def _get_adr_content(self, filename: str) -> str:
        """Helper to read ADR file content"""
        file_path = BASE_PATH / "docs" / "adr" / filename
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _extract_headers(self, content: str) -> List[str]:
        """Extract all markdown headers from content"""
        return re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)

    @pytest.mark.parametrize("adr_file", [
        "ADR-004-multi-layer-caching-strategy.md",
        "ADR-005-comprehensive-observability-strategy.md",
        "ADR-006-zero-trust-security-architecture.md",
        "ADR-007-event-driven-architecture.md",
    ])
    def test_adr_has_title(self, adr_file):
        """Verify ADR has a title (H1 header)"""
        content = self._get_adr_content(adr_file)
        h1_headers = re.findall(r'^#\s+(.+)$', content, re.MULTILINE)
        assert len(h1_headers) > 0, f"{adr_file} does not have a title (H1 header)"
        
        # Title should contain ADR number
        adr_number = adr_file.split('-')[1]
        assert any(f"ADR-{adr_number}" in title or f"ADR {adr_number}" in title 
                   for title in h1_headers), f"{adr_file} title does not contain ADR number"

    @pytest.mark.parametrize("adr_file,required_sections", [
        ("ADR-004-multi-layer-caching-strategy.md", ["Status", "Context", "Decision", "Consequences"]),
        ("ADR-005-comprehensive-observability-strategy.md", ["Status", "Context", "Decision", "Consequences"]),
        ("ADR-006-zero-trust-security-architecture.md", ["Status", "Context", "Decision", "Consequences"]),
        ("ADR-007-event-driven-architecture.md", ["Status", "Context", "Decision", "Consequences"]),
    ])
    def test_adr_has_required_sections(self, adr_file, required_sections):
        """Verify ADR contains all required sections"""
        content = self._get_adr_content(adr_file)
        headers = self._extract_headers(content)
        
        for section in required_sections:
            assert any(section in header for header in headers), \
                f"{adr_file} is missing required section: {section}"

    @pytest.mark.parametrize("adr_file", [
        "ADR-004-multi-layer-caching-strategy.md",
        "ADR-005-comprehensive-observability-strategy.md",
        "ADR-006-zero-trust-security-architecture.md",
        "ADR-007-event-driven-architecture.md",
    ])
    def test_adr_status_section_format(self, adr_file):
        """Verify Status section has proper format"""
        content = self._get_adr_content(adr_file)
        
        # Status section should exist and contain a valid status
        assert re.search(r'##\s+Status', content), f"{adr_file} missing Status header"
        
        # Should have a status value (Accepted, Proposed, Deprecated, Superseded)
        status_match = re.search(
            r'##\s+Status\s*\n\s*(\w+(?:\s+-\s+\w+\s+\d{4})?)',
            content,
            re.MULTILINE
        )
        assert status_match, f"{adr_file} Status section has invalid format"
        
        status_value = status_match.group(1).lower()
        valid_statuses = ['accepted', 'proposed', 'deprecated', 'superseded']
        assert any(status in status_value for status in valid_statuses), \
            f"{adr_file} has invalid status: {status_value}"

    @pytest.mark.parametrize("adr_file", [
        "ADR-004-multi-layer-caching-strategy.md",
        "ADR-005-comprehensive-observability-strategy.md",
        "ADR-006-zero-trust-security-architecture.md",
        "ADR-007-event-driven-architecture.md",
    ])
    def test_adr_has_substantial_content(self, adr_file):
        """Verify ADR has substantial content (not just headers)"""
        content = self._get_adr_content(adr_file)
        
        # Remove code blocks
        content_no_code = re.sub(r'```[\s\S]*?```', '', content)
        
        # Remove headers
        content_no_headers = re.sub(r'^#{1,6}\s+.+$', '', content_no_code, flags=re.MULTILINE)
        
        # Count remaining words
        words = content_no_headers.split()
        assert len(words) > 100, f"{adr_file} has insufficient content (< 100 words)"


class TestADRCodeBlocks:
    """Test code blocks within ADR documents"""

    def _get_adr_content(self, filename: str) -> str:
        """Helper to read ADR file content"""
        file_path = BASE_PATH / "docs" / "adr" / filename
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """Extract code blocks with their language identifiers"""
        pattern = r'```(\w*)\n([\s\S]*?)```'
        matches = re.findall(pattern, content)
        return [{'language': lang, 'code': code} for lang, code in matches]

    @pytest.mark.parametrize("adr_file", [
        "ADR-004-multi-layer-caching-strategy.md",
        "ADR-005-comprehensive-observability-strategy.md",
        "ADR-006-zero-trust-security-architecture.md",
        "ADR-007-event-driven-architecture.md",
    ])
    def test_adr_code_blocks_have_language(self, adr_file):
        """Verify code blocks specify their language"""
        content = self._get_adr_content(adr_file)
        code_blocks = self._extract_code_blocks(content)
        
        # Allow some blocks without language (for plain text examples)
        blocks_with_language = [b for b in code_blocks if b['language']]
        assert len(blocks_with_language) >= len(code_blocks) * 0.7, \
            f"{adr_file} has too many code blocks without language identifiers"

    @pytest.mark.parametrize("adr_file", [
        "ADR-004-multi-layer-caching-strategy.md",
    ])
    def test_adr_yaml_blocks_valid(self, adr_file):
        """Verify YAML code blocks are syntactically valid"""
        content = self._get_adr_content(adr_file)
        code_blocks = self._extract_code_blocks(content)
        
        yaml_blocks = [b for b in code_blocks if b['language'] in ['yaml', 'yml']]
        
        for i, block in enumerate(yaml_blocks):
            try:
                yaml.safe_load(block['code'])
            except yaml.YAMLError as e:
                pytest.fail(f"{adr_file} has invalid YAML in block {i+1}: {str(e)}")

    @pytest.mark.parametrize("adr_file", [
        "ADR-004-multi-layer-caching-strategy.md",
        "ADR-005-comprehensive-observability-strategy.md",
    ])
    def test_adr_json_blocks_valid(self, adr_file):
        """Verify JSON code blocks are syntactically valid"""
        content = self._get_adr_content(adr_file)
        code_blocks = self._extract_code_blocks(content)
        
        json_blocks = [b for b in code_blocks if b['language'] == 'json']
        
        for i, block in enumerate(json_blocks):
            try:
                json.loads(block['code'])
            except json.JSONDecodeError as e:
                pytest.fail(f"{adr_file} has invalid JSON in block {i+1}: {str(e)}")

    @pytest.mark.parametrize("adr_file", [
        "ADR-004-multi-layer-caching-strategy.md",
        "ADR-005-comprehensive-observability-strategy.md",
        "ADR-006-zero-trust-security-architecture.md",
        "ADR-007-event-driven-architecture.md",
    ])
    def test_adr_code_blocks_not_empty(self, adr_file):
        """Verify code blocks contain actual code"""
        content = self._get_adr_content(adr_file)
        code_blocks = self._extract_code_blocks(content)
        
        for i, block in enumerate(code_blocks):
            code_stripped = block['code'].strip()
            assert len(code_stripped) > 0, \
                f"{adr_file} has empty code block at position {i+1}"


class TestADRLinks:
    """Test internal and external links in ADR documents"""

    def _get_adr_content(self, filename: str) -> str:
        """Helper to read ADR file content"""
        file_path = BASE_PATH / "docs" / "adr" / filename
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _extract_markdown_links(self, content: str) -> List[Dict[str, str]]:
        """Extract markdown links [text](url)"""
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(pattern, content)
        return [{'text': text, 'url': url} for text, url in matches]

    @pytest.mark.parametrize("adr_file", [
        "ADR-004-multi-layer-caching-strategy.md",
        "ADR-005-comprehensive-observability-strategy.md",
        "ADR-006-zero-trust-security-architecture.md",
        "ADR-007-event-driven-architecture.md",
    ])
    def test_adr_internal_links_valid(self, adr_file):
        """Verify internal links point to existing files"""
        content = self._get_adr_content(adr_file)
        links = self._extract_markdown_links(content)
        
        base_dir = BASE_PATH / "docs" / "adr"
        
        for link in links:
            url = link['url']
            
            # Skip external URLs
            if url.startswith('http://') or url.startswith('https://'):
                continue
            
            # Skip anchors
            if url.startswith('#'):
                continue
            
            # Check relative links to .md files
            if url.endswith('.md'):
                # Remove anchor if present
                url_path = url.split('#')[0]
                
                # Resolve relative path
                if url_path.startswith('../'):
                    # Go up from adr directory
                    target = (base_dir / url_path).resolve()
                elif url_path.startswith('./'):
                    # Same directory
                    target = (base_dir / url_path[2:]).resolve()
                else:
                    # Assume same directory
                    target = (base_dir / url_path).resolve()
                
                assert target.exists(), \
                    f"{adr_file} contains broken link: {url} -> {target}"

    def test_adr_readme_links_valid(self):
        """Verify README links point to existing ADR files"""
        readme_path = BASE_PATH / "docs" / "adr" / "README.md"
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        links = self._extract_markdown_links(content)
        adr_dir = BASE_PATH / "docs" / "adr"
        
        for link in links:
            url = link['url']
            
            # Only check ADR links
            if 'ADR-' in url and url.endswith('.md'):
                url_path = url.split('#')[0]
                target = (adr_dir / url_path.lstrip('./')).resolve()
                
                assert target.exists(), \
                    f"README contains broken link: {url} -> {target}"


class TestADRConsistency:
    """Test consistency across ADR documents"""

    def _get_all_adr_files(self) -> List[Path]:
        """Get all ADR files (excluding README)"""
        adr_dir = BASE_PATH / "docs" / "adr"
        return [f for f in adr_dir.glob("ADR-*.md") if f.name != "README.md"]

    def test_adr_numbering_sequential(self):
        """Verify ADR numbers are present and properly formatted"""
        adr_files = self._get_all_adr_files()
        adr_numbers = []
        
        for adr_file in adr_files:
            match = re.search(r'ADR-(\d+)', adr_file.name)
            assert match, f"ADR file {adr_file.name} has invalid naming format"
            adr_numbers.append(int(match.group(1)))
        
        # Check that numbers are unique
        assert len(adr_numbers) == len(set(adr_numbers)), \
            "Duplicate ADR numbers found"
        
        # Check that numbers use consistent padding
        for adr_file in adr_files:
            match = re.search(r'ADR-(\d+)', adr_file.name)
            number_str = match.group(1)
            assert len(number_str) == 3, \
                f"ADR number in {adr_file.name} should be 3 digits (e.g., 004)"

    def test_adr_readme_index_complete(self):
        """Verify README index includes all ADR files"""
        adr_files = self._get_all_adr_files()
        readme_path = BASE_PATH / "docs" / "adr" / "README.md"
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        for adr_file in adr_files:
            # Check if ADR is referenced in README
            adr_name = adr_file.name
            assert adr_name in readme_content or adr_name.replace('-', ' ') in readme_content, \
                f"ADR {adr_name} is not listed in README index"

    def test_adr_filename_matches_title(self):
        """Verify ADR filename is consistent with title"""
        adr_files = self._get_all_adr_files()
        
        for adr_file in adr_files:
            with open(adr_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract ADR number from filename
            filename_match = re.search(r'ADR-(\d+)', adr_file.name)
            filename_number = filename_match.group(1)
            
            # Extract ADR number from title
            title_match = re.search(r'^#\s+ADR-(\d+)', content, re.MULTILINE)
            if title_match:
                title_number = title_match.group(1)
                assert filename_number == title_number, \
                    f"ADR number in filename ({filename_number}) doesn't match title ({title_number})"


class TestADRMetrics:
    """Test metrics and data in ADR documents"""

    def _get_adr_content(self, filename: str) -> str:
        """Helper to read ADR file content"""
        file_path = BASE_PATH / "docs" / "adr" / filename
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_adr_004_has_performance_metrics(self):
        """Verify ADR-004 includes performance metrics"""
        content = self._get_adr_content("ADR-004-multi-layer-caching-strategy.md")
        
        # Should have a performance results section
        assert "Performance Results" in content or "Results" in content, \
            "ADR-004 should include performance results"
        
        # Should contain metric values
        metric_patterns = [
            r'\d+ms',  # milliseconds
            r'\d+%',   # percentages
            r'\d+x',   # multipliers
        ]
        
        has_metrics = any(re.search(pattern, content) for pattern in metric_patterns)
        assert has_metrics, "ADR-004 should contain quantitative metrics"

    @pytest.mark.parametrize("adr_file", [
        "ADR-004-multi-layer-caching-strategy.md",
        "ADR-005-comprehensive-observability-strategy.md",
        "ADR-006-zero-trust-security-architecture.md",
        "ADR-007-event-driven-architecture.md",
    ])
    def test_adr_consequences_has_both_aspects(self, adr_file):
        """Verify Consequences section includes positive and negative aspects"""
        content = self._get_adr_content(adr_file)
        
        # Find Consequences section
        consequences_match = re.search(
            r'##\s+Consequences\s*\n([\s\S]+?)(?=\n##\s+|\Z)',
            content
        )
        
        assert consequences_match, f"{adr_file} missing Consequences section"
        consequences_section = consequences_match.group(1)
        
        # Should have both positive and negative subsections
        has_positive = any(word in consequences_section.lower() 
                          for word in ['positive', 'benefit', 'advantage', 'pro'])
        has_negative = any(word in consequences_section.lower() 
                          for word in ['negative', 'drawback', 'disadvantage', 'con', 'cost'])
        
        assert has_positive and has_negative, \
            f"{adr_file} Consequences section should include both positive and negative aspects"


class TestADRReadmeIntegrity:
    """Test ADR README.md completeness and accuracy"""

    def test_readme_has_overview(self):
        """Verify README has overview section"""
        readme_path = BASE_PATH / "docs" / "adr" / "README.md"
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should explain what ADRs are
        assert "Architecture Decision Record" in content or "ADR" in content, \
            "README should explain what ADRs are"

    def test_readme_has_format_description(self):
        """Verify README describes ADR format"""
        readme_path = BASE_PATH / "docs" / "adr" / "README.md"
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should describe ADR structure
        required_elements = ["Status", "Context", "Decision", "Consequences"]
        found_elements = sum(1 for elem in required_elements if elem in content)
        
        assert found_elements >= 3, \
            "README should describe ADR format with key sections"

    def test_readme_has_index_table(self):
        """Verify README has an index table"""
        readme_path = BASE_PATH / "docs" / "adr" / "README.md"
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have markdown table
        assert '|' in content and re.search(r'\|.*\|.*\|', content), \
            "README should contain an index table"