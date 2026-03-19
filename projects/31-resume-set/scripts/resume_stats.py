#!/usr/bin/env python3
"""
resume_stats.py — Resume Portfolio Statistics Analyzer

Reads all .md files from the professional/resume/ directory and generates
a formatted statistics table including word count, line count, section count,
and top 5 keywords per file.

Usage:
    python3 resume_stats.py

Output:
    Formatted table printed to stdout
    Can be redirected to demo_output/resume_stats.txt
"""

import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path


# Path to resume directory relative to this script
SCRIPT_DIR = Path(__file__).parent.resolve()
RESUME_DIR = (SCRIPT_DIR / "../../professional/resume").resolve()

# Common English stop words to exclude from keyword analysis
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "up", "about", "into", "through", "during",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "do", "does", "did", "will", "would", "could", "should", "may", "might",
    "must", "can", "i", "my", "your", "their", "our", "its", "this", "that",
    "these", "those", "it", "we", "you", "he", "she", "they", "all", "each",
    "more", "most", "other", "some", "such", "no", "not", "only", "same",
    "so", "than", "too", "very", "just", "as", "if", "also", "both", "per",
    "across", "over", "under", "between", "within", "without", "before",
    "after", "while", "when", "where", "which", "who", "how", "what",
    "any", "every", "own", "use", "used", "using", "via", "e", "g",
    "including", "based", "including", "multiple", "custom", "new",
    "full", "key", "high", "low", "real", "open", "single", "main",
    "team", "work", "working", "worked", "role", "roles", "level",
    "provide", "providing", "ensure", "ensuring", "create", "creating",
    "manage", "managing", "build", "building", "deploy", "deploying",
    "implement", "implementing", "configure", "configuring", "design",
    "designing", "develop", "developing", "support", "supporting",
    "maintain", "maintaining", "review", "reviewing", "monitor",
    "monitoring", "perform", "performing", "test", "testing", "run",
    "running", "set", "setting", "allow", "allowing", "reduce", "reducing",
    "improve", "improving", "achieve", "achieving", "demonstrate",
    "demonstrating", "apply", "applying", "follow", "following",
    "include", "including", "add", "adding", "update", "updating",
    "write", "writing", "document", "documenting", "track", "tracking",
    "system", "systems", "service", "services", "process", "processes",
    "data", "access", "end", "end", "plan", "plans", "need", "needs",
    "make", "making", "take", "taking", "give", "giving", "get", "getting",
    "put", "putting", "go", "going", "come", "coming", "know", "knowing",
    "think", "thinking", "see", "seeing", "look", "looking", "want",
    "wanting", "well", "back", "down", "out", "up", "right", "left",
    "next", "first", "last", "long", "little", "own", "old", "right",
    "big", "great", "good", "new", "small", "large", "common", "specific",
    "current", "available", "standard", "required", "complete",
    "comprehensive", "effective", "efficient", "clear", "strong",
    "deep", "production", "enterprise", "internal", "external",
    "project", "projects", "example", "examples", "below", "above",
    "skills", "skill", "experience", "experiences", "ability", "approach",
    "solution", "solutions", "environment", "environments", "platform",
    "platforms", "tool", "tools", "method", "methods", "strategy",
    "techniques", "practice", "practices", "policies", "policy",
    "procedure", "procedures", "documentation", "config", "configuration",
    "configurations", "deployment", "deployments", "integration",
    "integrations", "application", "applications", "operations",
    "operation", "infrastructure", "architecture", "security",
    "performance", "reliability", "scalability", "availability",
    "automation", "monitoring", "alerting", "logging", "backup",
    "recovery", "testing", "validation", "verification",
}


def count_words(text: str) -> int:
    """Count non-empty words in text, excluding Markdown syntax tokens."""
    # Strip Markdown formatting characters
    cleaned = re.sub(r"[#*`_\[\]()>|\\]", " ", text)
    words = [w for w in cleaned.split() if len(w) > 1 and not w.startswith("http")]
    return len(words)


def count_lines(text: str) -> int:
    """Count non-empty lines in text."""
    return sum(1 for line in text.splitlines() if line.strip())


def count_sections(text: str) -> int:
    """Count ## level headers (major sections)."""
    return len(re.findall(r"^##\s+", text, re.MULTILINE))


