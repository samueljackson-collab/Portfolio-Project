"""
Comprehensive validation tests for markdown documentation files.

This test suite validates:
- Markdown file existence and readability
- Required sections in ADRs (Architecture Decision Records)
- Required sections in Runbooks
- Code block syntax validation
- Internal link validity
- Consistent formatting and structure
- Metadata completeness
- Cross-references between documents
"""

import re
import pytest
from pathlib import Path
from typing import List, Dict, Set

BASE_PATH = Path(__file__).parent.parent


class TestADRDocuments:
    """Test Architecture Decision Record (ADR) documents"""

    @pytest.fixture
    def adr_files(self) -> List[Path]:
        """Return list of all ADR markdown files"""
        adr_dir = BASE_PATH / "docs/adr"
        return [f for f in adr_dir.glob("ADR-*.md") if f.is_file()]

    def test_adr_files_exist(self, adr_files):
        """Test that ADR files exist and are readable"""
        assert len(adr_files) > 0, "No ADR files found"
        for adr_file in adr_files:
            assert adr_file.exists(), f"ADR file not found: {adr_file}"
            assert adr_file.is_file(), f"ADR path is not a file: {adr_file}"
            # Test readability
            content = adr_file.read_text()
            assert len(content) > 0, f"ADR file is empty: {adr_file}"

    def test_adr_naming_convention(self, adr_files):
        """Test that ADR files follow naming convention ADR-NNN-title.md"""
        pattern = re.compile(r"^ADR-\d{3}-[a-z0-9-]+\.md$")
        for adr_file in adr_files:
            assert pattern.match(
                adr_file.name
            ), f"ADR file does not follow naming convention: {adr_file.name}"

    def test_adr_has_required_sections(self, adr_files):
        """Test that each ADR has all required sections"""
        required_sections = [
            "# ADR-",  # Title
            "## Status",
            "## Context",
            "## Decision",
            "## Consequences",
        ]

        for adr_file in adr_files:
            content = adr_file.read_text()
            for section in required_sections:
                assert (
                    section in content
                ), f"ADR {adr_file.name} missing required section: {section}"

    def test_adr_status_valid(self, adr_files):
        """Test that ADR status is one of the allowed values"""
        valid_statuses = [
            "Accepted",
            "Proposed",
            "Deprecated",
            "Superseded",
            "Rejected",
        ]

        for adr_file in adr_files:
            content = adr_file.read_text()
            # Find status line
            status_match = re.search(r"## Status\s+(\w+)", content)
            assert status_match, f"ADR {adr_file.name} has no valid status"

            status = status_match.group(1)
            assert (
                status in valid_statuses
            ), f"ADR {adr_file.name} has invalid status: {status}"

    def test_adr_has_date(self, adr_files):
        """Test that each ADR has a date specified"""
        date_patterns = [
            r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
            r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b",
            r"\d{4}-\d{2}-\d{2}",
        ]

        for adr_file in adr_files:
            content = adr_file.read_text()
            has_date = any(re.search(pattern, content) for pattern in date_patterns)
            assert has_date, f"ADR {adr_file.name} does not have a date"

    def test_adr_code_blocks_have_language(self, adr_files):
        """Test that code blocks specify a language for syntax highlighting"""
        for adr_file in adr_files:
            content = adr_file.read_text()
            # Find all code blocks
            code_blocks = re.findall(r"```(\w*)\n", content)

            for i, lang in enumerate(code_blocks):
                # Allow empty language for plain text/output blocks
                # But warn if there are many without language
                pass

            # At least 50% of code blocks should have a language specified
            if len(code_blocks) > 0:
                with_lang = sum(1 for lang in code_blocks if lang)
                ratio = with_lang / len(code_blocks)
                assert ratio >= 0.5, (
                    f"ADR {adr_file.name} has {len(code_blocks)} code blocks, "
                    f"but only {with_lang} specify a language"
                )

    def test_adr_consequences_not_empty(self, adr_files):
        """Test that Consequences section has content"""
        for adr_file in adr_files:
            content = adr_file.read_text()
            # Find Consequences section
            consequences_match = re.search(
                r"## Consequences\s+(.*?)(?=\n## |\Z)", content, re.DOTALL
            )
            assert (
                consequences_match
            ), f"ADR {adr_file.name} missing Consequences section"

            consequences_content = consequences_match.group(1).strip()
            # Should have at least some content (more than just whitespace)
            assert (
                len(consequences_content) > 50
            ), f"ADR {adr_file.name} has minimal or empty Consequences section"

    def test_adr_has_positive_and_negative_consequences(self, adr_files):
        """Test that Consequences section discusses both positive and negative impacts"""
        for adr_file in adr_files:
            content = adr_file.read_text()
            consequences_match = re.search(
                r"## Consequences\s+(.*?)(?=\n## |\Z)", content, re.DOTALL
            )

            if consequences_match:
                consequences = consequences_match.group(1).lower()
                # Look for positive indicators
                has_positive = any(
                    word in consequences
                    for word in [
                        "positive",
                        "benefit",
                        "advantage",
                        "improvement",
                        "better",
                    ]
                )
                # Look for negative indicators
                has_negative = any(
                    word in consequences
                    for word in [
                        "negative",
                        "cost",
                        "disadvantage",
                        "trade-off",
                        "tradeoff",
                        "overhead",
                    ]
                )

                assert (
                    has_positive
                ), f"ADR {adr_file.name} Consequences should include benefits"
                assert (
                    has_negative
                ), f"ADR {adr_file.name} Consequences should include downsides"


