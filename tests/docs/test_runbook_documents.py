"""
Comprehensive tests for Production Runbooks

This test suite validates:
- Runbook file existence and structure
- Required sections presence
- Command syntax validity
- Internal link integrity
- Consistency across runbooks
- Alert definitions
- Step-by-step procedures
"""

import pytest
import re
import yaml
from pathlib import Path
from typing import List, Dict

BASE_PATH = Path(__file__).parent.parent.parent


class TestRunbookFileExistence:
    """Test that runbook files exist and are accessible"""

    def test_runbook_directory_exists(self):
        """Verify the runbooks directory exists"""
        runbook_dir = BASE_PATH / "docs" / "runbooks"
        assert runbook_dir.exists(), "Runbooks directory does not exist"
        assert runbook_dir.is_dir(), "Runbooks path is not a directory"

    def test_runbook_readme_exists(self):
        """Verify runbooks README exists"""
        readme = BASE_PATH / "docs" / "runbooks" / "README.md"
        assert readme.exists(), "Runbooks README.md does not exist"
        assert readme.is_file(), "Runbooks README.md is not a file"

    @pytest.mark.parametrize("runbook_file", [
        "incident-response-framework.md",
        "runbook-database-connection-pool-exhaustion.md",
        "runbook-disaster-recovery.md",
        "runbook-high-cpu-usage.md",
        "runbook-high-error-rate.md",
        "runbook-security-incident-response.md",
    ])
    def test_runbook_files_exist(self, runbook_file):
        """Verify individual runbook files exist"""
        file_path = BASE_PATH / "docs" / "runbooks" / runbook_file
        assert file_path.exists(), f"Runbook file {runbook_file} does not exist"
        assert file_path.is_file(), f"{runbook_file} is not a file"


class TestRunbookStructure:
    """Test runbook document structure and required sections"""

    def _get_runbook_content(self, filename: str) -> str:
        """Helper to read runbook file content"""
        file_path = BASE_PATH / "docs" / "runbooks" / filename
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _extract_headers(self, content: str) -> List[str]:
        """Extract all markdown headers from content"""
        return re.findall(r'^#{1,6}\s+(.+)$', content, re.MULTILINE)

    @pytest.mark.parametrize("runbook_file", [
        "runbook-high-cpu-usage.md",
        "runbook-database-connection-pool-exhaustion.md",
        "runbook-high-error-rate.md",
        "runbook-disaster-recovery.md",
        "runbook-security-incident-response.md",
    ])
    def test_runbook_has_title(self, runbook_file):
        """Verify runbook has a title (H1 header)"""
        content = self._get_runbook_content(runbook_file)
        h1_headers = re.findall(r'^#\s+(.+)$', content, re.MULTILINE)
        assert len(h1_headers) > 0, f"{runbook_file} does not have a title (H1 header)"

    @pytest.mark.parametrize("runbook_file,required_sections", [
        ("runbook-high-cpu-usage.md", ["Overview", "Symptoms", "Detection", "Investigation"]),
        ("runbook-database-connection-pool-exhaustion.md", ["Overview", "Symptoms", "Detection"]),
        ("runbook-high-error-rate.md", ["Overview", "Symptoms", "Detection"]),
        ("runbook-disaster-recovery.md", ["Overview", "Prerequisites", "Recovery"]),
        ("runbook-security-incident-response.md", ["Overview", "Detection", "Response"]),
        ("incident-response-framework.md", ["Overview", "Lifecycle", "Roles"]),
    ])
    def test_runbook_has_required_sections(self, runbook_file, required_sections):
        """Verify runbook contains required sections"""
        content = self._get_runbook_content(runbook_file)
        headers = self._extract_headers(content)
        
        for section in required_sections:
            assert any(section in header for header in headers), \
                f"{runbook_file} is missing required section: {section}"

    @pytest.mark.parametrize("runbook_file", [
        "runbook-high-cpu-usage.md",
        "runbook-database-connection-pool-exhaustion.md",
        "runbook-high-error-rate.md",
    ])
    def test_runbook_has_overview_with_severity(self, runbook_file):
        """Verify runbook Overview includes severity information"""
        content = self._get_runbook_content(runbook_file)
        
        # Should have Overview section
        assert re.search(r'##\s+Overview', content), f"{runbook_file} missing Overview header"
        
        # Should mention severity
        overview_match = re.search(
            r'##\s+Overview\s*\n([\s\S]+?)(?=\n##\s+|\Z)',
            content
        )
        
        if overview_match:
            overview_section = overview_match.group(1)
            has_severity = bool(re.search(r'severity|priority|P\d|sev\d', overview_section, re.IGNORECASE))
            assert has_severity, f"{runbook_file} Overview should include severity information"

    @pytest.mark.parametrize("runbook_file", [
        "runbook-high-cpu-usage.md",
        "runbook-database-connection-pool-exhaustion.md",
        "runbook-high-error-rate.md",
        "runbook-disaster-recovery.md",
        "runbook-security-incident-response.md",
    ])
    def test_runbook_has_substantial_content(self, runbook_file):
        """Verify runbook has substantial content"""
        content = self._get_runbook_content(runbook_file)
        
        # Remove code blocks
        content_no_code = re.sub(r'```[\s\S]*?```', '', content)
        
        # Count words
        words = content_no_code.split()
        assert len(words) > 200, f"{runbook_file} has insufficient content (< 200 words)"


