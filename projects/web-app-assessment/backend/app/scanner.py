from typing import List, Dict
from pydantic import BaseModel
from pydantic import BaseModel, HttpUrl


class ScanFinding(BaseModel):
    title: str
    severity: str
    description: str
    rule: str


def scan_page(url: str) -> List[ScanFinding]:
    """Apply dummy vulnerability rules to a URL.

    The function checks for a handful of simulated insecure patterns to mimic
    a lightweight application security scan. Findings are deterministic to
    keep unit tests stable and documentation reproducible.
    """
    findings: List[ScanFinding] = []
    normalized = str(url).lower()

    rules: Dict[str, Dict[str, str]] = {
        "plain_http": {
            "title": "Insecure transport",
            "severity": "high",
            "description": "Page is served over HTTP instead of HTTPS.",
        },
        "debug_param": {
            "title": "Debug mode enabled",
            "severity": "medium",
            "description": "Debug parameter detected in the query string.",
        },
        "id_param": {
            "title": "Potential injection point",
            "severity": "medium",
            "description": "Identifier parameter could be vulnerable to SQL injection.",
        },
        "token_leak": {
            "title": "Sensitive token in URL",
            "severity": "high",
            "description": "Authentication token appears in the query string.",
        },
    }

    if normalized.startswith("http://"):
        findings.append(ScanFinding(**rules["plain_http"], rule="PLAIN_HTTP"))

    if "debug=true" in normalized or "debug=1" in normalized:
        findings.append(ScanFinding(**rules["debug_param"], rule="DEBUG_FLAG"))

    if "id=" in normalized:
        findings.append(ScanFinding(**rules["id_param"], rule="IDENTIFIER_PARAM"))

    if "token=" in normalized:
        findings.append(ScanFinding(**rules["token_leak"], rule="TOKEN_IN_QUERY"))

    return findings