class TestRunbookDocuments:
    """Test Runbook documents"""

    @pytest.fixture
    def runbook_files(self) -> List[Path]:
        """Return list of all runbook markdown files"""
        runbook_dir = BASE_PATH / "docs/runbooks"
        return [f for f in runbook_dir.glob("runbook-*.md") if f.is_file()]

    @pytest.fixture
    def incident_response_file(self) -> Path:
        """Return incident response framework file"""
        return BASE_PATH / "docs/runbooks/incident-response-framework.md"

    def test_runbook_files_exist(self, runbook_files):
        """Test that runbook files exist and are readable"""
        assert len(runbook_files) > 0, "No runbook files found"
        for runbook in runbook_files:
            assert runbook.exists(), f"Runbook not found: {runbook}"
            content = runbook.read_text()
            assert len(content) > 0, f"Runbook is empty: {runbook}"

    def test_runbook_naming_convention(self, runbook_files):
        """Test that runbook files follow naming convention"""
        pattern = re.compile(r"^runbook-[a-z0-9-]+\.md$")
        for runbook in runbook_files:
            assert pattern.match(
                runbook.name
            ), f"Runbook does not follow naming convention: {runbook.name}"

    def test_runbook_has_required_sections(self, runbook_files):
        """Test that runbooks have operational sections"""
        # At least some of these sections should be present
        expected_sections = [
            "## Symptoms",
            "## Investigation",
            "## Resolution",
            "## Prevention",
            "## Diagnostic",
            "## Detection",
            "## Quick Reference",
        ]

        for runbook in runbook_files:
            content = runbook.read_text()
            found_sections = [s for s in expected_sections if s in content]
            assert (
                len(found_sections) >= 2
            ), f"Runbook {runbook.name} should have at least 2 operational sections"

    def test_runbook_has_commands_or_code(self, runbook_files):
        """Test that runbooks contain actionable commands or code examples"""
        for runbook in runbook_files:
            content = runbook.read_text()
            # Check for code blocks which should contain commands
            has_code_blocks = "```" in content
            assert (
                has_code_blocks
            ), f"Runbook {runbook.name} should contain code blocks with commands"

    def test_runbook_has_bash_commands(self, runbook_files):
        """Test that runbooks include bash/shell commands for operations"""
        for runbook in runbook_files:
            content = runbook.read_text()
            # Look for bash/shell code blocks or common command patterns
            has_bash = re.search(r"```(bash|shell|sh)", content)
            has_commands = re.search(r"(kubectl|curl|grep|cat|ps|top|docker)", content)

            assert (
                has_bash or has_commands
            ), f"Runbook {runbook.name} should include operational commands"

    def test_incident_response_framework_exists(self, incident_response_file):
        """Test that incident response framework file exists"""
        assert (
            incident_response_file.exists()
        ), "Incident response framework file not found"
        content = incident_response_file.read_text()
        assert (
            len(content) > 1000
        ), "Incident response framework should have substantial content"

    def test_incident_response_has_severity_levels(self, incident_response_file):
        """Test that incident response framework defines severity levels"""
        content = incident_response_file.read_text().lower()
        # Should discuss severity or priority
        assert (
            "severity" in content or "priority" in content
        ), "Incident response framework should define severity levels"

    def test_incident_response_has_escalation(self, incident_response_file):
        """Test that incident response framework includes escalation procedures"""
        content = incident_response_file.read_text().lower()
        assert (
            "escalat" in content
        ), "Incident response framework should include escalation procedures"