class TestRunbookCommands:
    """Test command blocks in runbooks"""

    def _get_runbook_content(self, filename: str) -> str:
        """Helper to read runbook file content"""
        file_path = BASE_PATH / "docs" / "runbooks" / filename
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """Extract code blocks with their language identifiers"""
        pattern = r'```(\w*)\n([\s\S]*?)```'
        matches = re.findall(pattern, content)
        return [{'language': lang, 'code': code} for lang, code in matches]

    @pytest.mark.parametrize("runbook_file", [
        "runbook-high-cpu-usage.md",
        "runbook-database-connection-pool-exhaustion.md",
        "runbook-high-error-rate.md",
        "runbook-disaster-recovery.md",
        "runbook-security-incident-response.md",
    ])
    def test_runbook_has_code_blocks(self, runbook_file):
        """Verify runbook contains code blocks with commands"""
        content = self._get_runbook_content(runbook_file)
        code_blocks = self._extract_code_blocks(content)
        
        assert len(code_blocks) > 0, f"{runbook_file} should contain code blocks with commands"

    @pytest.mark.parametrize("runbook_file", [
        "runbook-high-cpu-usage.md",
        "runbook-database-connection-pool-exhaustion.md",
        "runbook-high-error-rate.md",
    ])
    def test_runbook_bash_commands_have_comments(self, runbook_file):
        """Verify bash commands include helpful comments"""
        content = self._get_runbook_content(runbook_file)
        code_blocks = self._extract_code_blocks(content)
        
        bash_blocks = [b for b in code_blocks if b['language'] in ['bash', 'sh', 'shell']]
        
        if bash_blocks:
            blocks_with_comments = [b for b in bash_blocks if '#' in b['code']]
            comment_ratio = len(blocks_with_comments) / len(bash_blocks)
            
            assert comment_ratio >= 0.5, \
                f"{runbook_file} should have comments in at least 50% of bash blocks"

    @pytest.mark.parametrize("runbook_file", [
        "runbook-high-cpu-usage.md",
        "runbook-database-connection-pool-exhaustion.md",
    ])
    def test_runbook_kubectl_commands_safe(self, runbook_file):
        """Verify kubectl commands avoid dangerous operations"""
        content = self._get_runbook_content(runbook_file)
        code_blocks = self._extract_code_blocks(content)
        
        bash_blocks = [b for b in code_blocks if b['language'] in ['bash', 'sh', 'shell', '']]
        
        dangerous_patterns = [
            r'kubectl\s+delete\s+namespace',
            r'kubectl\s+delete\s+.*\s+--all',
            r'rm\s+-rf\s+/',
        ]
        
        for block in bash_blocks:
            for pattern in dangerous_patterns:
                assert not re.search(pattern, block['code']), \
                    f"{runbook_file} contains dangerous command: {pattern}"

    @pytest.mark.parametrize("runbook_file", [
        "runbook-high-cpu-usage.md",
    ])
    def test_runbook_yaml_alerts_valid(self, runbook_file):
        """Verify YAML alert definitions are syntactically valid"""
        content = self._get_runbook_content(runbook_file)
        code_blocks = self._extract_code_blocks(content)
        
        yaml_blocks = [b for b in code_blocks if b['language'] in ['yaml', 'yml']]
        
        for i, block in enumerate(yaml_blocks):
            try:
                parsed = yaml.safe_load(block['code'])
                # Alert definitions should be dicts or lists
                assert isinstance(parsed, (dict, list)), \
                    f"{runbook_file} YAML block {i+1} should be dict or list"
            except yaml.YAMLError as e:
                pytest.fail(f"{runbook_file} has invalid YAML in block {i+1}: {str(e)}")


