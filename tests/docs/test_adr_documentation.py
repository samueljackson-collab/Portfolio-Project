"""
Comprehensive tests for Architecture Decision Records (ADRs)

This test suite validates:
- ADR file structure and required sections
- Metadata consistency (status, dates, categories)
- Code block syntax validation
- Internal link integrity
- Cross-references between ADRs
- Markdown formatting
- Content quality checks
"""

import re
import pytest
from pathlib import Path
from typing import List, Dict, Set

BASE_PATH = Path(__file__).parent.parent.parent


class TestADRStructure:
    """Test ADR file structure and required sections"""

    @pytest.fixture
    def adr_files(self) -> List[Path]:
        """Get all ADR files"""
        adr_dir = BASE_PATH / "docs/adr"
        return sorted(adr_dir.glob("ADR-*.md"))

    @pytest.fixture
    def adr_readme(self) -> Path:
        """Get ADR README"""
        return BASE_PATH / "docs/adr/README.md"

    def test_adr_files_exist(self, adr_files):
        """Test that ADR files exist"""
        assert len(adr_files) >= 4, "Expected at least 4 ADR files"

        expected_adrs = [
            "ADR-004-multi-layer-caching-strategy.md",
            "ADR-005-comprehensive-observability-strategy.md",
            "ADR-006-zero-trust-security-architecture.md",
            "ADR-007-event-driven-architecture.md",
        ]

        adr_names = [f.name for f in adr_files]
        for expected in expected_adrs:
            assert expected in adr_names, f"Missing ADR: {expected}"

    def test_adr_readme_exists(self, adr_readme):
        """Test that ADR README exists"""
        assert adr_readme.exists(), "ADR README.md not found"

    def test_adr_has_required_sections(self, adr_files):
        """Test that each ADR has all required sections"""
        required_sections = [
            "# ADR-",  # Title
            "## Status",
            "## Context",
            "## Decision",
        ]

        for adr_file in adr_files:
            with open(adr_file) as f:
                content = f.read()

            for section in required_sections:
                assert section in content, f"{adr_file.name} missing section: {section}"

    def test_adr_status_valid(self, adr_files):
        """Test that ADR status is one of the allowed values"""
        valid_statuses = ["Accepted", "Proposed", "Deprecated", "Superseded"]
        status_pattern = re.compile(r"## Status\s+(\w+)")

        for adr_file in adr_files:
            with open(adr_file) as f:
                content = f.read()

            match = status_pattern.search(content)
            assert match, f"{adr_file.name} has no status"

            status = match.group(1)
            assert (
                status in valid_statuses
            ), f"{adr_file.name} has invalid status: {status}"

    def test_adr_title_format(self, adr_files):
        """Test that ADR titles follow the format: # ADR-NNN: Title"""
        title_pattern = re.compile(r"^# ADR-\d{3,4}: .+$", re.MULTILINE)

        for adr_file in adr_files:
            with open(adr_file) as f:
                content = f.read()

            match = title_pattern.search(content)
            assert match, f"{adr_file.name} has invalid title format"

    def test_adr_numbering_matches_filename(self, adr_files):
        """Test that ADR number in title matches filename"""
        for adr_file in adr_files:
            # Extract number from filename
            filename_match = re.search(r"ADR-(\d{3,4})", adr_file.name)
            assert filename_match, f"Invalid filename format: {adr_file.name}"
            filename_num = filename_match.group(1)

            # Extract number from title
            with open(adr_file) as f:
                first_line = f.readline()

            title_match = re.search(r"# ADR-(\d{3,4})", first_line)
            assert title_match, f"{adr_file.name} has no ADR number in title"
            title_num = title_match.group(1)

            assert (
                filename_num == title_num
            ), f"ADR number mismatch in {adr_file.name}: filename={filename_num}, title={title_num}"

    def test_adr_minimum_content_length(self, adr_files):
        """Test that ADRs have substantial content"""
        min_length = 1000  # At least 1000 characters

        for adr_file in adr_files:
            with open(adr_file) as f:
                content = f.read()

            assert (
                len(content) >= min_length
            ), f"{adr_file.name} is too short ({len(content)} chars, expected >= {min_length})"

    def test_adr_has_code_examples(self, adr_files):
        """Test that ADRs contain code examples"""
        for adr_file in adr_files:
            with open(adr_file) as f:
                content = f.read()

            # Count code blocks
            code_block_count = content.count("```")
            assert (
                code_block_count >= 4
            ), f"{adr_file.name} should have at least 2 code blocks (found {code_block_count // 2})"