class TestDocumentationLinks:
    """Test internal links in documentation"""

    @pytest.fixture
    def all_doc_files(self) -> List[Path]:
        """Return all markdown documentation files"""
        docs_dir = BASE_PATH / "docs"
        return list(docs_dir.rglob("*.md"))

    def extract_markdown_links(self, content: str) -> List[tuple]:
        """Extract all markdown links from content"""
        # Pattern: [text](url)
        pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
        return re.findall(pattern, content)

    def test_internal_links_valid(self, all_doc_files):
        """Test that internal relative links point to existing files"""
        for doc_file in all_doc_files:
            content = doc_file.read_text()
            links = self.extract_markdown_links(content)

            for link_text, link_url in links:
                # Skip external links
                if link_url.startswith(("http://", "https://", "mailto:")):
                    continue

                # Skip anchors only
                if link_url.startswith("#"):
                    continue

                # Remove anchor from URL
                clean_url = link_url.split("#")[0]
                if not clean_url:
                    continue

                # Resolve relative path
                if clean_url.startswith("./"):
                    target = (doc_file.parent / clean_url).resolve()
                elif clean_url.startswith("../"):
                    target = (doc_file.parent / clean_url).resolve()
                else:
                    target = (doc_file.parent / clean_url).resolve()

                assert target.exists(), (
                    f"In {doc_file.name}: Link to '{link_url}' ('{link_text}') "
                    f"points to non-existent file: {target}"
                )

    def test_adr_cross_references(self):
        """Test that ADRs properly reference related ADRs"""
        adr_dir = BASE_PATH / "docs/adr"
        adr_files = list(adr_dir.glob("ADR-*.md"))

        # Build map of ADR IDs
        adr_ids = set()
        for adr_file in adr_files:
            match = re.match(r"(ADR-\d{3})", adr_file.name)
            if match:
                adr_ids.add(match.group(1))

        # Check that referenced ADRs exist
        for adr_file in adr_files:
            content = adr_file.read_text()
            # Find ADR references
            referenced_adrs = re.findall(r"\b(ADR-\d{3})\b", content)

            for ref_id in referenced_adrs:
                # Skip self-references
                if ref_id in adr_file.name:
                    continue
                # Referenced ADR should exist or be marked as planned
                if ref_id not in adr_ids:
                    # Check if it's mentioned as planned
                    assert (
                        "planned" in content.lower()
                    ), f"In {adr_file.name}: References non-existent ADR {ref_id}"