class TestRunbookLinks:
    """Test internal links in runbook documents"""

    def _get_runbook_content(self, filename: str) -> str:
        """Helper to read runbook file content"""
        file_path = BASE_PATH / "docs" / "runbooks" / filename
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _extract_markdown_links(self, content: str) -> List[Dict[str, str]]:
        """Extract markdown links [text](url)"""
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(pattern, content)
        return [{'text': text, 'url': url} for text, url in matches]

    @pytest.mark.parametrize("runbook_file", [
        "runbook-high-cpu-usage.md",
        "runbook-database-connection-pool-exhaustion.md",
        "runbook-high-error-rate.md",
        "runbook-disaster-recovery.md",
        "runbook-security-incident-response.md",
    ])
    def test_runbook_internal_links_valid(self, runbook_file):
        """Verify internal links point to existing files"""
        content = self._get_runbook_content(runbook_file)
        links = self._extract_markdown_links(content)
        
        runbook_dir = BASE_PATH / "docs" / "runbooks"
        
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
                url_path = url.split('#')[0]
                
                # Resolve relative path
                if url_path.startswith('../'):
                    target = (runbook_dir / url_path).resolve()
                elif url_path.startswith('./'):
                    target = (runbook_dir / url_path[2:]).resolve()
                else:
                    target = (runbook_dir / url_path).resolve()
                
                assert target.exists(), \
                    f"{runbook_file} contains broken link: {url} -> {target}"

    def test_runbook_readme_links_valid(self):
        """Verify README links point to existing runbook files"""
        readme_path = BASE_PATH / "docs" / "runbooks" / "README.md"
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        links = self._extract_markdown_links(content)
        runbook_dir = BASE_PATH / "docs" / "runbooks"
        
        for link in links:
            url = link['url']
            
            # Only check runbook links
            if url.endswith('.md') and not url.startswith('http'):
                url_path = url.split('#')[0]
                target = (runbook_dir / url_path.lstrip('./')).resolve()
                
                assert target.exists(), \
                    f"README contains broken link: {url} -> {target}"


