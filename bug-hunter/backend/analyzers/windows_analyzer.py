from .base import BaseAnalyzer


class WindowsAnalyzer(BaseAnalyzer):
    platform = "windows"

    def rules(self) -> list[dict]:
        return [
            # ── Rule 1 ────────────────────────────────────────────────
            {
                "pattern": r"\bstrcpy\s*\(|\bsprintf\s*\(|\bgets\s*\(|\bstrcat\s*\(|\bwcscpy\s*\(|\bwcscat\s*\(",
                "title": "Unsafe C/C++ String Function — Buffer Overflow",
                "description": "Functions like strcpy, sprintf, gets, strcat, wcscpy, and wcscat write to destination buffers without bounds checking. Writing past the end of a stack buffer overwrites return addresses (classic stack smashing), enabling arbitrary code execution — one of the most exploited vulnerability classes in Windows history.",
                "severity": "Critical",
                "category": "Memory",
                "recommendation": "Replace with safe CRT variants: strcpy_s, sprintf_s, gets_s, strcat_s with explicit buffer sizes. Enable /GS (stack canaries), /SAFESEH, and /DYNAMICBASE (ASLR) compiler flags. Use std::string in C++. Run with Address Sanitizer during testing.",
                "cwe_id": "CWE-120",
                "cvss_score": 9.8,
            },
            # ── Rule 2 ────────────────────────────────────────────────
            {
                "pattern": r"Process\.Start\s*\(\s*(?:[a-zA-Z_]\w*)\s*\)|CreateProcess\s*\(\s*NULL|ShellExecute\s*\(\s*NULL,\s*NULL",
                "title": "Process Execution with Variable Path — DLL Hijacking Risk",
                "description": "Passing a variable or unvalidated path to Process.Start, CreateProcess, or ShellExecute allows attackers to replace the target executable or place a malicious DLL with the same name in a directory that appears earlier in the search path, achieving code execution with the caller's privileges.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Use absolute, hardcoded paths to executables. Set ProcessStartInfo.UseShellExecute = false and specify the full path. Call SetDllDirectory(\"\") to disable current-directory DLL search. Sign all executables and verify signatures before loading.",
                "cwe_id": "CWE-427",
                "cvss_score": 9.3,
            },
            # ── Rule 3 ────────────────────────────────────────────────
            {
                "pattern": r"GC\.SuppressFinalize\s*\(",
                "title": "GC.SuppressFinalize — Verify Full IDisposable Pattern",
                "description": "GC.SuppressFinalize is only correct when paired with a complete IDisposable implementation. If the object acquires unmanaged resources (handles, COM objects, native memory) and Dispose() is not called, those resources leak until GC finalization — which may not run for minutes or hours under low memory pressure.",
                "severity": "High",
                "category": "Memory",
                "recommendation": "Implement the full IDisposable dispose pattern: public void Dispose() { Dispose(true); GC.SuppressFinalize(this); } protected virtual void Dispose(bool disposing) { if (disposing) { /* managed */ } /* unmanaged */ }. Use 'using' or 'await using' at all call sites.",
                "cwe_id": "CWE-401",
                "cvss_score": 6.5,
            },
            # ── Rule 4 ────────────────────────────────────────────────
            {
                "pattern": r"Thread\.Abort\s*\(\s*\)|thread\.Abort\s*\(",
                "title": "Thread.Abort() — Unsafe Asynchronous Exception",
                "description": "Thread.Abort() injects a ThreadAbortException at an arbitrary point — potentially inside a finally block, while holding a lock, or during CLR internal operations. This can leave resources unreleased, corrupt shared state, and cause unpredictable behavior. It is removed in .NET 5+.",
                "severity": "High",
                "category": "Performance",
                "recommendation": "Use CancellationToken for cooperative cancellation. Pass CancellationToken to async methods and check IsCancellationRequested at safe checkpoints. For blocking operations, use CancellationTokenSource.CancelAfter() with a timeout.",
                "cwe_id": "CWE-662",
                "cvss_score": 6.1,
            },
            # ── Rule 5 ────────────────────────────────────────────────
            {
                "pattern": r"Registry\.LocalMachine\.OpenSubKey\s*\([^)]*,\s*true\s*\)|RegistryKey\.OpenBaseKey\s*\(.*RegistryHive\.LocalMachine",
                "title": "Registry HKLM Write Without Elevation Check",
                "description": "Writing to HKEY_LOCAL_MACHINE requires administrator privileges. Attempting to write without checking elevation will either fail silently due to registry virtualization, throw UnauthorizedAccessException, or — in the worst case — succeed in a virtualized location that masquerades as the real key.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Check WindowsPrincipal.IsInRole(WindowsBuiltInRole.Administrator) before HKLM writes. Use a manifest with requestedExecutionLevel asInvoker if elevation isn't required. Prefer HKCU settings to avoid requiring elevation. Fail explicitly with a UAC prompt if elevation is needed.",
                "cwe_id": "CWE-269",
                "cvss_score": 6.5,
            },
            # ── Rule 6 ────────────────────────────────────────────────
            {
                "pattern": r"new\s+SecureString\s*\(\s*\)|SecureString\s+\w+\s*=\s*new",
                "title": "SecureString — Verify Disposal and Minimal Scope",
                "description": "SecureString protects data in encrypted memory, but provides no protection if: (1) it is not disposed promptly (data remains in encrypted memory until GC), (2) the content is marshaled to a regular string (data exposed in plaintext), or (3) the key is accessible from multiple threads without synchronization.",
                "severity": "Medium",
                "category": "Memory",
                "recommendation": "Always wrap SecureString in a 'using' block. Avoid calling Marshal.PtrToStringBSTR unless absolutely necessary. Consider that SecureString is deprecated in .NET 6+ — evaluate whether the threat model actually benefits from its protections vs. a Span<char> that is zeroed immediately.",
                "cwe_id": "CWE-316",
                "cvss_score": 5.5,
            },
            # ── Rule 7 ────────────────────────────────────────────────
            {
                "pattern": r"INTERNET_OPTION_SECURITY_FLAGS|SECURITY_FLAG_IGNORE_CERT|InternetSetOption.*INTERNET_OPTION",
                "title": "WinInet SSL Certificate Validation Disabled",
                "description": "Setting SECURITY_FLAG_IGNORE_CERT_CN_INVALID, SECURITY_FLAG_IGNORE_CERT_DATE_INVALID, or SECURITY_FLAG_IGNORE_REVOCATION via InternetSetOption disables TLS certificate checks in WinInet. This is often added to fix a certificate error in development and forgotten in production builds.",
                "severity": "High",
                "category": "Network",
                "recommendation": "Remove all SECURITY_FLAG_IGNORE_CERT_* flags from production code. Fix the underlying certificate issue (expired cert, CN mismatch, missing intermediate CA). Use INTERNET_OPTION_SECURITY_CERTIFICATE_STRUCT to inspect certificate details programmatically if needed.",
                "cwe_id": "CWE-295",
                "cvss_score": 8.1,
            },
            # ── Rule 8 ────────────────────────────────────────────────
            {
                "pattern": r"Marshal\.AllocHGlobal\s*\(|Marshal\.AllocCoTaskMem\s*\(",
                "title": "Unmanaged Memory Allocated Without Guaranteed Free",
                "description": "Marshal.AllocHGlobal and AllocCoTaskMem allocate memory outside the .NET GC heap. If the code throws between allocation and the corresponding Free call (missing finally block), the unmanaged memory leaks for the lifetime of the process — potentially gigabytes over time in long-running services.",
                "severity": "High",
                "category": "Memory",
                "recommendation": "Always free unmanaged memory in a finally block: IntPtr ptr = IntPtr.Zero; try { ptr = Marshal.AllocHGlobal(size); ... } finally { if (ptr != IntPtr.Zero) Marshal.FreeHGlobal(ptr); }. For ownership semantics, wrap in a SafeHandle subclass.",
                "cwe_id": "CWE-401",
                "cvss_score": 6.5,
            },
            # ── Rule 9 ────────────────────────────────────────────────
            {
                "pattern": r"catch\s*\(\s*Exception\s+\w+\s*\)\s*\{\s*\}|catch\s*\{\s*\}|catch\s*\(\s*Exception\s*\)\s*\{\s*(?:\/\/.*\n)?\s*\}",
                "title": "Empty Catch Block — Swallowed Exception",
                "description": "Catching all exceptions and doing nothing suppresses errors silently. Security exceptions (UnauthorizedAccessException, CryptographicException), I/O failures, and null reference errors that should abort an operation are silently ignored, leaving the application in an inconsistent state.",
                "severity": "Medium",
                "category": "Logic",
                "recommendation": "Catch only specific, expected exception types. Re-throw unexpected exceptions with 'throw;' (preserves stack trace). Log all caught exceptions with full stack trace and context. Add a global AppDomain.UnhandledException handler for last-resort logging.",
                "cwe_id": "CWE-390",
                "cvss_score": 5.3,
            },
            # ── Rule 10 ───────────────────────────────────────────────
            {
                "pattern": r"\[DllImport\s*\(|P/Invoke|extern\s+static\s+\w",
                "title": "P/Invoke Native Interop — Verify Marshaling Safety",
                "description": "P/Invoke calls bypass .NET's type safety. Incorrect calling conventions, wrong parameter types, missing SafeHandle usage, or improper string marshaling causes stack corruption, access violations, or undetected memory leaks that are extremely difficult to diagnose.",
                "severity": "Medium",
                "category": "Memory",
                "recommendation": "Validate all DllImport signatures against official C headers. Use SafeHandle for all native handles. Explicitly specify [MarshalAs] attributes for strings and arrays. In .NET 7+, prefer LibraryImport (source-generated P/Invoke) for better performance and AOT compatibility.",
                "cwe_id": "CWE-119",
                "cvss_score": 5.9,
            },
            # ── Rule 11 ───────────────────────────────────────────────
            {
                "pattern": r"(?:ConnectionString|connectionString)\s*=\s*[\"'][^\"']*(?:Password|pwd|User ID|UID)=[^\"']{3,}[\"']",
                "title": "Hardcoded Database Connection String with Credentials",
                "description": "Connection strings with embedded usernames, passwords, or integrated security tokens hardcoded in source code are exposed to anyone with repository access. Source code is frequently stored in version control, CI systems, and artifact servers — all of which should be considered potentially public.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Store connection strings in encrypted configuration (Windows DPAPI via ProtectedConfigurationProvider), environment variables, or Azure Key Vault / AWS Secrets Manager. Use Windows Authentication (Integrated Security=true) where possible to eliminate credential storage entirely.",
                "cwe_id": "CWE-798",
                "cvss_score": 9.1,
            },
            # ── Rule 12 ───────────────────────────────────────────────
            {
                "pattern": r"SqlCommand\s*\(\s*(?:[a-zA-Z_]\w*\s*\+|\"[^\"]*\"\s*\+)|\"SELECT.*\"\s*\+|\"UPDATE.*\"\s*\+|\"INSERT.*\"\s*\+|\"DELETE.*\"\s*\+",
                "title": "SQL Injection in ADO.NET — String Concatenation in Query",
                "description": "Concatenating user input directly into SQL command strings in ADO.NET allows SQL injection. Attackers can read or destroy the entire database, bypass authentication (OR 1=1), or execute extended stored procedures like xp_cmdshell to run OS commands.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Use SqlCommand with SqlParameter: cmd.Parameters.AddWithValue('@id', userId). For complex queries, use LINQ to SQL, Entity Framework, or Dapper with parameterized queries. Enable SQL Server's Transparent Data Encryption and auditing.",
                "cwe_id": "CWE-89",
                "cvss_score": 9.8,
            },
            # ── Rule 13 ───────────────────────────────────────────────
            {
                "pattern": r"XmlDocument\s*\(\s*\)|XmlTextReader\s*\(\s*\)|XDocument\.Load|XmlReader\.Create(?!.*DtdProcessing\.Prohibit)",
                "title": "XML External Entity (XXE) Injection",
                "description": "XML parsers in .NET that do not explicitly disable DTD processing are vulnerable to XXE injection. Attackers include an external entity reference in submitted XML to read arbitrary server files (/etc/passwd, web.config), perform SSRF, or trigger denial of service via entity expansion (billion laughs).",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "For XmlDocument: set xmlDoc.XmlResolver = null. For XmlReader: set settings.DtdProcessing = DtdProcessing.Prohibit and settings.XmlResolver = null. For XDocument.Load, wrap with XmlReader using those settings. Never enable DTD processing on untrusted XML.",
                "cwe_id": "CWE-611",
                "cvss_score": 9.1,
            },
            # ── Rule 14 ───────────────────────────────────────────────
            {
                "pattern": r"BinaryFormatter\s*\(\s*\)|new\s+BinaryFormatter|SoapFormatter|LosFormatter|ObjectStateFormatter",
                "title": "Insecure Deserialization via BinaryFormatter",
                "description": "BinaryFormatter.Deserialize() is the most dangerous deserialization sink in .NET. It executes arbitrary code during deserialization via gadget chains. Microsoft has removed it from .NET 5+ and backported security warnings to .NET Framework. Any use on untrusted data is a critical RCE vulnerability.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Remove BinaryFormatter entirely. Replace with System.Text.Json, Newtonsoft.Json, or Google.Protobuf for data exchange. If you must deserialize complex .NET object graphs, use MessagePack with a strict type resolver that allowlists expected types.",
                "cwe_id": "CWE-502",
                "cvss_score": 9.8,
            },
            # ── Rule 15 ───────────────────────────────────────────────
            {
                "pattern": r"Path\.Combine\s*\([^)]*(?:Request\.|HttpContext\.|userInput|input|param|query|fileName)[^)]*\)|File\.(?:Open|Read|Write|Delete)\s*\(\s*(?:[a-zA-Z_]\w*\s*\+|.*Request\.|.*userInput)",
                "title": "Path Traversal — User-Controlled File Path",
                "description": "Constructing file paths from user-supplied input without canonicalization allows path traversal attacks using ..\\..\\..\\windows\\system32\\config\\sam or URL-encoded variants. Attackers can read sensitive server files, overwrite application binaries, or delete critical system files.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Call Path.GetFullPath() on the constructed path and assert it starts with the expected base directory: if (!fullPath.StartsWith(allowedBase, StringComparison.OrdinalIgnoreCase)) throw. Reject any input containing '..' or null bytes. Use a virtual filesystem abstraction instead of direct paths.",
                "cwe_id": "CWE-22",
                "cvss_score": 8.6,
            },
            # ── Rule 16 ───────────────────────────────────────────────
            {
                "pattern": r"MD5CryptoServiceProvider\s*\(\s*\)|new\s+MD5CryptoServiceProvider|SHA1CryptoServiceProvider|new\s+SHA1CryptoServiceProvider|DESCryptoServiceProvider",
                "title": "Broken Cryptographic Algorithm — MD5 / SHA-1 / DES",
                "description": "MD5 and SHA-1 are broken for integrity and signature purposes. DES has a 56-bit key space crackable in hours. Using these for password hashing, HMAC, digital signatures, or key derivation undermines all security properties they are meant to provide.",
                "severity": "High",
                "category": "Crypto",
                "recommendation": "Use SHA256 or SHA512 for general hashing. Use HMACSHA256 for MACs. For password hashing use Rfc2898DeriveBytes (PBKDF2-SHA256) with >= 100,000 iterations or install BCrypt.Net-Next. Use AES with GCM mode via AesGcm in .NET Core 3.0+.",
                "cwe_id": "CWE-327",
                "cvss_score": 7.5,
            },
            # ── Rule 17 ───────────────────────────────────────────────
            {
                "pattern": r"static\s+(?:int|long|bool|string|List|Dictionary)\s+\w+\s*[;=]|Interlocked\.(?!Increment|Decrement|Exchange|CompareExchange)",
                "title": "Mutable Static Field — Potential Race Condition",
                "description": "Mutable static fields shared across threads without synchronization are a common source of race conditions in Windows services and ASP.NET applications. Reads and writes to reference types and 64-bit values are not guaranteed atomic on 32-bit systems.",
                "severity": "Medium",
                "category": "Performance",
                "recommendation": "Protect mutable static state with lock(), ReaderWriterLockSlim, or ConcurrentDictionary. Prefer immutable static fields (readonly) where possible. Use ThreadLocal<T> for per-thread storage. In ASP.NET, prefer scoped/transient DI lifetimes over static state.",
                "cwe_id": "CWE-362",
                "cvss_score": 5.9,
            },
            # ── Rule 18 ───────────────────────────────────────────────
            {
                "pattern": r"unchecked\s*\{|int\s+\w+\s*=\s*\(\s*int\s*\)\s*\w+\s*\*\s*\w+|Convert\.ToInt32\s*\([^)]*\*[^)]*\)",
                "title": "Integer Overflow in Unchecked Context",
                "description": "Integer arithmetic in C# defaults to unchecked mode, silently wrapping on overflow. Multiplication or addition of user-controlled values that overflow can produce negative buffer sizes, incorrect loop bounds, or exploit conditions (e.g., a large length wraps to a small negative value used as an array index).",
                "severity": "High",
                "category": "Memory",
                "recommendation": "Use the 'checked' keyword or project-level <CheckForOverflowUnderflow>true</CheckForOverflowUnderflow> to enable overflow detection. For security-critical arithmetic, use checked { } blocks explicitly. Validate that user-controlled numeric inputs are within safe ranges before arithmetic.",
                "cwe_id": "CWE-190",
                "cvss_score": 7.5,
            },
            # ── Rule 19 ───────────────────────────────────────────────
            {
                "pattern": r"Regex\s*\(\s*[\"'][^\"']*(?:\.\*|\.\+|\[.*\]\*|\[.*\]\+){2,}[\"']|Regex\.IsMatch\s*\(\s*(?:userInput|input|param|request)\s*,",
                "title": "Regular Expression Denial of Service (ReDoS)",
                "description": "Complex regex patterns with nested quantifiers (e.g., (a+)+ or (.+)*) evaluated against attacker-controlled input can cause catastrophic backtracking, consuming 100% CPU for seconds or minutes per request. This enables a single-request denial-of-service attack.",
                "severity": "High",
                "category": "Performance",
                "recommendation": "Use Regex.IsMatch with a timeout: new Regex(pattern, RegexOptions.None, TimeSpan.FromMilliseconds(100)). Catch RegexMatchTimeoutException and treat as invalid input. Use .NET 7+ source-generated Regex ([GeneratedRegex]) which emits optimal non-backtracking IL. Review patterns for nested quantifiers.",
                "cwe_id": "CWE-1333",
                "cvss_score": 7.5,
            },
            # ── Rule 20 ───────────────────────────────────────────────
            {
                "pattern": r"new\s+NamedPipeServerStream|CreateNamedPipe|PipeAccessRule",
                "title": "Named Pipe Without Proper Access Control",
                "description": "Named pipes created without explicit DACL (Discretionary Access Control List) restrictions inherit a default ACL that may allow all authenticated users (or even Everyone) to connect. A malicious local process can connect to the pipe, intercept data, or impersonate the server.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Create pipes with explicit PipeSecurity objects: var ps = new PipeSecurity(); ps.AddAccessRule(new PipeAccessRule(WindowsIdentity.GetCurrent().Name, PipeAccessRights.FullControl, AccessControlType.Allow)); Use impersonation (PipeImpersonationLevel.Impersonation) to verify client identity before serving requests.",
                "cwe_id": "CWE-732",
                "cvss_score": 7.1,
            },
            # ── Rule 21 ───────────────────────────────────────────────
            {
                "pattern": r"Response\.Write\s*\(.*(?:Request\.|input|param|query|userInput)|HttpResponse\.Write\s*\(.*Request",
                "title": "Cross-Site Scripting (XSS) in ASP.NET Response.Write",
                "description": "Writing user-supplied data directly to the HTTP response via Response.Write() without HTML encoding allows reflected XSS. Attackers craft URLs with injected script payloads that execute in the victim's browser, enabling session theft, keylogging, and DOM manipulation.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Use HttpUtility.HtmlEncode() before writing any user data to the response. In ASP.NET MVC/Razor, use @Html.Encode() or the automatic encoding in Razor @ expressions. Enable the [ValidateInput(true)] attribute and configure AntiXssEncoder as the default encoder.",
                "cwe_id": "CWE-79",
                "cvss_score": 8.8,
            },
            # ── Rule 22 ───────────────────────────────────────────────
            {
                "pattern": r"new\s+Thread\s*\(|ThreadPool\.QueueUserWorkItem|Task\.Run\s*\(\s*\(\s*\)\s*=>",
                "title": "Unhandled Exception in Background Thread — Silent App Crash",
                "description": "Unhandled exceptions thrown on background threads (Thread, ThreadPool, Task.Run) silently terminate the thread in .NET Framework (before 4.0) or crash the AppDomain in later versions. Exceptions in fire-and-forget Tasks are silently swallowed unless observed.",
                "severity": "Medium",
                "category": "Logic",
                "recommendation": "Wrap thread body in try/catch. For Task.Run, always await the result or attach .ContinueWith(t => HandleException(t.Exception), TaskContinuationOptions.OnlyOnFaulted). Configure TaskScheduler.UnobservedTaskException globally to catch escaping exceptions.",
                "cwe_id": "CWE-390",
                "cvss_score": 5.3,
            },
            # ── Rule 23 ───────────────────────────────────────────────
            {
                "pattern": r"string\s+\w+\s*=\s*\"[A-Za-z0-9+/]{20,}={0,2}\"|const\s+string\s+\w*(?:key|secret|password|token|pwd|api)\w*\s*=\s*\"",
                "title": "Hardcoded Secret or Cryptographic Key in Source",
                "description": "Secrets hardcoded as string literals in C# source files are embedded in the compiled assembly in plaintext. They can be extracted in seconds using dotPeek, ILSpy, or strings.exe on the binary — no source code access required. These secrets cannot be rotated without a new deployment.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Load secrets from environment variables, Windows DPAPI (ProtectedData.Protect), Azure Key Vault, or AWS Secrets Manager at runtime. Use the .NET Secret Manager for development. Never commit secrets to version control — use pre-commit hooks (git-secrets, truffleHog) to prevent this.",
                "cwe_id": "CWE-798",
                "cvss_score": 9.1,
            },
            # ── Rule 24 ───────────────────────────────────────────────
            {
                "pattern": r"Environment\.GetEnvironmentVariable\s*\(\s*\"PATH\"\s*\)|AppDomain\.CurrentDomain\.BaseDirectory|Directory\.GetCurrentDirectory\s*\(\s*\)",
                "title": "Application Base Directory Used for Security Decisions",
                "description": "Using AppDomain.CurrentDomain.BaseDirectory or GetCurrentDirectory() as the root for security checks or DLL loading is unsafe because these values can be controlled by attackers via PATH manipulation, symlinks, or working directory injection in some deployment scenarios.",
                "severity": "Medium",
                "category": "Security",
                "recommendation": "Use typeof(YourClass).Assembly.Location to get the actual assembly path. Validate that all loaded DLLs have valid Authenticode signatures before loading. Harden the application directory ACL to prevent non-admin writes. Use AppContext.BaseDirectory for deployment-relative paths.",
                "cwe_id": "CWE-427",
                "cvss_score": 5.9,
            },
            # ── Rule 25 ───────────────────────────────────────────────
            {
                "pattern": r"EventLog\.WriteEntry|EventLog\.Source\s*=|new\s+EventLog\s*\(",
                "title": "Sensitive Data Written to Windows Event Log",
                "description": "The Windows Event Log is accessible to all users in the Users group (read) and many administrators (read/write). Writing sensitive data (exception messages containing passwords, stack traces with connection strings, or raw request data) to the Event Log exposes it to all local users and log aggregation systems.",
                "severity": "Medium",
                "category": "Security",
                "recommendation": "Sanitize all data written to Event Log — strip connection strings, credentials, and PII. Log only error codes and correlation IDs, not raw exception messages containing sensitive context. Use structured logging (Serilog, NLog) with output enrichment to control what fields are emitted.",
                "cwe_id": "CWE-532",
                "cvss_score": 5.3,
            },
        ]
