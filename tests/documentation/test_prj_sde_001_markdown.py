"""
Comprehensive tests for PRJ-SDE-001 markdown documentation

This test suite validates:
- Documentation completeness
- File structure and organization
- Content quality
- Markdown syntax
- Code block formatting
- Link validity (structure)
- Consistency across documents
"""

import re
from pathlib import Path
import pytest


@pytest.fixture
def docs_dir():
    """Return path to PRJ-SDE-001 documentation directory."""
    return Path("projects/01-sde-devops/PRJ-SDE-001")


@pytest.fixture
def readme(docs_dir):
    """Return path to README.md."""
    return docs_dir / "README.md"


@pytest.fixture
def architecture_diagrams(docs_dir):
    """Return path to ARCHITECTURE-DIAGRAMS.md."""
    return docs_dir / "ARCHITECTURE-DIAGRAMS.md"


@pytest.fixture
def cost_calculator(docs_dir):
    """Return path to COST-CALCULATOR.md."""
    return docs_dir / "COST-CALCULATOR.md"


@pytest.fixture
def demo_script(docs_dir):
    """Return path to DEMO-SCRIPT.md."""
    return docs_dir / "DEMO-SCRIPT.md"


@pytest.fixture
def interview_prep(docs_dir):
    """Return path to INTERVIEW-PREP-SHEET.md."""
    return docs_dir / "INTERVIEW-PREP-SHEET.md"


@pytest.fixture
def one_page_summary(docs_dir):
    """Return path to ONE-PAGE-SUMMARY.md."""
    return docs_dir / "ONE-PAGE-SUMMARY.md"


@pytest.fixture
def presentation_deck(docs_dir):
    """Return path to PRESENTATION-DECK.md."""
    return docs_dir / "PRESENTATION-DECK.md"


@pytest.fixture
def video_script(docs_dir):
    """Return path to VIDEO-WALKTHROUGH-SCRIPT.md."""
    return docs_dir / "VIDEO-WALKTHROUGH-SCRIPT.md"


class TestDocumentationCompleteness:
    """Test that all required documentation files exist."""

    def test_readme_exists(self, readme):
        """Verify README.md exists."""
        assert readme.exists(), "README.md is required"

    def test_architecture_diagrams_exist(self, architecture_diagrams):
        """Verify ARCHITECTURE-DIAGRAMS.md exists."""
        assert architecture_diagrams.exists(), "ARCHITECTURE-DIAGRAMS.md is required"

    def test_cost_calculator_exists(self, cost_calculator):
        """Verify COST-CALCULATOR.md exists."""
        assert cost_calculator.exists(), "COST-CALCULATOR.md is required"

    def test_demo_script_exists(self, demo_script):
        """Verify DEMO-SCRIPT.md exists."""
        assert demo_script.exists(), "DEMO-SCRIPT.md is required"

    def test_interview_prep_exists(self, interview_prep):
        """Verify INTERVIEW-PREP-SHEET.md exists."""
        assert interview_prep.exists(), "INTERVIEW-PREP-SHEET.md is required"

    def test_one_page_summary_exists(self, one_page_summary):
        """Verify ONE-PAGE-SUMMARY.md exists."""
        assert one_page_summary.exists(), "ONE-PAGE-SUMMARY.md is required"

    def test_presentation_deck_exists(self, presentation_deck):
        """Verify PRESENTATION-DECK.md exists."""
        assert presentation_deck.exists(), "PRESENTATION-DECK.md is required"

    def test_video_script_exists(self, video_script):
        """Verify VIDEO-WALKTHROUGH-SCRIPT.md exists."""
        assert video_script.exists(), "VIDEO-WALKTHROUGH-SCRIPT.md is required"