def extract_top_keywords(text: str, top_n: int = 5) -> list[str]:
    """
    Extract top N meaningful keywords from resume text.

    Strategy:
    1. Strip Markdown syntax
    2. Tokenize into words of 3+ characters
    3. Remove stop words
    4. Count frequency
    5. Return top N by frequency, preserving original casing of most common form
    """
    # Remove URLs
    text_clean = re.sub(r"https?://\S+", " ", text)
    # Remove Markdown link syntax [text](url) — keep the display text
    text_clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text_clean)
    # Remove remaining Markdown formatting
    text_clean = re.sub(r"[#*`_\[\]()>|\\]", " ", text_clean)
    # Remove punctuation except hyphens within words
    text_clean = re.sub(r"[^\w\s\-]", " ", text_clean)

    # Tokenize
    raw_tokens = text_clean.split()

    # Filter: length >= 3, not purely numeric, not a stop word (case-insensitive)
    tokens = []
    for t in raw_tokens:
        t_stripped = t.strip("-").strip()
        if (
            len(t_stripped) >= 3
            and not t_stripped.isdigit()
            and t_stripped.lower() not in STOP_WORDS
            and not re.match(r"^\d+[\.\-]\d+$", t_stripped)  # version numbers
        ):
            tokens.append(t_stripped)

    # Count case-insensitively, but preserve original casing (most frequent form)
    lower_counter: Counter = Counter()
    casing_map: dict = {}

    for token in tokens:
        lower = token.lower()
        lower_counter[lower] += 1
        if lower not in casing_map:
            casing_map[lower] = token
        # Prefer uppercase/mixed-case form (acronyms like AWS, SIEM)
        elif token.isupper() or (token != token.lower() and len(token) <= 6):
            casing_map[lower] = token

    # Return top N keywords in their preferred casing
    top = lower_counter.most_common(top_n)
    return [casing_map[word] for word, _ in top]


def analyze_file(filepath: Path) -> dict:
    """Analyze a single resume file and return stats dict."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    return {
        "filename": filepath.name,
        "words": count_words(content),
        "lines": count_lines(content),
        "sections": count_sections(content),
        "keywords": extract_top_keywords(content, top_n=5),
        "size_bytes": filepath.stat().st_size,
    }


def format_keywords(keywords: list[str]) -> str:
    """Format keyword list as comma-separated string."""
    return ", ".join(keywords)


def print_stats_table(stats: list[dict]) -> None:
    """Print a formatted statistics table to stdout."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("=== Resume Portfolio Statistics ===")
    print(f"Generated: {now}")
    print(f"Resume directory: {RESUME_DIR}")
    print()

    # Column widths
    col_file = 42
    col_words = 7
    col_lines = 7
    col_sections = 9

    # Header
    header = (
        f"{'File':<{col_file}} "
        f"{'Words':>{col_words}} "
        f"{'Lines':>{col_lines}} "
        f"{'Sections':>{col_sections}}"
    )
    separator = "-" * 70
    print(header)
    print(separator)

    total_words = 0
    total_lines = 0
    total_sections = 0

    for s in stats:
        print(
            f"{s['filename']:<{col_file}} "
            f"{s['words']:>{col_words}} "
            f"{s['lines']:>{col_lines}} "
            f"{s['sections']:>{col_sections}}"
        )
        total_words += s["words"]
        total_lines += s["lines"]
        total_sections += s["sections"]

    print(separator)
    print(
        f"{'Total':<{col_file}} "
        f"{total_words:>{col_words}} "
        f"{total_lines:>{col_lines}} "
        f"{total_sections:>{col_sections}}"
    )
    print()

    # Keyword summary by track
    track_map = {
        "Cloud_Engineer_Resume.md": "Cloud Engineer",
        "Cybersecurity_Analyst_Resume.md": "Cybersecurity",
        "Network_Engineer_Resume.md": "Network",
        "QA_Engineer_Resume.md": "QA Engineer",
        "System_Development_Engineer_Resume.md": "SDE",
    }

    resume_stats = [s for s in stats if s["filename"] in track_map]
    if resume_stats:
        print("Top Keywords by Track:")
        for s in resume_stats:
            track = track_map.get(s["filename"], s["filename"])
            kw_str = format_keywords(s["keywords"])
            print(f"  {track:<18} {kw_str}")
        print()

    # Summary
    print("=== Summary ===")
    print(f"Total files analyzed : {len(stats)}")
    print(f"Total word count     : {total_words:,}")
    print(f"Total line count     : {total_lines:,}")
    print(f"Total sections       : {total_sections}")
    avg_words = total_words // len(stats) if stats else 0
    print(f"Average words/file   : {avg_words}")

    # File size summary
    total_bytes = sum(s["size_bytes"] for s in stats)
    print(f"Total size on disk   : {total_bytes / 1024:.1f}K")
    print()


def main() -> None:
    """Main entry point."""
    if not RESUME_DIR.exists():
        print(f"ERROR: Resume directory not found: {RESUME_DIR}")
        print("Run this script from within the projects/31-resume-set/scripts/ directory,")
        print("or ensure the professional/resume/ directory exists at the repo root.")
        raise SystemExit(1)

    md_files = sorted(RESUME_DIR.glob("*.md"))

    if not md_files:
        print(f"WARNING: No .md files found in {RESUME_DIR}")
        raise SystemExit(1)

    stats = []
    for filepath in md_files:
        try:
            file_stats = analyze_file(filepath)
            stats.append(file_stats)
        except (OSError, UnicodeDecodeError) as e:
            print(f"WARNING: Could not read {filepath.name}: {e}")

    print_stats_table(stats)


if __name__ == "__main__":
    main()