class TestADRCodeBlocks:
    """Test code blocks in ADRs for syntax and consistency"""

    @pytest.fixture
    def adr_files(self) -> List[Path]:
        """Get all ADR files"""
        adr_dir = BASE_PATH / "docs/adr"
        return sorted(adr_dir.glob("ADR-*.md"))

    def test_code_blocks_are_closed(self, adr_files):
        """Test that all code blocks are properly closed"""
        for adr_file in adr_files:
            with open(adr_file) as f:
                content = f.read()

            # Count opening and closing backticks
            backtick_count = content.count("```")
            assert (
                backtick_count % 2 == 0
            ), f"{adr_file.name} has unclosed code blocks ({backtick_count} backticks)"

    def test_code_blocks_have_language(self, adr_files):
        """Test that code blocks specify a language"""
        code_block_pattern = re.compile(r"```(\w+)?")

        for adr_file in adr_files:
            with open(adr_file) as f:
                content = f.read()

            matches = code_block_pattern.findall(content)
            opening_blocks = matches[::2]  # Every other match is an opening block

            for i, lang in enumerate(opening_blocks):
                assert (
                    lang
                ), f"{adr_file.name} has code block #{i+1} without language specification"

    def test_typescript_code_syntax(self, adr_files):
        """Test TypeScript code blocks for basic syntax errors"""
        ts_pattern = re.compile(r"```typescript\n(.*?)```", re.DOTALL)

        # Basic syntax checks
        checks = [
            (r"\binterface\s+\w+\s*{", "interface declaration"),
            (r"\bclass\s+\w+", "class declaration"),
            (r"\bfunction\s+\w+\s*\(", "function declaration"),
            (r"\basync\s+", "async keyword usage"),
        ]

        for adr_file in adr_files:
            with open(adr_file) as f:
                content = f.read()

            ts_blocks = ts_pattern.findall(content)
            if not ts_blocks:
                continue

            # Check that TypeScript blocks have proper structure
            for block in ts_blocks:
                # Should have at least some keywords
                has_keywords = any(
                    keyword in block
                    for keyword in [
                        "const",
                        "let",
                        "var",
                        "function",
                        "class",
                        "interface",
                        "type",
                        "async",
                        "await",
                        "return",
                    ]
                )
                assert (
                    has_keywords
                ), f"{adr_file.name} has TypeScript block without proper keywords"

    def test_bash_code_syntax(self, adr_files):
        """Test Bash code blocks for basic syntax"""
        bash_pattern = re.compile(r"```(?:bash|shell)\n(.*?)```", re.DOTALL)

        for adr_file in adr_files:
            with open(adr_file) as f:
                content = f.read()

            bash_blocks = bash_pattern.findall(content)
            if not bash_blocks:
                continue

            for block in bash_blocks:
                # Skip comment-only blocks
                if all(
                    line.strip().startswith("#") or not line.strip()
                    for line in block.split("\n")
                ):
                    continue

                # Should have at least some commands
                has_commands = any(
                    keyword in block
                    for keyword in [
                        "kubectl",
                        "aws",
                        "curl",
                        "echo",
                        "export",
                        "if",
                        "for",
                        "while",
                        "$",
                    ]
                )
                assert (
                    has_commands
                ), f"{adr_file.name} has Bash block without proper commands"

    def test_yaml_code_syntax(self, adr_files):
        """Test YAML code blocks for basic structure"""
        yaml_pattern = re.compile(r"```yaml\n(.*?)```", re.DOTALL)

        for adr_file in adr_files:
            with open(adr_file) as f:
                content = f.read()

            yaml_blocks = yaml_pattern.findall(content)
            if not yaml_blocks:
                continue

            for block in yaml_blocks:
                # Should have colon (key-value pairs)
                assert (
                    ":" in block
                ), f"{adr_file.name} has YAML block without key-value pairs"