class TestReadmeContent:
    """Test README.md content and structure."""

    def test_readme_not_empty(self, readme):
        """Verify README.md has content."""
        content = readme.read_text()
        assert len(content) > 100, "README should have substantial content"

    def test_readme_has_title(self, readme):
        """Verify README has a title (H1 heading)."""
        content = readme.read_text()
        assert re.search(r'^#\s+.+', content, re.MULTILINE), \
               "README should have an H1 title"

    def test_readme_has_project_description(self, readme):
        """Verify README describes the project."""
        content = readme.read_text()
        assert "project" in content.lower() or "infrastructure" in content.lower(), \
               "README should describe the project"

    def test_readme_has_sections(self, readme):
        """Verify README has multiple sections."""
        content = readme.read_text()
        heading_count = len(re.findall(r'^##\s+', content, re.MULTILINE))
        assert heading_count >= 3, "README should have multiple sections (##)"

    def test_readme_mentions_terraform(self, readme):
        """Verify README mentions Terraform."""
        content = readme.read_text()
        assert "terraform" in content.lower(), "README should mention Terraform"

    def test_readme_has_usage_instructions(self, readme):
        """Verify README includes usage/deployment instructions."""
        content = readme.read_text()
        assert any(keyword in content.lower() 
                  for keyword in ["usage", "deploy", "getting started", "quickstart", "how to"]), \
               "README should include usage instructions"


class TestArchitectureDiagrams:
    """Test ARCHITECTURE-DIAGRAMS.md content."""

    def test_has_mermaid_diagrams(self, architecture_diagrams):
        """Verify document contains Mermaid diagrams."""
        content = architecture_diagrams.read_text()
        assert "```mermaid" in content, "Should contain Mermaid diagram code blocks"

    def test_has_multiple_diagrams(self, architecture_diagrams):
        """Verify document has multiple architecture diagrams."""
        content = architecture_diagrams.read_text()
        diagram_count = content.count("```mermaid")
        assert diagram_count >= 2, f"Should have at least 2 diagrams, found {diagram_count}"

    def test_diagrams_are_closed(self, architecture_diagrams):
        """Verify all Mermaid code blocks are properly closed."""
        content = architecture_diagrams.read_text()
        open_count = content.count("```mermaid")
        # Count closing ``` that follow mermaid blocks
        close_count = len(re.findall(r'```mermaid.*?```', content, re.DOTALL))
        assert open_count == close_count, \
               f"All Mermaid blocks should be closed ({open_count} opened, {close_count} closed)"

    def test_has_diagram_descriptions(self, architecture_diagrams):
        """Verify diagrams have descriptive text."""
        content = architecture_diagrams.read_text()
        # Should have headings for diagram sections
        diagram_heading_count = len(re.findall(r'^##\s+Diagram', content, re.MULTILINE))
        assert diagram_heading_count >= 2, "Should have titled diagram sections"


class TestCostCalculator:
    """Test COST-CALCULATOR.md content."""

    def test_has_cost_information(self, cost_calculator):
        """Verify document contains cost information."""
        content = cost_calculator.read_text()
        assert "$" in content or "cost" in content.lower(), \
               "Should contain cost information"

    def test_has_pricing_breakdown(self, cost_calculator):
        """Verify document breaks down costs by service."""
        content = cost_calculator.read_text()
        # Should mention AWS services
        assert any(service in content.upper() 
                  for service in ["RDS", "EC2", "ECS", "S3", "CLOUDWATCH"]), \
               "Should break down costs by AWS service"

    def test_has_monthly_estimates(self, cost_calculator):
        """Verify document provides monthly cost estimates."""
        content = cost_calculator.read_text()
        assert "month" in content.lower(), "Should provide monthly estimates"

    def test_has_different_environment_costs(self, cost_calculator):
        """Verify document shows costs for different environments."""
        content = cost_calculator.read_text()
        env_count = sum(1 for env in ["dev", "development", "staging", "prod", "production"]
                       if env in content.lower())
        assert env_count >= 2, "Should show costs for multiple environments"


