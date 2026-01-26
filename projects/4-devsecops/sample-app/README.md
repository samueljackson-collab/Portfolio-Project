# Security Demo Application

This directory contains intentionally vulnerable and secure versions of a web application for demonstrating security scanning tools.

## Files

### `vulnerable.py` - Intentionally Vulnerable Application

Contains common security vulnerabilities for demonstration purposes:

| Vulnerability | CWE | Detection Tool |
|--------------|-----|----------------|
| Hardcoded Credentials | CWE-798 | Gitleaks, TruffleHog |
| SQL Injection | CWE-89 | Semgrep, Bandit, CodeQL |
| Command Injection | CWE-78 | Semgrep, Bandit |
| Path Traversal | CWE-22 | Semgrep, Bandit |
| Cross-Site Scripting (XSS) | CWE-79 | Semgrep |
| Insecure Deserialization | CWE-502 | Semgrep, Bandit |
| Weak Cryptography (MD5) | CWE-327 | Semgrep, Bandit |
| Insecure Random | CWE-330 | Semgrep, Bandit |
| Open Redirect | CWE-601 | Semgrep |
| XML External Entity (XXE) | CWE-611 | Semgrep, Bandit |
| Server-Side Request Forgery | CWE-918 | Semgrep |
| Debug Mode in Production | CWE-489 | Bandit |

### `secure.py` - Secure Implementation

Demonstrates the correct way to handle each vulnerability:

- Environment variables for secrets
- Parameterized SQL queries
- Input validation and allowlists
- Proper escaping and templates
- JSON instead of pickle
- bcrypt for password hashing
- secrets module for tokens
- URL validation for redirects
- defusedxml for XML parsing
- SSRF protection with IP validation

## Running Scans

### Semgrep
```bash
semgrep --config auto sample-app/ --json > semgrep-results.json
```

### Bandit
```bash
bandit -r sample-app/ -f json -o bandit-results.json
```

### Gitleaks
```bash
gitleaks detect --source sample-app/ --report-format json --report-path gitleaks-results.json
```

### Generate Dashboard
```bash
python scripts/generate-dashboard.py \
  --semgrep semgrep-results.json \
  --bandit bandit-results.json \
  --gitleaks gitleaks-results.json \
  --output security-dashboard.html
```

## Warning

The `vulnerable.py` file is for educational and testing purposes only. **DO NOT** deploy this code or use any of these patterns in production applications.
