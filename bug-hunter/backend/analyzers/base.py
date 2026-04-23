from __future__ import annotations
import re
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class RawFinding:
    title: str
    description: str
    severity: str
    category: str
    platform: str
    line_number: int | None
    code_snippet: str
    recommendation: str
    cwe_id: str | None
    cvss_score: float | None
    evidence: str


class BaseAnalyzer(ABC):
    platform: str = "generic"

    def analyze(self, code: str, filename: str) -> list[RawFinding]:
        lines = code.splitlines()
        findings: list[RawFinding] = []
        for rule in self.rules():
            findings.extend(self._apply_rule(rule, lines))
        return findings

    def _apply_rule(self, rule: dict, lines: list[str]) -> list[RawFinding]:
        findings = []
        pattern = re.compile(rule["pattern"], re.IGNORECASE | re.MULTILINE)
        for idx, line in enumerate(lines, start=1):
            match = pattern.search(line)
            if match:
                snippet = self._context_snippet(lines, idx - 1)
                findings.append(RawFinding(
                    title=rule["title"],
                    description=rule["description"],
                    severity=rule["severity"],
                    category=rule["category"],
                    platform=self.platform,
                    line_number=idx,
                    code_snippet=snippet,
                    recommendation=rule["recommendation"],
                    cwe_id=rule.get("cwe_id"),
                    cvss_score=rule.get("cvss_score"),
                    evidence=f"Matched pattern `{rule['pattern']}` at line {idx}: {line.strip()[:120]}",
                ))
        return findings

    @staticmethod
    def _context_snippet(lines: list[str], center: int, context: int = 2) -> str:
        start = max(0, center - context)
        end = min(len(lines), center + context + 1)
        numbered = [f"{i + 1:>4}: {lines[i]}" for i in range(start, end)]
        return "\n".join(numbered)

    @abstractmethod
    def rules(self) -> list[dict]:
        ...
