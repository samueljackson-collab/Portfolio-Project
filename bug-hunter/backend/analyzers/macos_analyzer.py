from .base import BaseAnalyzer


class MacOSAnalyzer(BaseAnalyzer):
    platform = "macos"

    def rules(self) -> list[dict]:
        return [
            # ── Rule 1 ────────────────────────────────────────────────
            {
                "pattern": r"NSTask\s*\(\s*\)|Process\s*\(\s*\)|task\.arguments\s*=.*(?:userInput|input|arg|param|value|request|query)",
                "title": "NSTask / Process with User-Controlled Arguments — Command Injection",
                "description": "Constructing NSTask (Process in Swift) arguments from user-controlled input enables command injection. If launchPath is /bin/sh with -c, attackers can append shell metacharacters (;, |, &&, $()) to execute arbitrary commands with the application's privileges and macOS entitlements.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Never pass user input directly to NSTask arguments. Use an allowlist for all input values. Avoid launchPath = '/bin/sh' with -c — set launchPath to the absolute path of the target binary and pass arguments as separate array elements. Validate input against a strict allowlist pattern.",
                "cwe_id": "CWE-78",
                "cvss_score": 9.8,
            },
            # ── Rule 2 ────────────────────────────────────────────────
            {
                "pattern": r"kSecAttrAccessibleAlways(?:ThisDeviceOnly)?",
                "title": "Keychain Accessible Always — Weakened Data-at-Rest Protection",
                "description": "kSecAttrAccessibleAlways / kSecAttrAccessibleAlwaysThisDeviceOnly allows Keychain items to be read regardless of whether the user is logged in or the screen is locked. This violates the principle of least privilege and weakens data-at-rest protection against physical attacks and cold-boot scenarios.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Use kSecAttrAccessibleWhenUnlocked for items only needed when the user is active. Use kSecAttrAccessibleAfterFirstUnlock for daemon/background items after system boot. Document each choice with a security justification comment.",
                "cwe_id": "CWE-522",
                "cvss_score": 6.8,
            },
            # ── Rule 3 ────────────────────────────────────────────────
            {
                "pattern": r"NSXPCConnection\s*\(|xpc_connection_create|xpc_connection_set_event_handler|xpc_connection_resume",
                "title": "XPC Service Without Caller Entitlement Validation",
                "description": "XPC services that don't validate the connecting process's code signature or entitlements accept connections from any local process. A malicious app can connect and invoke privileged helper methods, achieving local privilege escalation from a sandboxed context.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "In the XPC listener delegate, use SecCodeCopyGuestWithAttributes(NULL, attributes, kSecCSDefaultFlags, &code) and SecCodeCheckValidity(code, kSecCSDefaultFlags, requirement) to verify caller identity. Check com.apple.security.application-groups entitlements before serving requests.",
                "cwe_id": "CWE-284",
                "cvss_score": 8.8,
            },
            # ── Rule 4 ────────────────────────────────────────────────
            {
                "pattern": r"NSWorkspace\.shared\.open\s*\(|NSWorkspace\.shared\.openURL|openURL\s*\(",
                "title": "NSWorkspace.open() with Unvalidated URL — Open Redirect",
                "description": "Opening an unvalidated URL with NSWorkspace.shared.open() can launch any registered URL scheme handler on macOS. Attackers who control the URL can trigger file:// paths to launch local executables, custom scheme handlers in other apps, or phishing pages in the default browser.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Validate the URL scheme and host before calling NSWorkspace.open(). Allowlist permitted schemes (https, mailto). For deep links, use Universal Links with server-side app-site-association files. Display a confirmation dialog before opening external URLs from untrusted sources.",
                "cwe_id": "CWE-601",
                "cvss_score": 7.4,
            },
            # ── Rule 5 ────────────────────────────────────────────────
            {
                "pattern": r"\bsudo\b|chmod\s+[0-7]*7[0-7][0-7]\s+|chmod\s+a\+[rwx]+\s+|chmod\s+[ugo]*\+[rw]+\s+/",
                "title": "Overly Permissive Shell Permissions",
                "description": "Using sudo without hardening the PATH, or setting world-write permissions (chmod 777, chmod a+rwx) on files or directories, creates privilege escalation opportunities. Attackers who can write to world-writable directories can replace privileged executables or inject malicious scripts.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Harden sudo scripts: explicitly set PATH=/usr/bin:/bin at the top of privileged scripts. Never use 777 permissions — use 755 for executables, 644 for data files, 700 for private key directories. Validate file ownership before operating on them in privileged context.",
                "cwe_id": "CWE-732",
                "cvss_score": 7.8,
            },
            # ── Rule 6 ────────────────────────────────────────────────
            {
                "pattern": r"FileManager\.default\.createFile\s*\([^)]*attributes:\s*nil|\.write\s*\(to:[^)]*atomically:\s*true\)(?![\s\S]*?protectionKey)",
                "title": "File Created Without Explicit Protection Attributes",
                "description": "Files created with nil attributes on macOS do not automatically get encrypted data-at-rest protection. Unlike iOS which applies NSFileProtectionComplete by default for NSData.write(to:atomically:), macOS files only inherit the process umask and use no extra protection layer.",
                "severity": "Medium",
                "category": "Security",
                "recommendation": "Set explicit POSIX permissions (0o600 for user-only files) and consider encrypting sensitive file contents before writing using CryptoKit. Set immutable flag on integrity-critical files with chflags(). Store secrets in Keychain rather than as plain files.",
                "cwe_id": "CWE-732",
                "cvss_score": 5.5,
            },
            # ── Rule 7 ────────────────────────────────────────────────
            {
                "pattern": r"@autoreleasepool\s*\{|NSAutoreleasePool\s*\*\s*\w+\s*=\s*\[\[NSAutoreleasePool",
                "title": "Autorelease Pool Scope — Verify Memory Efficiency in Loops",
                "description": "Objective-C autorelease pools that are not drained frequently inside tight loops cause memory spikes. All objects added to the pool accumulate until the pool drains at the end of the run loop iteration. In tight loops processing large datasets, this can spike memory usage by orders of magnitude.",
                "severity": "Low",
                "category": "Memory",
                "recommendation": "Place @autoreleasepool { } inside the inner loop body, not outside it. In Swift, use autoreleasepool { } closure. Drain after each iteration or after processing each batch element. Profile with Instruments → Allocations to identify pool drain timing issues.",
                "cwe_id": "CWE-400",
                "cvss_score": 3.7,
            },
            # ── Rule 8 ────────────────────────────────────────────────
            {
                "pattern": r"FileManager\.default(?!.*per-thread)|NSFileManager\.defaultManager\(\)",
                "title": "NSFileManager Default Instance in Multi-Threaded Context",
                "description": "NSFileManager.defaultManager() is not thread-safe for use on threads other than the main thread. Concurrent file operations using the default instance can cause races, inconsistent state, and intermittent crashes that are nearly impossible to reproduce.",
                "severity": "Medium",
                "category": "Performance",
                "recommendation": "Create a new FileManager() instance per thread or GCD queue: let fm = FileManager(). The default instance is safe only on the main thread. For concurrent file processing, use per-task FileManager instances or serialize access through a dedicated serial queue.",
                "cwe_id": "CWE-362",
                "cvss_score": 5.9,
            },
            # ── Rule 9 ────────────────────────────────────────────────
            {
                "pattern": r"DispatchQueue\.main\.sync\s*\{|CFRunLoopPerformBlock.*kCFRunLoopCommonModes",
                "title": "DispatchQueue.main.sync — Deadlock When Called from Main Thread",
                "description": "Calling DispatchQueue.main.sync{} from the main thread deadlocks immediately and permanently. The main thread waits for the main queue to drain the block, which cannot happen because the main thread is blocked waiting. This causes a completely unresponsive application.",
                "severity": "High",
                "category": "Performance",
                "recommendation": "Never call DispatchQueue.main.sync from any code that may execute on the main thread. Use DispatchQueue.main.async for all UI updates from background threads. Check with Thread.isMainThread or dispatchPrecondition(condition: .onQueue(.main)) before sync calls.",
                "cwe_id": "CWE-833",
                "cvss_score": 6.5,
            },
            # ── Rule 10 ───────────────────────────────────────────────
            {
                "pattern": r"NSURLConnection\.sendSynchronousRequest|NSURLConnection\s*\(|[Uu][Rr][Ll]Connection",
                "title": "Deprecated NSURLConnection — Security and Performance Risk",
                "description": "NSURLConnection is deprecated since macOS 10.11. It lacks HTTP/2 support, has limited TLS configuration options, and its synchronous API blocks the calling thread. It does not receive security updates and known vulnerabilities in it may not be patched.",
                "severity": "Medium",
                "category": "Network",
                "recommendation": "Migrate to URLSession (NSURLSession). Use URLSession.shared for simple requests or create a custom URLSession with URLSessionConfiguration for certificate pinning, background transfers, and HTTP/2. Leverage async/await on macOS 12+ for clean asynchronous code.",
                "cwe_id": "CWE-477",
                "cvss_score": 5.3,
            },
            # ── Rule 11 ───────────────────────────────────────────────
            {
                "pattern": r"NSAppleScript\s*\(|NSAppleEventDescriptor|executeAndReturnError|osascript",
                "title": "AppleScript / OSAScript Execution with Potential Injection",
                "description": "Constructing AppleScript strings with user-controlled data enables AppleScript injection, which can execute arbitrary system commands, launch applications, access the filesystem, and interact with any scriptable application on the system including Mail, Safari, and the Finder.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Never interpolate user input into AppleScript source strings. Use Apple Events directly via NSAppleEventDescriptor for structured communication with specific applications. If AppleScript is unavoidable, treat all user data as literal strings using escaped AppleScript string literals.",
                "cwe_id": "CWE-78",
                "cvss_score": 9.3,
            },
            # ── Rule 12 ───────────────────────────────────────────────
            {
                "pattern": r"dlopen\s*\(|RTLD_GLOBAL|NSBundle\.load\s*\(|Bundle\.load\s*\(",
                "title": "Dynamic Library Loading — Potential Dylib Injection",
                "description": "Using dlopen() with a relative path or loading bundles from user-controlled paths is vulnerable to dylib injection via DYLD_INSERT_LIBRARIES or dylib hijacking. Attackers who place a malicious dylib in the search path can execute arbitrary code in the app's process.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Use absolute, hardcoded paths for dlopen(). Verify loaded library code signatures using SecStaticCodeCheckValidity before using any symbols. Disable DYLD_INSERT_LIBRARIES via the __restrict segment or hardened runtime entitlements. Enable Library Validation in Hardened Runtime.",
                "cwe_id": "CWE-426",
                "cvss_score": 8.1,
            },
            # ── Rule 13 ───────────────────────────────────────────────
            {
                "pattern": r"SQLite3_exec\s*\(.*(?:userInput|input|param|query|request)|sqlite3_exec\s*\([^,]+,\s*(?:[a-zA-Z_]\w*\s*,|\w+\s*\+)",
                "title": "SQLite SQL Injection via String Concatenation",
                "description": "Building SQLite query strings by concatenating user input allows SQL injection. Unlike server databases, SQLite on macOS apps stores local data — user records, messages, settings — that an attacker can exfiltrate or modify entirely through a single injected query.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Use sqlite3_prepare_v2() with ? placeholder parameters and sqlite3_bind_text/int/blob() to safely bind values. In Swift, use FMDB's executeQuery(withArgumentsIn:) or Core Data's NSPredicate with %K/%@ format strings which properly parameterize queries.",
                "cwe_id": "CWE-89",
                "cvss_score": 9.1,
            },
            # ── Rule 14 ───────────────────────────────────────────────
            {
                "pattern": r"NSXMLParser\s*\(\s*\)|XMLParser\s*\(\s*\)|NSXML(?:Document|Element|Node)",
                "title": "NSXMLParser — Verify XXE / External Entity Protection",
                "description": "NSXMLParser on macOS does not process external entities by default, but custom XMLParserDelegate implementations may inadvertently handle external entity callbacks. If shouldResolveExternalEntities is not explicitly false, XXE attacks can read arbitrary local files.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Ensure the XMLParser delegate does not implement parser(_:resolveExternalEntityName:systemID:). Set shouldResolveExternalEntities = false explicitly. For NSXML frameworks, configure NSXMLDocumentContentKind and use sanitized input. Validate XML against a schema before parsing.",
                "cwe_id": "CWE-611",
                "cvss_score": 7.5,
            },
            # ── Rule 15 ───────────────────────────────────────────────
            {
                "pattern": r"NSLog\s*\(@?[\"'][^\"']*(?:password|token|secret|key|auth|pin|ssn|credit)[^\"']*[\"']|NSLog\s*\(@?[\"'][^\"']*%[^\"']*[\"'],.*(?:password|token|secret)",
                "title": "Sensitive Data Logged via NSLog in macOS App",
                "description": "NSLog output is captured by the unified logging system and visible in Console.app, system.log, and via log stream on the terminal. On macOS, these logs persist on disk and may be included in crash reports, Feedback Assistant submissions, and diagnostic archives sent to Apple.",
                "severity": "Medium",
                "category": "Security",
                "recommendation": "Replace NSLog with os_log or os_signpost with privacy annotations: os_log('token: %{private}s', token). In Swift, use Logger (iOS 14 / macOS 11+). Audit all NSLog calls before release. Use a build flag to disable verbose logging in release builds.",
                "cwe_id": "CWE-532",
                "cvss_score": 5.3,
            },
            # ── Rule 16 ───────────────────────────────────────────────
            {
                "pattern": r"symlink\s*\(|link\s*\(|readlink\s*\(|lstat\s*\(",
                "title": "Symbolic Link (Symlink) Race Condition — TOCTOU",
                "description": "Checking whether a path is a symlink and then operating on the file is a Time-Of-Check-Time-Of-Use (TOCTOU) race condition. An attacker who controls the filesystem can replace a regular file with a symlink to /etc/sudoers or another privileged file between the check and the operation.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Use open() with O_NOFOLLOW to refuse to follow symlinks. On macOS, use openat() with AT_SYMLINK_NOFOLLOW. After opening, use fstat() on the file descriptor (not fstatat on the path) for all subsequent metadata checks. Never use separate stat() + open() sequences.",
                "cwe_id": "CWE-362",
                "cvss_score": 7.5,
            },
            # ── Rule 17 ───────────────────────────────────────────────
            {
                "pattern": r"let\s+\w+\s*=\s*try!\s+|guard\s+let\s+\w+\s*=\s*try\?|fatalError\s*\(\s*\)",
                "title": "Force Try or fatalError in Non-Bootstrap Code — Crash Risk",
                "description": "Using try! or fatalError() outside of application initialization code causes the app to terminate with an uncatchable error when conditions the developer assumed would never occur actually do occur in production. Unexpected nil or error conditions will crash rather than degrade gracefully.",
                "severity": "Medium",
                "category": "Crash",
                "recommendation": "Handle errors explicitly with do { try } catch { }. Reserve fatalError() for programming errors during development (wrong data type, invariant violations) with a clear message. In production code, prefer returning nil, throwing, or logging + recovering gracefully.",
                "cwe_id": "CWE-755",
                "cvss_score": 5.0,
            },
            # ── Rule 18 ───────────────────────────────────────────────
            {
                "pattern": r"UserDefaults\.standard\.set\s*\([^)]*(?:password|token|secret|key|auth|credential)[^)]*\)|defaults\s+write\s+.*(?:password|token|secret)",
                "title": "Sensitive Value Stored in UserDefaults on macOS",
                "description": "UserDefaults on macOS are stored in ~/Library/Preferences/<bundle-id>.plist in plaintext. These files are readable by any process running as the same user and are included in Time Machine backups without encryption, exposing credentials to any backup accessor.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Use the macOS Keychain via SecItemAdd/SecItemCopyMatching for all sensitive values. In Swift, use KeychainAccess or SwiftKeychainWrapper libraries. For inter-process sharing, use a Keychain item with a shared access group rather than UserDefaults.",
                "cwe_id": "CWE-312",
                "cvss_score": 7.1,
            },
            # ── Rule 19 ───────────────────────────────────────────────
            {
                "pattern": r"NSTask|Process\b(?!.*absolutePath)|launchPath\s*=\s*\"/bin/sh\"|launchPath\s*=\s*\"/usr/bin/env\"",
                "title": "Shell Launch Path Used in NSTask — Injection Surface",
                "description": "Setting NSTask.launchPath to /bin/sh or /usr/bin/env creates a shell interpretation layer where metacharacters in arguments gain special meaning. Even if arguments come from a \"trusted\" source, any upstream function that processes user input into those arguments becomes a code-injection risk.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Set launchPath to the absolute binary path (e.g., /usr/bin/find) and pass arguments as a separate String array — never through /bin/sh -c. This eliminates the shell interpretation layer entirely. Validate all input values against an allowlist before passing as arguments.",
                "cwe_id": "CWE-78",
                "cvss_score": 8.1,
            },
            # ── Rule 20 ───────────────────────────────────────────────
            {
                "pattern": r"SecKeychainAddGenericPassword|SecKeychainItemModifyAttributesAndData|SecKeychainFindGenericPassword",
                "title": "Legacy Keychain API Usage — Use Security Framework Modern APIs",
                "description": "The deprecated SecKeychain* APIs (SecKeychainAddGenericPassword etc.) have known security limitations: they use OS X password caching behavior, do not support modern access control primitives (ACL with biometrics), and are not available in sandboxed App Store apps.",
                "severity": "Medium",
                "category": "Security",
                "recommendation": "Migrate to the modern Security framework: SecItemAdd, SecItemCopyMatching, SecItemUpdate, SecItemDelete with CFDictionary attributes. Use kSecUseAuthenticationContext with LAContext for biometric-protected items. These APIs work correctly in sandboxed and non-sandboxed contexts.",
                "cwe_id": "CWE-477",
                "cvss_score": 5.3,
            },
            # ── Rule 21 ───────────────────────────────────────────────
            {
                "pattern": r"system\s*\(|popen\s*\(|exec[lv]p?\s*\(|posix_spawn\s*\(",
                "title": "POSIX system() / popen() / exec() — Command Injection",
                "description": "Calling system(), popen(), execl/execv/execvp with user-controlled strings on macOS enables shell command injection. These functions invoke /bin/sh to interpret the command string, meaning any shell metacharacter in user input becomes executable. This applies to any language with C bindings.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Replace system()/popen() with NSTask/Process using absolute binary paths and separate argument arrays. For execv variants, only pass pre-validated, allowlisted strings as arguments. Never pass user data through shell-interpreting functions even if 'partially sanitized'.",
                "cwe_id": "CWE-78",
                "cvss_score": 9.8,
            },
            # ── Rule 22 ───────────────────────────────────────────────
            {
                "pattern": r"DYLD_INSERT_LIBRARIES|DYLD_FRAMEWORK_PATH|DYLD_LIBRARY_PATH|getenv\s*\(\s*\"DYLD_",
                "title": "DYLD Environment Variable Read — Potential Dylib Injection Check",
                "description": "Reading DYLD_INSERT_LIBRARIES or other DYLD_ environment variables from getenv() may indicate an attempt to detect library injection. However, the Hardened Runtime disables DYLD_ variables for protected processes. Relying on getenv checks for security decisions is unreliable.",
                "severity": "Low",
                "category": "Security",
                "recommendation": "Enable Hardened Runtime entitlement (com.apple.security.cs.disable-library-validation: false) which automatically blocks DYLD_INSERT_LIBRARIES injection. Enable Library Validation to ensure only Apple-signed or team-signed libraries load. Do not rely on getenv() checks as a security control.",
                "cwe_id": "CWE-693",
                "cvss_score": 3.1,
            },
            # ── Rule 23 ───────────────────────────────────────────────
            {
                "pattern": r"NSPasteboard\.general\.(setString|setData|writeObjects)|NSPasteboard\.general\.string\(forType:",
                "title": "Sensitive Data Written to or Read from System Pasteboard",
                "description": "NSPasteboard.general is a shared system resource accessible to all running applications. Writing sensitive data (passwords, API keys, PII) to the general pasteboard allows any app in the foreground to silently read it. Reading from the pasteboard without user interaction may trigger privacy prompts in macOS 12+.",
                "severity": "Medium",
                "category": "Security",
                "recommendation": "Avoid placing sensitive data on NSPasteboard.general. Use NSPasteboard(name:) for in-app clipboard operations. Clear the pasteboard after use if sensitive data was placed there. For macOS 12+, request user permission before accessing clipboard contents from background contexts.",
                "cwe_id": "CWE-200",
                "cvss_score": 4.3,
            },
            # ── Rule 24 ───────────────────────────────────────────────
            {
                "pattern": r"\.contains\s*\(\s*\"\.\.\"|\.\./|path\.hasSuffix\s*\(\"[^\"]*\.\.[^\"]*\"\)|filePath.*\+.*userInput|filePath.*\+.*input",
                "title": "Path Traversal in File Operation",
                "description": "Constructing file paths from user-controlled input on macOS allows path traversal using ../ sequences to escape the intended directory. Attackers can read ~/.ssh/id_rsa, ~/Library/Keychains/, application preferences, or overwrite critical application files.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Use URL(fileURLWithPath:relativeTo:) to resolve paths against a base directory and verify the resulting URL starts with the intended base path. Reject any input containing '..' or null bytes. Use FileManager.default.containerURL(forSecurityApplicationGroupIdentifier:) for shared group directories.",
                "cwe_id": "CWE-22",
                "cvss_score": 8.6,
            },
            # ── Rule 25 ───────────────────────────────────────────────
            {
                "pattern": r"SMJobBless|AuthorizationExecuteWithPrivileges|AuthorizationCreate",
                "title": "Privileged Helper Tool Installation — Verify Validation",
                "description": "SMJobBless installs a privileged helper tool with root privileges. If the helper's code signing requirements, plist version strings, or bundle ID checks are not properly validated, attackers can replace the helper binary during the installation window or install a malicious tool with the same label.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Set strict code signing requirements in the helper's Info.plist. Validate bundle version and code signature in AuthorizationExecuteWithPrivileges callbacks. Use SMAppService (macOS 13+) as the modern replacement. Implement inter-process validation using the XPC connection's audit token.",
                "cwe_id": "CWE-284",
                "cvss_score": 7.5,
            },
        ]
