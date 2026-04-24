from .base import BaseAnalyzer


class WebAnalyzer(BaseAnalyzer):
    platform = "web"

    def rules(self) -> list[dict]:
        return [
            # ── Rule 1 ────────────────────────────────────────────────
            {
                "pattern": r"\"SELECT\s[^\"]*\"\s*\+|\"INSERT\s[^\"]*\"\s*\+|\"UPDATE\s[^\"]*\"\s*\+|\"DELETE\s[^\"]*\"\s*\+|f\"SELECT|f\"INSERT|f\"UPDATE|f\"DELETE|query\s*\+=\s*|query\s*=\s*[\"'].*[\"']\s*\+",
                "title": "SQL Injection — String-Concatenated Query",
                "description": "Constructing SQL by concatenating user-supplied strings allows attackers to inject arbitrary SQL. Beyond authentication bypass (OR 1=1), attackers can extract the entire database (UNION SELECT), drop tables, read server files (LOAD_FILE), or execute OS commands (xp_cmdshell on MSSQL) — all via a single crafted request.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Use parameterized queries exclusively: cursor.execute('SELECT * FROM users WHERE id = %s', (uid,)). Use an ORM (SQLAlchemy, Django ORM, Sequelize, TypeORM) which parameterizes by default. Apply least-privilege database accounts. Enable query logging to detect injection attempts.",
                "cwe_id": "CWE-89",
                "cvss_score": 9.8,
            },
            # ── Rule 2 ────────────────────────────────────────────────
            {
                "pattern": r"innerHTML\s*=|outerHTML\s*=|document\.write\s*\(|insertAdjacentHTML\s*\(|\.html\s*\([^)]*(?:userInput|input|param|req\.|request\.|data\[|\$_GET|\$_POST)",
                "title": "Cross-Site Scripting (XSS) — DOM / Reflected Injection",
                "description": "Writing user-controlled data to innerHTML, document.write(), or jQuery's .html() without encoding executes injected JavaScript in the victim's browser. Attackers steal session cookies, redirect to phishing pages, log keystrokes, or silently exfiltrate all data visible to the victim user.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Use textContent/innerText instead of innerHTML for text data. Sanitize HTML with DOMPurify if rendering is required. Apply a strict Content Security Policy (script-src 'none' or 'nonce-...'). In frameworks (React, Vue, Angular), avoid dangerouslySetInnerHTML / v-html / [innerHTML] bindings.",
                "cwe_id": "CWE-79",
                "cvss_score": 8.8,
            },
            # ── Rule 3 ────────────────────────────────────────────────
            {
                "pattern": r"(?:api[_-]?key|apikey|api[_-]?secret|secret[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|pwd|private[_-]?key|client[_-]?secret|bearer)\s*[=:]\s*['\"][A-Za-z0-9+/=_\-\.]{8,}['\"]",
                "title": "Hardcoded Secret / Credential in Source Code",
                "description": "Hardcoded credentials, API keys, or secrets in source code are exposed to anyone with repository access. In public repositories or leaked codebases, attackers immediately use these to access external services, cloud infrastructure, payment processors, or databases — often before the developer notices.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Remove all hardcoded secrets immediately and rotate them. Use environment variables, a secrets manager (Vault, AWS Secrets Manager, Doppler, 1Password Secrets Automation), or encrypted secret stores. Add pre-commit hooks (detect-secrets, truffleHog, git-secrets) to CI/CD pipelines.",
                "cwe_id": "CWE-798",
                "cvss_score": 9.1,
            },
            # ── Rule 4 ────────────────────────────────────────────────
            {
                "pattern": r"\beval\s*\(|\bnew Function\s*\(|\bexec\s*\(|\bexecSync\s*\(|\bspawn\s*\(\s*(?:req|input|param|userInput|cmd|command)\b",
                "title": "eval() / exec() with Potentially Untrusted Input — RCE Risk",
                "description": "eval(), new Function(), and exec()/execSync() execute their arguments as code. If user-controlled data reaches these sinks, attackers achieve Remote Code Execution on the server or in the victim's browser. This is one of the most severe web vulnerabilities — a single request can own the server.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Never use eval() on user input. Replace Node.js exec() with execFile() (no shell interpretation) or spawn() with separate argument arrays. Replace server-side eval() with a safe expression parser (mathjs, jsep). Remove all dynamic code evaluation.",
                "cwe_id": "CWE-95",
                "cvss_score": 9.8,
            },
            # ── Rule 5 ────────────────────────────────────────────────
            {
                "pattern": r"hashlib\.md5\s*\(|hashlib\.sha1\s*\(|MD5\s*\(|SHA1\s*\(|CryptoJS\.MD5|bcrypt\.hashSync\s*\([^,]+,\s*[1-6]\s*\)|createHash\s*\(\s*['\"]md5['\"]|createHash\s*\(\s*['\"]sha1['\"]",
                "title": "Weak Cryptographic Hash for Security Operation",
                "description": "MD5 and SHA-1 are broken for collision resistance. MD5 collisions are generated in <1 second. SHA-1 was broken by the SHAttered attack in 2017. bcrypt with cost < 10 is vulnerable to brute force on modern GPUs. Using these for password hashing, integrity verification, or HMAC provides false security.",
                "severity": "High",
                "category": "Crypto",
                "recommendation": "For passwords: bcrypt (cost ≥ 12), Argon2id, or scrypt. For data integrity: SHA-256 or SHA-3. For HMAC: HMAC-SHA256 or HMAC-SHA512. In Node.js, use crypto.createHmac('sha256', key). In Python, use hashlib.sha256() or the argon2-cffi library for passwords.",
                "cwe_id": "CWE-327",
                "cvss_score": 7.5,
            },
            # ── Rule 6 ────────────────────────────────────────────────
            {
                "pattern": r"Access-Control-Allow-Origin:\s*\*|res\.(?:header|set|setHeader)\s*\(\s*['\"]Access-Control-Allow-Origin['\"],\s*['\"][*]['\"]|app\.use\s*\(\s*cors\s*\(\s*\)\s*\)|cors\s*\(\s*\{[^}]*origin:\s*['\"][*]['\"]",
                "title": "Wildcard CORS Policy — Credential Leakage Risk",
                "description": "Access-Control-Allow-Origin: * allows any website's JavaScript to make cross-origin requests to your API. Combined with Access-Control-Allow-Credentials: true (which wildcard actually prevents by spec), overly broad CORS policies enable Cross-Site Request Forgery (CSRF) and cross-origin data theft attacks.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Set CORS to an explicit allowlist: origin: ['https://yourdomain.com', 'https://app.yourdomain.com']. Use a function-based origin validator for dynamic allowlists. Never use wildcard with credentials. Combine with CSRF tokens for state-changing endpoints.",
                "cwe_id": "CWE-942",
                "cvss_score": 7.5,
            },
            # ── Rule 7 ────────────────────────────────────────────────
            {
                "pattern": r"http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0|::1)[a-zA-Z0-9]",
                "title": "Insecure HTTP URL — Cleartext Communication",
                "description": "Hardcoded http:// URLs for production services transmit all data in cleartext. Session tokens, API keys, and sensitive user data are visible to network observers. HTTP connections are also vulnerable to active interception — injecting malicious JavaScript into responses.",
                "severity": "Medium",
                "category": "Network",
                "recommendation": "Replace all production http:// URLs with https://. Enable HTTP Strict Transport Security (HSTS) with a long max-age. Configure automatic HTTP-to-HTTPS redirects at the load balancer level. Use HSTS preloading for maximum protection.",
                "cwe_id": "CWE-319",
                "cvss_score": 5.9,
            },
            # ── Rule 8 ────────────────────────────────────────────────
            {
                "pattern": r"open\s*\([^)]*(?:\.\./|%2e%2e|%252e)|path\.(?:join|resolve)\s*\([^)]*(?:req\.|request\.|userInput|input|param|\$_GET|\$_POST|\$_REQUEST)",
                "title": "Path Traversal — Directory Traversal Attack",
                "description": "File paths constructed from user-controlled input without canonicalization allow ../ traversal to escape the intended directory. Attackers access /etc/passwd, /etc/shadow, application source code, .env files, or overwrite server configuration. URL-encoded variants (%2e%2e%2f) bypass naive checks.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Resolve the full path and assert it starts with the allowed base: realpath = os.path.realpath(user_path); assert realpath.startswith(BASE_DIR). In Node.js: path.resolve(BASE_DIR, userInput).startsWith(BASE_DIR). Reject inputs containing '..' or null bytes before path construction.",
                "cwe_id": "CWE-22",
                "cvss_score": 8.6,
            },
            # ── Rule 9 ────────────────────────────────────────────────
            {
                "pattern": r"pickle\.loads\s*\(|pickle\.load\s*\(|yaml\.load\s*\([^)]*(?!Loader=yaml\.SafeLoader|Loader=yaml\.CSafeLoader|safe_load)|marshal\.loads\s*\(",
                "title": "Insecure Deserialization — Arbitrary Code Execution",
                "description": "Python's pickle.loads(), yaml.load() without SafeLoader, and marshal.loads() execute arbitrary Python code embedded in the serialized data stream. A single crafted request containing a malicious pickle payload achieves full Remote Code Execution with the web process's OS privileges.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Never deserialize pickle/marshal from untrusted sources. Use json.loads() or yaml.safe_load() for data interchange. Sign serialized data with HMAC if integrity is needed: hmac.compare_digest(expected_sig, actual_sig). For complex objects use jsonpickle with a type allowlist.",
                "cwe_id": "CWE-502",
                "cvss_score": 9.8,
            },
            # ── Rule 10 ───────────────────────────────────────────────
            {
                "pattern": r"redirect\s*\(\s*request\.\w+\s*\[|redirect\s*\(\s*req\.(?:query|params|body)\.|HttpResponseRedirect\s*\(\s*request\.GET|return\s+redirect\s*\(\s*next\s*\)",
                "title": "Open Redirect — Unvalidated Redirect Destination",
                "description": "Redirecting users to a URL from an unvalidated request parameter creates open redirect vulnerabilities. Attackers craft phishing URLs that appear legitimate (yourbank.com/login?next=evil.com), redirecting users to attacker-controlled sites after authentication. This is commonly used in credential harvesting campaigns.",
                "severity": "Medium",
                "category": "Security",
                "recommendation": "Allowlist redirect destinations: only accept relative paths or URLs matching your application's domain. Use urlparse to extract and validate host/scheme before redirecting. Reject any destination with a different origin. Show a warning page before redirecting to external domains.",
                "cwe_id": "CWE-601",
                "cvss_score": 6.1,
            },
            # ── Rule 11 ───────────────────────────────────────────────
            {
                "pattern": r"lxml\.etree\.parse\s*\(|etree\.fromstring\s*\(|xml\.etree\.ElementTree\.parse|defusedxml",
                "title": "XML Parser — Verify XXE / Billion Laughs Protection",
                "description": "Standard XML parsers (lxml, Python's xml.etree.ElementTree, Java's DocumentBuilder) are vulnerable to XXE injection and entity expansion attacks (Billion Laughs / XML Bomb). A malicious XML document can read arbitrary server files or exhaust server memory.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Use defusedxml Python library which patches all standard parsers to disable external entities and DTD processing by default. For lxml, set resolve_entities=False and no_network=True in XMLParser(). Never parse XML from untrusted sources with a default-configured parser.",
                "cwe_id": "CWE-611",
                "cvss_score": 9.1,
            },
            # ── Rule 12 ───────────────────────────────────────────────
            {
                "pattern": r"requests\.get\s*\(\s*(?:url|target|dest|endpoint|proxy|fetch)|\bfetch\s*\(\s*(?:url|target|endpoint|req\.query|req\.body|request\.args)|urllib\.request\.urlopen\s*\(\s*(?!\"https)",
                "title": "Server-Side Request Forgery (SSRF)",
                "description": "Making server-side HTTP requests to user-controlled URLs allows attackers to probe internal services (metadata endpoints at 169.254.169.254 for AWS/GCP credentials, internal databases, Redis, Elasticsearch), read internal-only endpoints, or pivot to internal network hosts that are not exposed publicly.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Validate and allowlist target URLs against a strict list of permitted schemes and domains. Block private IP ranges (10.x, 172.16-31.x, 192.168.x, 127.x, 169.254.x, ::1) in all URL fetching code. Use a dedicated egress proxy that enforces allowlists. Resolve DNS before validation to prevent DNS rebinding.",
                "cwe_id": "CWE-918",
                "cvss_score": 9.1,
            },
            # ── Rule 13 ───────────────────────────────────────────────
            {
                "pattern": r"algorithms\s*=\s*\[.*\"none\"\s*\]|jwt\.decode\s*\([^)]*algorithms.*none|verify\s*=\s*False|options\s*=\s*\{[^}]*\"verify_signature\"\s*:\s*False",
                "title": "JWT Algorithm Confusion — 'none' Algorithm or Signature Skip",
                "description": "Accepting JWT tokens with the 'none' algorithm or skipping signature verification allows attackers to forge arbitrary tokens. An attacker changes the algorithm to 'none', sets any user ID or role in the payload, and removes the signature — the server accepts the forged token as valid.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Always specify an explicit algorithms allowlist: jwt.decode(token, key, algorithms=['HS256']). Never include 'none' in the algorithm list. Always verify the signature (never set verify=False). Use asymmetric algorithms (RS256, ES256) in multi-service environments where signing and verification are separated.",
                "cwe_id": "CWE-347",
                "cvss_score": 9.8,
            },
            # ── Rule 14 ───────────────────────────────────────────────
            {
                "pattern": r"__proto__\s*\[|prototype\[|Object\.assign\s*\(\s*\{\}|merge\s*\(\s*(?:obj|target|config|settings|options)\s*,\s*(?:req\.|input|body|userInput)",
                "title": "Prototype Pollution — Object Inheritance Corruption",
                "description": "Merging or assigning user-controlled objects into JavaScript objects without property key validation allows attackers to set __proto__ or constructor.prototype properties. This corrupts the prototype chain of all objects in the application, potentially overriding security-critical properties or enabling DoS.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Use Object.create(null) for objects storing user-controlled keys. Sanitize keys before merge: if (key === '__proto__' || key === 'constructor' || key === 'prototype') continue. Use safe merge libraries (lodash.mergeWith with customizer) or structuredClone() for deep copies.",
                "cwe_id": "CWE-1321",
                "cvss_score": 8.1,
            },
            # ── Rule 15 ───────────────────────────────────────────────
            {
                "pattern": r"render_template_string\s*\(.*(?:request\.|input|param|userInput)|Template\s*\(\s*(?:userInput|input|request|f\"|\".*\{)",
                "title": "Server-Side Template Injection (SSTI)",
                "description": "Rendering Jinja2, Twig, Freemarker, or other templates from user-controlled strings enables SSTI. Attackers inject template expressions ({{7*7}}, {{config}}) to enumerate environment variables, execute OS commands ({{''.__class__.__mro__[1].__subclasses__()}}), or read arbitrary files from the server.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Never pass user input to render_template_string() or Template(). Always use render_template() with static template files. If dynamic template generation is required, use a sandbox environment with SandboxedEnvironment in Jinja2. Treat template engines as code execution environments.",
                "cwe_id": "CWE-94",
                "cvss_score": 9.8,
            },
            # ── Rule 16 ───────────────────────────────────────────────
            {
                "pattern": r"\$where\s*:|\.find\s*\(\s*\{[^}]*\$|\.findOne\s*\(\s*\{[^}]*\$|MongoClient.*\$(?:gt|lt|ne|in|nin|or|and|regex|where)",
                "title": "NoSQL Injection — MongoDB Operator Injection",
                "description": "Passing user-controlled JSON objects directly to MongoDB queries without validation allows operator injection. Attackers submit {\"$gt\": \"\"} for a password field to match all documents, bypassing authentication — the MongoDB equivalent of SQL injection.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Validate and sanitize all query parameters: reject objects when a string is expected. Use mongoose schema validation with strict: true to reject unknown fields. Use a query builder that doesn't accept raw operators from user input. Allowlist expected query keys and value types.",
                "cwe_id": "CWE-943",
                "cvss_score": 9.1,
            },
            # ── Rule 17 ───────────────────────────────────────────────
            {
                "pattern": r"ldap\.search_s\s*\(.*(?:userInput|input|param|request|uid|cn|dn)\s*\+|\"\\(cn=\"\s*\+|\"\\(&\\(cn=\"\s*\+",
                "title": "LDAP Injection",
                "description": "Constructing LDAP search filter strings from user input allows LDAP injection. Attackers inject LDAP special characters ()(|!\\*) to bypass authentication, enumerate the entire directory, read all user attributes including credentials and group memberships, or perform directory denial of service.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Escape all user input using your LDAP library's escape function (e.g., ldap3.utils.conv.escape_filter_chars() in Python). Use parameterized LDAP queries if your library supports them. Validate that input contains only expected character classes before using in any LDAP filter.",
                "cwe_id": "CWE-90",
                "cvss_score": 9.1,
            },
            # ── Rule 18 ───────────────────────────────────────────────
            {
                "pattern": r"process\.env\.NODE_ENV\s*!==?\s*['\"]production['\"]|if\s*\(\s*debug\s*\)|app\.use\s*\(\s*morgan\s*\(\s*['\"]dev['\"]|console\.log\s*\(.*(?:password|token|secret|key|req\.body)",
                "title": "Debug Mode or Verbose Logging Enabled in Production",
                "description": "Debug middleware, verbose logging, and development-mode error handlers expose stack traces, environment variables, database schemas, and internal request/response details in production. Attackers use this information to map the application's attack surface and identify exploitable components.",
                "severity": "Medium",
                "category": "Security",
                "recommendation": "Gate all debug logging behind NODE_ENV === 'production' checks. Use structured logging (Winston, Pino) with log levels — only ERROR and WARN in production. Configure express-validator to return generic error messages in production. Use a global error handler that strips stack traces from API responses.",
                "cwe_id": "CWE-532",
                "cvss_score": 5.3,
            },
            # ── Rule 19 ───────────────────────────────────────────────
            {
                "pattern": r"introspectionEnabled:\s*true|graphiql:\s*true|__schema\s*\{|playground:\s*true",
                "title": "GraphQL Introspection / Playground Enabled in Production",
                "description": "GraphQL introspection enabled in production exposes the full schema — all types, fields, mutations, and relationships. Attackers use this to identify sensitive fields, map the entire data model, and craft targeted queries to extract data. GraphQL playground/GraphiQL provides a convenient attack interface.",
                "severity": "Medium",
                "category": "Security",
                "recommendation": "Disable introspection in production: introspection: process.env.NODE_ENV !== 'production'. Disable GraphiQL and playground in production deployments. Implement query depth limiting, query complexity analysis, and persisted query allowlists to restrict what clients can query.",
                "cwe_id": "CWE-200",
                "cvss_score": 5.3,
            },
            # ── Rule 20 ───────────────────────────────────────────────
            {
                "pattern": r"X-Frame-Options|Content-Security-Policy|X-Content-Type-Options|Strict-Transport-Security|Referrer-Policy",
                "title": "Security Header Present — Verify Configuration Correctness",
                "description": "The presence of security headers is detected. This is a positive signal — verify the values are correct. Misconfigured headers (CSP with unsafe-inline, HSTS without includeSubDomains, X-Frame-Options ALLOWALL) provide false protection and may indicate incomplete security hardening.",
                "severity": "Low",
                "category": "Security",
                "recommendation": "Audit security header values: CSP should include default-src 'none' and specific allowlists without unsafe-inline. HSTS should have max-age >= 31536000 with includeSubDomains. X-Frame-Options should be DENY or SAMEORIGIN. Use securityheaders.com to validate your configuration.",
                "cwe_id": "CWE-693",
                "cvss_score": 3.1,
            },
            # ── Rule 21 ───────────────────────────────────────────────
            {
                "pattern": r"os\.system\s*\(|subprocess\.(?:call|run|Popen|check_output)\s*\([^)]*(?:shell\s*=\s*True|stdin=subprocess\.PIPE)[^)]*(?:userInput|input|param|request|f\"|\".*{)|subprocess\.call\s*\([^)]*shell=True",
                "title": "OS Command Injection via subprocess with shell=True",
                "description": "Using subprocess with shell=True and user-controlled input is equivalent to calling os.system() on the input — it passes the command through /bin/sh, enabling full shell injection with metacharacters. A single semicolon allows appending arbitrary commands.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Remove shell=True and pass the command as a list: subprocess.run(['/usr/bin/find', '-name', user_input], shell=False). Validate all inputs against an explicit allowlist of safe values. Use shlex.quote() as a last resort, but prefer eliminating shell=True entirely.",
                "cwe_id": "CWE-78",
                "cvss_score": 9.8,
            },
            # ── Rule 22 ───────────────────────────────────────────────
            {
                "pattern": r"\.setAttribute\s*\(\s*['\"]on\w+['\"]|addEventListener\s*\(\s*['\"]message['\"].*JSON\.parse|postMessage\s*\(\s*(?!window\.)",
                "title": "DOM-Based XSS via Event Handler or postMessage",
                "description": "Setting event handler attributes (onclick, onerror) via setAttribute with user-controlled values, or processing unvalidated postMessage data, creates DOM-based XSS. The attack occurs entirely in the client-side DOM — no server interaction required — making it undetectable by server-side filters.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Never set event handler attributes via setAttribute. Use addEventListener for event binding. Validate postMessage origin with event.origin against an explicit allowlist. Use a strict Content Security Policy that blocks inline event handlers. Use DOMPurify to sanitize any HTML before insertion.",
                "cwe_id": "CWE-79",
                "cvss_score": 7.5,
            },
            # ── Rule 23 ───────────────────────────────────────────────
            {
                "pattern": r"crypto\.randomBytes\s*\(\s*[1-7]\s*\)|crypto\.randomBytes\s*\(\s*8\s*\)|Math\.random\s*\(\s*\).*(?:token|session|csrf|nonce|salt|key)",
                "title": "Insufficient Entropy for Security Token Generation",
                "description": "Using Math.random() (non-cryptographic) or generating tokens with fewer than 16 random bytes creates guessable security tokens. Session IDs, CSRF tokens, password reset tokens, and API keys with insufficient entropy are vulnerable to brute force or statistical prediction attacks.",
                "severity": "High",
                "category": "Crypto",
                "recommendation": "Use crypto.randomBytes(32) for all security tokens (produces 256 bits of entropy). For Node.js: const token = crypto.randomBytes(32).toString('hex'). For Python: secrets.token_hex(32). Never use Math.random() or uuid.uuid4() alone for security tokens — use crypto.randomUUID() (Node 14.17+) instead.",
                "cwe_id": "CWE-338",
                "cvss_score": 7.4,
            },
            # ── Rule 24 ───────────────────────────────────────────────
            {
                "pattern": r"\.cookie\s*\([^)]*(?:httpOnly|HttpOnly)\s*:\s*false|Set-Cookie:[^\\n]*(?!HttpOnly)|res\.cookie\s*\([^)]*\)(?![^;]*httpOnly:\s*true)",
                "title": "Session Cookie Without HttpOnly Flag — XSS Session Theft",
                "description": "Session cookies without the HttpOnly attribute are accessible via document.cookie in JavaScript. Any XSS vulnerability (including third-party JavaScript) can silently exfiltrate session cookies to an attacker's server, enabling complete session hijacking without the user's knowledge.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Set HttpOnly: true on all session and authentication cookies: res.cookie('session', value, { httpOnly: true, secure: true, sameSite: 'strict', maxAge: 3600000 }). Also set Secure (HTTPS-only) and SameSite=Strict. Use __Host- cookie prefix for additional protection.",
                "cwe_id": "CWE-1004",
                "cvss_score": 7.5,
            },
            # ── Rule 25 ───────────────────────────────────────────────
            {
                "pattern": r"require\s*\(\s*(?:userInput|input|param|request\.|path\s*\+|`\$\{)|import\s*\(\s*(?:userInput|input|`\$\{path|`\$\{req)",
                "title": "Dynamic require() / import() with User-Controlled Path",
                "description": "Passing user-controlled values to require() or dynamic import() allows attackers to load arbitrary Node.js modules, including built-in modules (child_process, fs), local files, or installed packages with dangerous side effects. This achieves RCE with a single crafted request parameter.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Never call require() or import() with user-supplied paths. Use a static lookup map: const MODULES = { 'plugin-a': require('./plugins/a') }; return MODULES[userInput]. Validate that userInput is a key in the map before lookup. Disable dynamic requires in webpack/bundler configs.",
                "cwe_id": "CWE-95",
                "cvss_score": 9.8,
            },
        ]
