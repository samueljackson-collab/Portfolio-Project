# Security Standards

**Version:** 2.1 | **Owner:** Security Engineering | **Last Updated:** 2026-01-10

All engineers are responsible for writing secure code. Security is not a review step at
the end — it is built in from the first line of code.

---

## 1. Authentication & Authorisation

### 1.1 Never Roll Your Own Auth

Use established, audited libraries. Do not implement JWT signing, password hashing, or
session management from scratch.

```python
# GOOD — use passlib for hashing, python-jose for JWTs
from passlib.context import CryptContext
from jose import jwt, JWTError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

### 1.2 JWT Standards

- Algorithm: **RS256** or **ES256** (asymmetric). Never HS256 in production (symmetric key sharing risk).
- Expiry: Access tokens **15 minutes**, refresh tokens **7 days**.
- Claims: Always validate `exp`, `iat`, `iss`, `aud`.
- Storage: Tokens in `HttpOnly`, `Secure`, `SameSite=Strict` cookies. Never in localStorage.

### 1.3 MFA Requirements

| Account Type | MFA Required | Accepted Methods |
|-------------|-------------|-----------------|
| Domain admin | Mandatory | FIDO2 / hardware key only |
| Standard employee | Mandatory | TOTP / FIDO2 |
| Service accounts | N/A | Certificate or API key with IP restriction |
| API access | Recommended | API key + IP allowlist |

---

## 2. Secrets Management

### Rules — Zero Tolerance

- **NEVER** hardcode secrets in source code
- **NEVER** commit `.env` files to version control
- **NEVER** log secrets, tokens, or passwords (even in debug logs)
- **ALWAYS** use environment variables or a secrets manager

### Approved Secrets Managers

| Environment | Tool |
|-----------|------|
| AWS | AWS Secrets Manager or Parameter Store |
| Local dev | `.env` file (in `.gitignore`) + `python-dotenv` |
| Kubernetes | Sealed Secrets or External Secrets Operator |
| CI/CD | GitHub Actions Secrets or Vault |

```python
# GOOD — retrieve secret at runtime, never hardcoded
import boto3

def get_db_password() -> str:
    client = boto3.client("secretsmanager", region_name="us-east-1")
    response = client.get_secret_value(SecretId="prod/db/password")
    return response["SecretString"]

# BAD — instant security violation
DB_PASSWORD = "SuperSecret123!"  # NEVER DO THIS
```

---

## 3. Input Validation & Injection Prevention

### 3.1 SQL Injection

Always use parameterised queries. Never concatenate user input into SQL strings.

```python
# GOOD — parameterised query
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

# BAD — SQL injection vulnerability
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")  # NEVER
```

### 3.2 Command Injection

Never pass user input to shell commands. Use subprocess with a list, not a string.

```python
# GOOD — no shell interpretation
subprocess.run(["git", "clone", user_provided_url], check=True, capture_output=True)

# BAD — command injection vulnerability
os.system(f"git clone {user_provided_url}")  # NEVER
```

### 3.3 XSS Prevention

- All user-provided content must be HTML-escaped before rendering
- Use framework defaults (React escapes by default; never use `dangerouslySetInnerHTML`)
- Content Security Policy (CSP) header required on all web applications

---

## 4. Dependency Security

```bash
# Python — audit with safety or pip-audit
pip-audit --require-hashes

# Node.js — audit with npm
npm audit --audit-level=high

# Container images — scan with Trivy
trivy image --exit-code 1 --severity HIGH,CRITICAL myapp:latest
```

### Dependency Policy

- **CRITICAL/HIGH** CVEs: Block PR merge until resolved
- **MEDIUM** CVEs: Must be remediated within 30 days
- **LOW** CVEs: Track in tech debt register; remediate within 90 days
- Dependency updates reviewed monthly (Dependabot / Renovate)

---

## 5. Secure Defaults Checklist

Every new service must satisfy all of the following at launch:

- [ ] TLS 1.2+ enforced on all endpoints (no HTTP in production)
- [ ] Security headers set: `Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options`, `Content-Security-Policy`
- [ ] No sensitive data in URL parameters (use POST body or headers)
- [ ] Rate limiting on authentication endpoints (max 10 attempts / 15 min)
- [ ] Audit logging enabled for all auth events and admin actions
- [ ] Least-privilege IAM role / service account
- [ ] Secrets stored in secrets manager (not env vars in container spec)
- [ ] SAST scan clean before first production deploy
