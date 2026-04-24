from __future__ import annotations
import asyncio
import re
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

CROSS_RULE_CONTEXT_RADIUS = 15  # lines above/below a finding to re-inspect


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
    cross_rule_trigger: str | None = field(default=None)  # which rule triggered the re-check


class BaseAnalyzer(ABC):
    platform: str = "generic"

    # ------------------------------------------------------------------ #
    #  Public entry point                                                  #
    # ------------------------------------------------------------------ #

    async def analyze_streaming(self, code: str, filename: str):
        """Async generator that yields RawFindings rule-by-rule for live streaming."""
        lines = code.splitlines()
        rules = self.rules()
        initial: list[RawFinding] = []

        for rule_idx, rule in enumerate(rules):
            batch = await asyncio.to_thread(self._apply_rule, rule, lines, rule_idx)
            for finding in batch:
                initial.append(finding)
                yield finding
            await asyncio.sleep(0)  # yield control to event loop between rules

        cross = await asyncio.to_thread(self._cross_rule_pass, initial, lines, rules)
        for finding in cross:
            yield finding

    def analyze(self, code: str, filename: str) -> list[RawFinding]:
        lines = code.splitlines()
        rules = self.rules()

        # ── Pass 1: run every rule against every line ──────────────────
        initial: list[RawFinding] = []
        for rule in rules:
            initial.extend(self._apply_rule(rule, lines, rule_index=rules.index(rule)))

        # ── Pass 2: cross-rule re-inspection ──────────────────────────
        # For each finding discovered in pass 1, extract an extended
        # context window around the suspicious line and re-run ALL rules
        # against that window.  New findings that pass 1 missed (because
        # the pattern only "fired" in the combined suspicious context) are
        # added with metadata linking them back to the trigger finding.
        cross: list[RawFinding] = self._cross_rule_pass(initial, lines, rules)

        return initial + cross

    # ------------------------------------------------------------------ #
    #  Pass 1 helpers                                                      #
    # ------------------------------------------------------------------ #

    def _apply_rule(
        self,
        rule: dict,
        lines: list[str],
        rule_index: int = -1,
    ) -> list[RawFinding]:
        findings: list[RawFinding] = []
        try:
            pattern = re.compile(rule["pattern"], re.IGNORECASE | re.MULTILINE)
        except re.error:
            return findings

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
                    evidence=(
                        f"[Rule {rule_index + 1}] Matched `{rule['pattern'][:80]}` "
                        f"at line {idx}: {line.strip()[:120]}"
                    ),
                ))
        return findings

    # ------------------------------------------------------------------ #
    #  Pass 2 – cross-rule re-inspection                                   #
    # ------------------------------------------------------------------ #

    def _cross_rule_pass(
        self,
        initial_findings: list[RawFinding],
        lines: list[str],
        rules: list[dict],
    ) -> list[RawFinding]:
        """
        For every finding from pass 1, carve out an extended context window
        (CROSS_RULE_CONTEXT_RADIUS lines in each direction) and re-run the
        full rule set against that window.  Any *new* matches — findings
        whose (title, line_number) key did not appear in pass 1 — are
        returned as secondary findings.  This catches cascading patterns:
        e.g. rule 16 surfaces a suspicious block that rule 3 should also
        have caught but missed because the triggering text only appears
        adjacent to the primary match.
        """
        if not initial_findings:
            return []

        # Keys already found — skip duplicates
        seen: set[tuple[str, int | None]] = {
            (f.title, f.line_number) for f in initial_findings
        }
        cross_findings: list[RawFinding] = []

        for trigger in initial_findings:
            if trigger.line_number is None:
                continue

            center = trigger.line_number - 1  # 0-indexed
            ctx_start = max(0, center - CROSS_RULE_CONTEXT_RADIUS)
            ctx_end = min(len(lines), center + CROSS_RULE_CONTEXT_RADIUS + 1)

            # Pairs of (actual_1indexed_line_number, line_text)
            window = [
                (i + 1, lines[i])
                for i in range(ctx_start, ctx_end)
            ]

            for rule_idx, rule in enumerate(rules):
                try:
                    pattern = re.compile(rule["pattern"], re.IGNORECASE | re.MULTILINE)
                except re.error:
                    continue

                for actual_ln, line_text in window:
                    if not pattern.search(line_text):
                        continue

                    key = (rule["title"], actual_ln)
                    if key in seen:
                        continue  # already reported

                    seen.add(key)
                    snippet = self._context_snippet(lines, actual_ln - 1)
                    cross_findings.append(RawFinding(
                        title=rule["title"],
                        description=rule["description"],
                        severity=rule["severity"],
                        category=rule["category"],
                        platform=self.platform,
                        line_number=actual_ln,
                        code_snippet=snippet,
                        recommendation=rule["recommendation"],
                        cwe_id=rule.get("cwe_id"),
                        cvss_score=rule.get("cvss_score"),
                        evidence=(
                            f"[Cross-rule · Rule {rule_idx + 1} re-inspecting context "
                            f"of '{trigger.title}' at line {trigger.line_number}] "
                            f"Matched `{rule['pattern'][:60]}` at line {actual_ln}: "
                            f"{line_text.strip()[:120]}"
                        ),
                        cross_rule_trigger=trigger.title,
                    ))

        return cross_findings

    # ------------------------------------------------------------------ #
    #  Shared utilities                                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _context_snippet(lines: list[str], center: int, context: int = 3) -> str:
        start = max(0, center - context)
        end = min(len(lines), center + context + 1)
        return "\n".join(f"{i + 1:>4}: {lines[i]}" for i in range(start, end))

    @abstractmethod
    def rules(self) -> list[dict]:
        ...