class TestRunbookConsistency:
    """Test consistency across runbook documents"""

    def _get_all_runbook_files(self) -> List[Path]:
        """Get all runbook files (excluding README and framework)"""
        runbook_dir = BASE_PATH / "docs" / "runbooks"
        return [f for f in runbook_dir.glob("runbook-*.md")]

    def test_runbook_naming_convention(self):
        """Verify runbook files follow naming convention"""
        runbook_files = self._get_all_runbook_files()
        
        for runbook_file in runbook_files:
            # Should start with 'runbook-' and end with '.md'
            assert runbook_file.name.startswith('runbook-'), \
                f"{runbook_file.name} doesn't follow naming convention"
            
            # Should use hyphens, not underscores
            assert '_' not in runbook_file.name.replace('runbook-', ''), \
                f"{runbook_file.name} should use hyphens, not underscores"

    def test_runbook_readme_index_complete(self):
        """Verify README index includes all runbook files"""
        runbook_files = self._get_all_runbook_files()
        readme_path = BASE_PATH / "docs" / "runbooks" / "README.md"
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        for runbook_file in runbook_files:
            runbook_name = runbook_file.name
            assert runbook_name in readme_content, \
                f"Runbook {runbook_name} is not listed in README index"

    @pytest.mark.parametrize("runbook_file", [
        "runbook-high-cpu-usage.md",
        "runbook-database-connection-pool-exhaustion.md",
        "runbook-high-error-rate.md",
    ])
    def test_runbook_references_related_adrs(self, runbook_file):
        """Verify runbooks reference related ADRs"""
        runbook_path = BASE_PATH / "docs" / "runbooks" / runbook_file
        with open(runbook_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should reference ADRs or have Related section
        has_adr_reference = 'ADR-' in content or 'Architecture Decision' in content
        has_related_section = 'Related' in content or 'See Also' in content
        
        assert has_adr_reference or has_related_section, \
            f"{runbook_file} should reference related ADRs or have Related section"


class TestRunbookProcedures:
    """Test step-by-step procedures in runbooks"""

    def _get_runbook_content(self, filename: str) -> str:
        """Helper to read runbook file content"""
        file_path = BASE_PATH / "docs" / "runbooks" / filename
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @pytest.mark.parametrize("runbook_file", [
        "runbook-high-cpu-usage.md",
        "runbook-database-connection-pool-exhaustion.md",
        "runbook-high-error-rate.md",
    ])
    def test_runbook_has_investigation_steps(self, runbook_file):
        """Verify runbook contains numbered or structured investigation steps"""
        content = self._get_runbook_content(runbook_file)
        
        # Should have investigation section
        has_investigation = bool(re.search(r'investigation|diagnos|troubleshoot', content, re.IGNORECASE))
        assert has_investigation, f"{runbook_file} should have investigation steps"
        
        # Should have numbered steps or structured headings
        has_numbers = bool(re.search(r'###\s+\d+\.', content))  # ### 1. Step
        has_ordered_list = bool(re.search(r'^\d+\.\s+', content, re.MULTILINE))  # 1. Step
        
        assert has_numbers or has_ordered_list, \
            f"{runbook_file} should have numbered steps"

    @pytest.mark.parametrize("runbook_file", [
        "runbook-high-cpu-usage.md",
        "runbook-database-connection-pool-exhaustion.md",
        "runbook-high-error-rate.md",
    ])
    def test_runbook_has_mitigation_section(self, runbook_file):
        """Verify runbook includes mitigation strategies"""
        content = self._get_runbook_content(runbook_file)
        
        mitigation_keywords = ['mitigation', 'resolution', 'fix', 'remediation', 'solution']
        has_mitigation = any(keyword in content.lower() for keyword in mitigation_keywords)
        
        assert has_mitigation, f"{runbook_file} should include mitigation/resolution section"

    @pytest.mark.parametrize("runbook_file", [
        "runbook-high-cpu-usage.md",
        "runbook-database-connection-pool-exhaustion.md",
        "runbook-disaster-recovery.md",
    ])
    def test_runbook_includes_time_estimates(self, runbook_file):
        """Verify runbook includes time estimates for steps"""
        content = self._get_runbook_content(runbook_file)
        
        # Look for time estimates (minutes, hours)
        time_patterns = [
            r'\d+\s*(?:minute|min)s?',
            r'\d+\s*(?:hour|hr)s?',
            r'\d+-\d+\s*(?:minute|min)s?',
        ]
        
        has_time_estimates = any(re.search(pattern, content, re.IGNORECASE) 
                                 for pattern in time_patterns)
        
        assert has_time_estimates, \
            f"{runbook_file} should include time estimates for procedures"


class TestIncidentResponseFramework:
    """Test the incident response framework document"""

    def test_framework_has_severity_levels(self):
        """Verify framework defines severity levels"""
        framework_path = BASE_PATH / "docs" / "runbooks" / "incident-response-framework.md"
        with open(framework_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should define severity levels (P1, P2, etc. or Sev1, Sev2, etc.)
        has_severity = bool(re.search(r'severity|priority', content, re.IGNORECASE))
        assert has_severity, "Framework should define severity levels"
        
        # Should have multiple levels
        severity_levels = len(re.findall(r'P\d|Sev\d|Level\s+\d', content, re.IGNORECASE))
        assert severity_levels >= 3, "Framework should define at least 3 severity levels"

    def test_framework_has_roles(self):
        """Verify framework defines incident response roles"""
        framework_path = BASE_PATH / "docs" / "runbooks" / "incident-response-framework.md"
        with open(framework_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should define roles
        role_keywords = ['commander', 'coordinator', 'lead', 'responder', 'role']
        has_roles = any(keyword in content.lower() for keyword in role_keywords)
        
        assert has_roles, "Framework should define incident response roles"

    def test_framework_has_lifecycle(self):
        """Verify framework describes incident lifecycle"""
        framework_path = BASE_PATH / "docs" / "runbooks" / "incident-response-framework.md"
        with open(framework_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should describe lifecycle phases
        lifecycle_keywords = ['detect', 'respond', 'resolve', 'postmortem', 'lifecycle', 'phase']
        has_lifecycle = sum(1 for keyword in lifecycle_keywords if keyword in content.lower())
        
        assert has_lifecycle >= 3, "Framework should describe incident lifecycle phases"


class TestRunbookReadmeIntegrity:
    """Test runbooks README.md completeness"""

    def test_readme_has_overview(self):
        """Verify README has overview section"""
        readme_path = BASE_PATH / "docs" / "runbooks" / "README.md"
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should explain purpose of runbooks
        purpose_keywords = ['purpose', 'overview', 'about', 'runbook']
        has_overview = any(keyword in content.lower() for keyword in purpose_keywords)
        
        assert has_overview, "README should have an overview section"

    def test_readme_has_index(self):
        """Verify README has runbook index"""
        readme_path = BASE_PATH / "docs" / "runbooks" / "README.md"
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have index or list of runbooks
        has_index = 'index' in content.lower() or '- [' in content or '* [' in content
        
        assert has_index, "README should have a runbook index"

    def test_readme_categorizes_runbooks(self):
        """Verify README categorizes runbooks"""
        readme_path = BASE_PATH / "docs" / "runbooks" / "README.md"
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have categories
        category_keywords = ['performance', 'security', 'disaster', 'incident', 'category']
        has_categories = sum(1 for keyword in category_keywords if keyword in content.lower())
        
        assert has_categories >= 2, "README should categorize runbooks"