class TestADRREADME:
    """Test ADR README.md for completeness and accuracy"""

    @pytest.fixture
    def readme(self) -> Path:
        """Get ADR README"""
        return BASE_PATH / "docs/adr/README.md"

    @pytest.fixture
    def adr_files(self) -> List[Path]:
        """Get all ADR files"""
        adr_dir = BASE_PATH / "docs/adr"
        return sorted(adr_dir.glob("ADR-*.md"))

    def test_readme_exists(self, readme):
        """Test that README exists"""
        assert readme.exists(), "ADR README.md not found"

    def test_readme_has_required_sections(self, readme):
        """Test that README has all required sections"""
        required_sections = [
            "# Architecture Decision Records",
            "## About ADRs",
            "## ADR Format",
            "## ADR Index",
        ]

        with open(readme) as f:
            content = f.read()

        for section in required_sections:
            assert section in content, f"README missing section: {section}"

    def test_readme_lists_all_adrs(self, readme, adr_files):
        """Test that README lists all ADR files"""
        with open(readme) as f:
            content = f.read()

        for adr_file in adr_files:
            adr_name = adr_file.stem
            # Should be referenced in the README
            assert (
                adr_name in content or adr_file.name in content
            ), f"README does not list {adr_file.name}"

    def test_readme_links_are_valid(self, readme):
        """Test that all markdown links in README are valid"""
        with open(readme) as f:
            content = f.read()

        # Find all markdown links: [text](path)
        link_pattern = re.compile(r"\[([^\]]+)\]\(([^\)]+)\)")
        matches = link_pattern.findall(content)

        for text, link in matches:
            # Skip external links
            if link.startswith("http://") or link.startswith("https://"):
                continue

            # Skip anchors
            if link.startswith("#"):
                continue

            # Check relative file links
            link_path = readme.parent / link.split("#")[0]
            assert link_path.exists(), f"README has broken link: [{text}]({link})"

    def test_readme_has_table(self, readme):
        """Test that README has ADR index table"""
        with open(readme) as f:
            content = f.read()

        # Check for markdown table markers
        assert "|" in content, "README should contain a table"
        assert (
            "|-" in content or "|--" in content
        ), "README should contain table header separator"


class TestADRCrossReferences:
    """Test cross-references between ADRs"""

    @pytest.fixture
    def adr_files(self) -> List[Path]:
        """Get all ADR files"""
        adr_dir = BASE_PATH / "docs/adr"
        return sorted(adr_dir.glob("ADR-*.md"))

    def test_adr_related_section_links_valid(self, adr_files):
        """Test that 'Related ADRs' section links are valid"""
        for adr_file in adr_files:
            with open(adr_file) as f:
                content = f.read()

            # Check if has Related ADRs section
            if "## Related ADRs" not in content:
                continue

            # Extract section content
            related_section = content.split("## Related ADRs")[1].split("##")[0]

            # Find ADR references
            adr_refs = re.findall(r"ADR-\d{3,4}", related_section)

            for ref in adr_refs:
                # Check if referenced ADR exists
                ref_file = adr_file.parent / f"{ref}*.md"
                matching_files = list(adr_file.parent.glob(f"{ref}*.md"))
                assert (
                    len(matching_files) > 0
                ), f"{adr_file.name} references non-existent {ref}"