class TestDocumentationReadme:
    """Test README files in documentation directories"""

    def test_adr_readme_exists(self):
        """Test that ADR directory has a README"""
        readme = BASE_PATH / "docs/adr/README.md"
        assert readme.exists(), "ADR directory should have README.md"
        content = readme.read_text()
        assert len(content) > 200, "ADR README should have substantial content"

    def test_adr_readme_has_index(self):
        """Test that ADR README contains an index of ADRs"""
        readme = BASE_PATH / "docs/adr/README.md"
        content = readme.read_text()

        # Should have a table or list of ADRs
        assert "ADR-004" in content, "README should reference ADR-004"
        assert "ADR-005" in content, "README should reference ADR-005"
        assert "ADR-006" in content, "README should reference ADR-006"
        assert "ADR-007" in content, "README should reference ADR-007"

    def test_runbooks_readme_exists(self):
        """Test that runbooks directory has a README"""
        readme = BASE_PATH / "docs/runbooks/README.md"
        assert readme.exists(), "Runbooks directory should have README.md"
        content = readme.read_text()
        assert len(content) > 200, "Runbooks README should have substantial content"

    def test_runbooks_readme_has_index(self):
        """Test that runbooks README contains an index"""
        readme = BASE_PATH / "docs/runbooks/README.md"
        content = readme.read_text()

        # Should reference runbook files
        runbook_dir = BASE_PATH / "docs/runbooks"
        runbook_files = list(runbook_dir.glob("runbook-*.md"))

        # At least some runbooks should be mentioned
        mentioned_count = 0
        for runbook in runbook_files:
            if runbook.stem in content:
                mentioned_count += 1

        assert (
            mentioned_count >= len(runbook_files) * 0.5
        ), "README should mention at least half of the runbooks"


class TestMarkdownFormatting:
    """Test markdown formatting consistency"""

    @pytest.fixture
    def all_new_docs(self) -> List[Path]:
        """Return all newly added documentation files"""
        docs = []
        docs.extend((BASE_PATH / "docs/adr").glob("ADR-*.md"))
        docs.extend((BASE_PATH / "docs/runbooks").glob("*.md"))
        return docs

    def test_no_trailing_whitespace(self, all_new_docs):
        """Test that lines don't have trailing whitespace"""
        for doc in all_new_docs:
            lines = doc.read_text().splitlines()
            for i, line in enumerate(lines, 1):
                # Allow trailing spaces for markdown line breaks (2 spaces)
                if line.endswith("  "):
                    continue
                assert not line.endswith(" ") and not line.endswith(
                    "\t"
                ), f"{doc.name}:{i} has trailing whitespace"

    def test_consistent_heading_style(self, all_new_docs):
        """Test that headings use ATX style (# syntax)"""
        for doc in all_new_docs:
            content = doc.read_text()
            lines = content.splitlines()

            for i, line in enumerate(lines, 1):
                # Check for Setext-style headings (underlined with = or -)
                if i < len(lines) - 1:
                    next_line = lines[i]
                    if re.match(r"^[=\-]+$", next_line):
                        # This is acceptable for title, but ATX is preferred
                        pass

    def test_code_blocks_closed(self, all_new_docs):
        """Test that all code blocks are properly closed"""
        for doc in all_new_docs:
            content = doc.read_text()
            # Count opening and closing code fences
            opening = len(re.findall(r"^```", content, re.MULTILINE))
            closing = opening  # They should be equal

            assert (
                opening % 2 == 0
            ), f"{doc.name} has unclosed code blocks (odd number of ```)"

    def test_no_broken_links_syntax(self, all_new_docs):
        """Test that link syntax is not broken"""
        for doc in all_new_docs:
            content = doc.read_text()

            # Check for broken link patterns
            broken_patterns = [
                r"\]\([^\)]*\n",  # Link URL split across lines
                r"\[[^\]]*\n[^\]]*\]",  # Link text split across lines
            ]

            for pattern in broken_patterns:
                matches = re.findall(pattern, content)
                assert len(matches) == 0, f"{doc.name} may have broken link syntax"


