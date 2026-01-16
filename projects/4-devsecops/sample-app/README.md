# Sample Application for Security Testing

This directory contains two versions of a Flask application designed to demonstrate security vulnerabilities and their secure counterparts.

## Overview

| File | Purpose |
|------|---------|
| `vulnerable.py` | Intentionally vulnerable application for security scanner testing |
| `secure.py` | Secure implementation following OWASP best practices |

## Vulnerabilities Demonstrated

### vulnerable.py includes:

| Vulnerability | CWE | Description |
|--------------|-----|-------------|
| SQL Injection | CWE-89 | Direct string concatenation in SQL queries |
| Command Injection | CWE-78 | User input in shell commands |
| Cross-Site Scripting (XSS) | CWE-79 | Unescaped user input in HTML |
| Hardcoded Credentials | CWE-798 | Passwords and API keys in source code |
| Insecure Deserialization | CWE-502 | Using pickle with untrusted data |
| Path Traversal | CWE-22 | No validation of file paths |
| Weak Cryptography | CWE-327 | MD5/SHA1 for password hashing |
| XML External Entity (XXE) | CWE-611 | XML parsing without disabling external entities |
| Server-Side Request Forgery (SSRF) | CWE-918 | Fetching arbitrary URLs |
| Information Disclosure | CWE-200 | Exposing stack traces and debug info |
| Open Redirect | CWE-601 | Redirecting to user-supplied URLs |
| Missing Authentication | CWE-306 | Admin panel without auth |
| Mass Assignment | CWE-915 | Allowing arbitrary field updates |

### secure.py implements:

- Parameterized SQL queries
- Input validation and sanitization
- Secure password hashing (PBKDF2)
- Content Security Policy headers
- Rate limiting
- Authentication and authorization
- Path validation and sandboxing
- defusedxml for XXE protection
- SSRF prevention with URL validation
- Secure error handling
- Cryptographically secure random generation

## Running Locally

### Prerequisites

```bash
pip install -r requirements.txt
```

### Run the Vulnerable App (Testing Only)

```bash
# WARNING: Only run in isolated environment
python vulnerable.py
```

The app will start on `http://localhost:5000`

### Run the Secure App

```bash
# Set environment variables for production
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export DATABASE_URL=secure_app.db

python secure.py
```

## Security Scanning

### Using Semgrep

```bash
# Scan vulnerable app
semgrep --config "p/security-audit" --config "p/owasp-top-ten" vulnerable.py

# Scan secure app (should have fewer findings)
semgrep --config "p/security-audit" --config "p/owasp-top-ten" secure.py
```

### Using Bandit

```bash
# Scan vulnerable app
bandit -r vulnerable.py -f json -o bandit-vulnerable.json

# Scan secure app
bandit -r secure.py -f json -o bandit-secure.json

# Compare results
echo "Vulnerable app issues:"
cat bandit-vulnerable.json | python -c "import sys,json; d=json.load(sys.stdin); print(f'Total: {len(d[\"results\"])} issues')"

echo "Secure app issues:"
cat bandit-secure.json | python -c "import sys,json; d=json.load(sys.stdin); print(f'Total: {len(d[\"results\"])} issues')"
```

### Using Gitleaks (Secrets Detection)

```bash
# Scan for hardcoded secrets
gitleaks detect --source . --verbose
```

### Using Trivy

```bash
# Scan for vulnerabilities in dependencies
trivy fs --scanners vuln,secret .
```

## Expected Scan Results

### Vulnerable App

When scanning `vulnerable.py`, you should expect findings for:

- **High Severity**: SQL injection, command injection, hardcoded credentials
- **Medium Severity**: XSS, path traversal, insecure deserialization
- **Low Severity**: Weak cryptography, debug mode enabled

Example Semgrep output:
```
vulnerable.py
severity:error rule:python.lang.security.audit.dangerous-system-call
severity:error rule:python.lang.security.audit.hardcoded-password-string
severity:error rule:python.flask.security.xss.direct-template-string
...
```

### Secure App

When scanning `secure.py`, you should expect:

- Significantly fewer findings
- Remaining findings may be informational or require manual review
- No critical or high-severity vulnerabilities

## Testing Vulnerabilities Manually

### SQL Injection Test

```bash
# Against vulnerable app
curl -X POST http://localhost:5000/login \
  -d "username=admin' OR '1'='1&password=anything"
# Expected: Login successful (vulnerability exploited)

# Against secure app
curl -X POST http://localhost:5000/login \
  -d "username=admin' OR '1'='1&password=anything"
# Expected: Invalid credentials (attack blocked)
```

### Command Injection Test

```bash
# Against vulnerable app
curl "http://localhost:5000/ping?host=localhost;cat%20/etc/passwd"
# Expected: Shows /etc/passwd contents (vulnerability exploited)

# Against secure app
curl "http://localhost:5000/ping?host=localhost;cat%20/etc/passwd"
# Expected: Invalid hostname format (attack blocked)
```

### XSS Test

```bash
# Against vulnerable app
curl "http://localhost:5000/search?q=<script>alert('XSS')</script>"
# Expected: Script tag rendered (vulnerability exploited)

# Against secure app
curl "http://localhost:5000/search?q=<script>alert('XSS')</script>"
# Expected: Script tag escaped (attack blocked)
```

### Path Traversal Test

```bash
# Against vulnerable app
curl "http://localhost:5000/download?file=../../../etc/passwd"
# Expected: Shows /etc/passwd contents (vulnerability exploited)

# Against secure app
curl "http://localhost:5000/download?file=../../../etc/passwd"
# Expected: Invalid filename or Access denied (attack blocked)
```

## CI/CD Integration

The security pipeline automatically scans both files:

1. **Semgrep** runs with OWASP and security-audit rules
2. **Bandit** scans Python code for security issues
3. **Gitleaks** detects hardcoded secrets
4. **Trivy** scans for CVEs and secrets

The pipeline:
- Reports findings to GitHub Security tab (SARIF format)
- Generates JSON summaries for the dashboard
- Fails the build if critical issues are found in `secure.py`

## Learning Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.0.x/security/)
- [Semgrep Rules](https://semgrep.dev/explore)
- [Bandit Documentation](https://bandit.readthedocs.io/)

## Disclaimer

**WARNING**: The vulnerable application is for educational and testing purposes only. Never deploy vulnerable code to production. Always run security scanners in isolated environments.