class TestADRContentQuality:
    """Test ADR content quality and completeness"""

    @pytest.fixture
    def adr_files(self) -> List[Path]:
        """Get all ADR files"""
        adr_dir = BASE_PATH / "docs/adr"
        return sorted(adr_dir.glob("ADR-*.md"))

    def test_adr_has_consequences_or_tradeoffs(self, adr_files):
        """Test that ADRs discuss consequences or tradeoffs"""
        keywords = [
            "consequence",
            "trade-off",
            "tradeoff",
            "benefit",
            "drawback",
            "advantage",
            "disadvantage",
            "positive",
            "negative",
        ]

        for adr_file in adr_files:
            with open(adr_file) as f:
                content = f.read().lower()

            has_discussion = any(keyword in content for keyword in keywords)
            assert (
                has_discussion
            ), f"{adr_file.name} should discuss consequences or tradeoffs"

    def test_adr_has_technical_details(self, adr_files):
        """Test that ADRs include technical implementation details"""
        for adr_file in adr_files:
            with open(adr_file) as f:
                content = f.read()

            # Should have code blocks
            code_blocks = content.count("```")
            assert (
                code_blocks >= 4
            ), f"{adr_file.name} should have implementation details with code examples"

    def test_adr_context_is_substantial(self, adr_files):
        """Test that Context section has meaningful content"""
        for adr_file in adr_files:
            with open(adr_file) as f:
                content = f.read()

            # Extract Context section
            if "## Context" not in content:
                continue

            parts = content.split("## Context")[1].split("##")[0]
            context_length = len(parts.strip())

            assert (
                context_length >= 100
            ), f"{adr_file.name} Context section is too brief ({context_length} chars)"

    def test_adr_decision_is_clear(self, adr_files):
        """Test that Decision section is clear and actionable"""
        for adr_file in adr_files:
            with open(adr_file) as f:
                content = f.read()

            # Extract Decision section
            if "## Decision" not in content:
                continue

            parts = content.split("## Decision")[1].split("##")[0]
            decision_length = len(parts.strip())

            assert (
                decision_length >= 100
            ), f"{adr_file.name} Decision section is too brief ({decision_length} chars)"

    def test_adr_has_date_or_timeline(self, adr_files):
        """Test that ADRs include date information"""
        date_patterns = [
            r"\d{4}",  # Year
            r"(January|February|March|April|May|June|July|August|September|October|November|December)",
            r"\d{1,2}/\d{1,2}/\d{4}",  # Date format
        ]

        for adr_file in adr_files:
            with open(adr_file) as f:
                content = f.read()

            has_date = any(re.search(pattern, content) for pattern in date_patterns)
            assert (
                has_date
            ), f"{adr_file.name} should include date or timeline information"


class TestADRSpecificContent:
    """Test specific ADRs for their domain-specific content"""

    def test_adr_004_caching_strategy_content(self):
        """Test ADR-004 Multi-Layer Caching Strategy has expected content"""
        adr_file = BASE_PATH / "docs/adr/ADR-004-multi-layer-caching-strategy.md"
        if not adr_file.exists():
            pytest.skip("ADR-004 not found")

        with open(adr_file) as f:
            content = f.read().lower()

        required_topics = ["cache", "redis", "ttl", "invalidation"]
        for topic in required_topics:
            assert topic in content, f"ADR-004 should discuss {topic}"

    def test_adr_005_observability_content(self):
        """Test ADR-005 Observability Strategy has expected content"""
        adr_file = (
            BASE_PATH / "docs/adr/ADR-005-comprehensive-observability-strategy.md"
        )
        if not adr_file.exists():
            pytest.skip("ADR-005 not found")

        with open(adr_file) as f:
            content = f.read().lower()

        required_topics = [
            "metric",
            "log",
            "trace",
            "monitoring",
            "prometheus",
            "grafana",
        ]
        for topic in required_topics:
            assert topic in content, f"ADR-005 should discuss {topic}"

    def test_adr_006_security_content(self):
        """Test ADR-006 Zero-Trust Security has expected content"""
        adr_file = BASE_PATH / "docs/adr/ADR-006-zero-trust-security-architecture.md"
        if not adr_file.exists():
            pytest.skip("ADR-006 not found")

        with open(adr_file) as f:
            content = f.read().lower()

        required_topics = [
            "security",
            "authentication",
            "authorization",
            "encryption",
            "zero-trust",
        ]
        for topic in required_topics:
            assert topic in content, f"ADR-006 should discuss {topic}"

    def test_adr_007_event_driven_content(self):
        """Test ADR-007 Event-Driven Architecture has expected content"""
        adr_file = BASE_PATH / "docs/adr/ADR-007-event-driven-architecture.md"
        if not adr_file.exists():
            pytest.skip("ADR-007 not found")

        with open(adr_file) as f:
            content = f.read().lower()

        required_topics = ["event", "message", "queue", "async", "sns", "sqs"]
        for topic in required_topics:
            assert topic in content, f"ADR-007 should discuss {topic}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