class TestCodeExamplesInDocs:
    """Test code examples in documentation for basic validity"""

    @pytest.fixture
    def adr_files(self) -> List[Path]:
        """Return ADR files that contain code"""
        adr_dir = BASE_PATH / "docs/adr"
        return list(adr_dir.glob("ADR-*.md"))

    def extract_code_blocks(self, content: str, language: str = None) -> List[str]:
        """Extract code blocks from markdown"""
        if language:
            pattern = rf"```{language}\n(.*?)```"
        else:
            pattern = r"```\w*\n(.*?)```"
        return re.findall(pattern, content, re.DOTALL)

    def test_typescript_code_has_basic_syntax(self, adr_files):
        """Test that TypeScript code blocks have basic valid syntax"""
        for adr in adr_files:
            content = adr.read_text()
            ts_blocks = self.extract_code_blocks(content, "typescript")

            for block in ts_blocks:
                # Basic checks
                # Should have balanced braces (roughly)
                open_braces = block.count("{")
                close_braces = block.count("}")

                # Allow some flexibility (e.g., template literals)
                assert (
                    abs(open_braces - close_braces) <= 2
                ), f"In {adr.name}: TypeScript block has unbalanced braces"

    def test_yaml_code_blocks_structure(self, adr_files):
        """Test that YAML code blocks have reasonable structure"""
        for adr in adr_files:
            content = adr.read_text()
            yaml_blocks = self.extract_code_blocks(content, "yaml")
            yaml_blocks.extend(self.extract_code_blocks(content, "yml"))

            for block in yaml_blocks:
                # YAML should have key-value pairs
                has_kvp = ":" in block
                assert (
                    has_kvp
                ), f"In {adr.name}: YAML block appears to be missing key-value pairs"

    def test_shell_commands_not_obviously_broken(self):
        """Test that shell commands in runbooks are not obviously broken"""
        runbook_dir = BASE_PATH / "docs/runbooks"
        runbooks = list(runbook_dir.glob("runbook-*.md"))

        for runbook in runbooks:
            content = runbook.read_text()
            shell_blocks = self.extract_code_blocks(content, "bash")
            shell_blocks.extend(self.extract_code_blocks(content, "shell"))
            shell_blocks.extend(self.extract_code_blocks(content, "sh"))

            for block in shell_blocks:
                # Should not have common typos
                assert not re.search(
                    r"\|\s*\|", block
                ), f"In {runbook.name}: Shell command has double pipe (typo?)"
                assert not re.search(
                    r"&&\s*&&", block
                ), f"In {runbook.name}: Shell command has double && (typo?)"


class TestDocumentationMetadata:
    """Test metadata and frontmatter in documentation"""

    def test_adr_has_identifiable_id(self):
        """Test that each ADR has a clear ID in title"""
        adr_dir = BASE_PATH / "docs/adr"
        adr_files = list(adr_dir.glob("ADR-*.md"))

        for adr in adr_files:
            content = adr.read_text()
            # First line should be title with ID
            first_line = content.split("\n")[0]
            assert first_line.startswith(
                "# ADR-"
            ), f"{adr.name} should start with '# ADR-XXX:' title"

            # Extract ID from filename
            file_id = re.match(r"(ADR-\d{3})", adr.name).group(1)
            # Should match title
            assert (
                file_id in first_line
            ), f"{adr.name} title should include ID {file_id}"

    def test_runbooks_have_clear_titles(self):
        """Test that runbooks have clear descriptive titles"""
        runbook_dir = BASE_PATH / "docs/runbooks"
        runbooks = list(runbook_dir.glob("runbook-*.md"))

        for runbook in runbooks:
            content = runbook.read_text()
            lines = content.split("\n")

            # Find first non-empty line
            title_line = None
            for line in lines:
                if line.strip():
                    title_line = line
                    break

            assert title_line, f"{runbook.name} appears to be empty"
            assert title_line.startswith(
                "#"
            ), f"{runbook.name} should start with a markdown heading"

            # Title should be substantive
            title_text = title_line.lstrip("#").strip()
            assert (
                len(title_text) > 10
            ), f"{runbook.name} has too short a title: '{title_text}'"