class TestDemoScript:
    """Test DEMO-SCRIPT.md content."""

    def test_has_demo_steps(self, demo_script):
        """Verify document contains demonstration steps."""
        content = demo_script.read_text()
        # Should have numbered or bulleted lists
        assert re.search(r'^\d+\.', content, re.MULTILINE) or \
               re.search(r'^[\-\*]\s+', content, re.MULTILINE), \
               "Should have step-by-step instructions"

    def test_has_code_examples(self, demo_script):
        """Verify document includes code examples."""
        content = demo_script.read_text()
        assert "```" in content, "Should include code blocks for demonstration"

    def test_mentions_terraform_commands(self, demo_script):
        """Verify document includes Terraform commands."""
        content = demo_script.read_text()
        assert any(cmd in content for cmd in ["terraform init", "terraform plan", "terraform apply"]), \
               "Should include Terraform commands"


class TestInterviewPrep:
    """Test INTERVIEW-PREP-SHEET.md content."""

    def test_has_qa_format(self, interview_prep):
        """Verify document uses Q&A format."""
        content = interview_prep.read_text()
        # Should have questions (with ? marks or Q: format)
        assert "?" in content or re.search(r'\bQ:', content), \
               "Should contain interview questions"

    def test_has_technical_questions(self, interview_prep):
        """Verify document covers technical topics."""
        content = interview_prep.read_text()
        technical_terms = ["terraform", "infrastructure", "database", "rds", "aws"]
        found_terms = sum(1 for term in technical_terms if term in content.lower())
        assert found_terms >= 3, "Should cover multiple technical topics"

    def test_has_multiple_sections(self, interview_prep):
        """Verify document is organized into sections."""
        content = interview_prep.read_text()
        section_count = len(re.findall(r'^##\s+', content, re.MULTILINE))
        assert section_count >= 3, "Should have multiple topic sections"


class TestOnePageSummary:
    """Test ONE-PAGE-SUMMARY.md content."""

    def test_is_concise(self, one_page_summary):
        """Verify summary is appropriately concise."""
        content = one_page_summary.read_text()
        word_count = len(content.split())
        # Should be substantial but concise (roughly 1-2 pages when printed)
        assert 200 <= word_count <= 1500, \
               f"One-page summary should be 200-1500 words, got {word_count}"

    def test_has_project_overview(self, one_page_summary):
        """Verify summary includes project overview."""
        content = one_page_summary.read_text()
        assert any(keyword in content.lower() 
                  for keyword in ["overview", "summary", "project", "purpose"]), \
               "Should include project overview"

    def test_highlights_key_technologies(self, one_page_summary):
        """Verify summary highlights key technologies."""
        content = one_page_summary.read_text()
        assert "terraform" in content.lower() or "aws" in content.lower(), \
               "Should highlight key technologies"


class TestPresentationDeck:
    """Test PRESENTATION-DECK.md content."""

    def test_has_slide_structure(self, presentation_deck):
        """Verify document is structured like slides."""
        content = presentation_deck.read_text()
        # Should have multiple major sections (slide titles)
        section_count = len(re.findall(r'^##\s+', content, re.MULTILINE))
        assert section_count >= 5, f"Should have at least 5 slides, found {section_count}"

    def test_has_introduction_slide(self, presentation_deck):
        """Verify deck has introduction/title slide."""
        content = presentation_deck.read_text()
        first_section = content[:500]
        assert any(keyword in first_section.lower() 
                  for keyword in ["introduction", "title", "overview", "agenda"]), \
               "Should have introduction section"

    def test_has_conclusion_slide(self, presentation_deck):
        """Verify deck has conclusion/summary slide."""
        content = presentation_deck.read_text()
        assert any(keyword in content.lower() 
                  for keyword in ["conclusion", "summary", "questions", "thank you"]), \
               "Should have conclusion section"


class TestVideoScript:
    """Test VIDEO-WALKTHROUGH-SCRIPT.md content."""

    def test_has_script_format(self, video_script):
        """Verify document is formatted as a video script."""
        content = video_script.read_text()
        # Should have time markers or scene descriptions
        assert any(indicator in content.lower() 
                  for indicator in ["minute", "scene", "show", "demonstrate", "screen"]), \
               "Should be formatted as a video script"

    def test_has_narration_text(self, video_script):
        """Verify script includes narration text."""
        content = video_script.read_text()
        word_count = len(content.split())
        assert word_count >= 500, "Script should have substantial narration text"

    def test_includes_actions(self, video_script):
        """Verify script includes actions/demonstrations."""
        content = video_script.read_text()
        assert any(action in content.lower() 
                  for action in ["click", "run", "execute", "navigate", "show"]), \
               "Script should include demonstration actions"


class TestMarkdownFormatting:
    """Test markdown formatting consistency."""

    @pytest.mark.parametrize("doc_fixture", [
        "readme", "architecture_diagrams", "cost_calculator", "demo_script",
        "interview_prep", "one_page_summary", "presentation_deck", "video_script"
    ])
    def test_no_trailing_whitespace(self, doc_fixture, request):
        """Verify documents don't have excessive trailing whitespace."""
        doc_path = request.getfixturevalue(doc_fixture)
        content = doc_path.read_text()
        lines = content.split('\n')
        
        lines_with_trailing = [i for i, line in enumerate(lines, 1) 
                              if line.endswith('  ') and not line.endswith('  \n')]
        
        # Allow some trailing spaces (markdown line breaks use 2 spaces)
        assert len(lines_with_trailing) < len(lines) * 0.2, \
               f"Too many lines with trailing whitespace in {doc_path.name}"

    @pytest.mark.parametrize("doc_fixture", [
        "readme", "architecture_diagrams", "demo_script"
    ])
    def test_code_blocks_are_closed(self, doc_fixture, request):
        """Verify all code blocks are properly closed."""
        doc_path = request.getfixturevalue(doc_fixture)
        content = doc_path.read_text()
        
        open_count = content.count("```")
        assert open_count % 2 == 0, \
               f"All code blocks should be closed in {doc_path.name} (found {open_count} backticks)"

    @pytest.mark.parametrize("doc_fixture", [
        "readme", "architecture_diagrams", "cost_calculator", "demo_script"
    ])
    def test_has_proper_heading_hierarchy(self, doc_fixture, request):
        """Verify documents use proper heading hierarchy."""
        doc_path = request.getfixturevalue(doc_fixture)
        content = doc_path.read_text()
        lines = content.split('\n')
        
        # Find all headings
        headings = []
        for line in lines:
            match = re.match(r'^(#{1,6})\s+', line)
            if match:
                level = len(match.group(1))
                headings.append(level)
        
        # Should start with h1
        if headings:
            assert headings[0] == 1, f"Document should start with H1 in {doc_path.name}"


class TestConsistencyAcrossDocuments:
    """Test consistency across all documentation."""

    def test_consistent_project_naming(self, docs_dir):
        """Verify project is named consistently across documents."""
        doc_files = list(docs_dir.glob("*.md"))
        project_names = set()
        
        for doc_file in doc_files:
            content = doc_file.read_text()
            # Look for project identifier patterns
            matches = re.findall(r'PRJ-[A-Z]+-\d+', content)
            project_names.update(matches)
        
        # Should consistently use the same project ID
        assert len(project_names) <= 1 or "PRJ-SDE-001" in project_names, \
               f"Project should be consistently named (found: {project_names})"

    def test_all_docs_mention_terraform(self, docs_dir):
        """Verify all technical docs mention Terraform."""
        technical_docs = [
            "README.md", "ARCHITECTURE-DIAGRAMS.md", "DEMO-SCRIPT.md"
        ]
        
        for doc_name in technical_docs:
            doc_path = docs_dir / doc_name
            if doc_path.exists():
                content = doc_path.read_text()
                assert "terraform" in content.lower(), \
                       f"{doc_name} should mention Terraform"