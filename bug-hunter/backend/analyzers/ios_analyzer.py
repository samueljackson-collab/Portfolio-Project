from .base import BaseAnalyzer


class IOSAnalyzer(BaseAnalyzer):
    platform = "ios"

    def rules(self) -> list[dict]:
        return [
            # ── Rule 1 ────────────────────────────────────────────────
            {
                "pattern": r"UserDefaults\.standard\.set\s*\([^)]*(?:password|token|secret|key|auth|ssn|pin|credential)[^)]*\)|NSUserDefaults.*setObject.*(?:password|token|secret)",
                "title": "Sensitive Data Stored in NSUserDefaults / UserDefaults",
                "description": "UserDefaults stores data in an unencrypted plist file at Library/Preferences/<bundle-id>.plist. Passwords, tokens, or session data stored here are readable on jailbroken devices, via iTunes/iCloud backup extraction, or through filesystem forensics without device decryption.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Store sensitive values in the iOS Keychain using SecItemAdd / SecItemCopyMatching, or use a Keychain wrapper (KeychainAccess, SwiftKeychainWrapper). Use kSecAttrAccessibleWhenUnlockedThisDeviceOnly to prevent backup extraction.",
                "cwe_id": "CWE-312",
                "cvss_score": 7.1,
            },
            # ── Rule 2 ────────────────────────────────────────────────
            {
                "pattern": r"kSecAttrAccessibleAlways(?:ThisDeviceOnly)?",
                "title": "Keychain Item Accessible When Device Is Locked",
                "description": "kSecAttrAccessibleAlways or kSecAttrAccessibleAlwaysThisDeviceOnly allows the Keychain item to be read even when the device is locked, including after a device restart before the user has authenticated. This weakens data-at-rest protection against physical attacks.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Use kSecAttrAccessibleWhenUnlockedThisDeviceOnly for items accessed during active use. Use kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly only for background-accessible items — and document the justification. Never use kSecAttrAccessibleAlways.",
                "cwe_id": "CWE-522",
                "cvss_score": 6.8,
            },
            # ── Rule 3 ────────────────────────────────────────────────
            {
                "pattern": r"NSLog\s*\([^)]*(?:password|token|secret|key|auth|credential|ssn|pin)[^)]*\)|print\s*\([^)]*(?:password|token|secret)[^)]*\)",
                "title": "Sensitive Data Logged in Production Code",
                "description": "NSLog and print output is visible in Console.app, Xcode debug console, and via idevicesyslog by anyone with physical or USB access to the device. Logging credentials or tokens in production builds exposes them trivially to attackers with device access.",
                "severity": "Medium",
                "category": "Security",
                "recommendation": "Wrap all debug logging in #if DEBUG / #endif. Use os_log with the .private data formatter: os_log('token: %{private}s', token). Strip all production logging of sensitive values before App Store submission.",
                "cwe_id": "CWE-532",
                "cvss_score": 5.3,
            },
            # ── Rule 4 ────────────────────────────────────────────────
            {
                "pattern": r"NSAllowsArbitraryLoads\s*=\s*(?:YES|true|1)|NSExceptionAllowsInsecureHTTPLoads\s*=\s*(?:YES|true|1)",
                "title": "App Transport Security (ATS) Disabled",
                "description": "Setting NSAllowsArbitraryLoads to YES disables Apple's App Transport Security globally, permitting cleartext HTTP connections to any server. All network traffic is exposed to man-in-the-middle attacks on untrusted WiFi, intercepting session tokens and user data.",
                "severity": "High",
                "category": "Network",
                "recommendation": "Remove NSAllowsArbitraryLoads. Migrate all server endpoints to HTTPS/TLS 1.2+. If a single legacy endpoint requires HTTP, scope the exception to that domain only using NSExceptionDomains. Apple may reject apps with blanket ATS exceptions.",
                "cwe_id": "CWE-319",
                "cvss_score": 7.4,
            },
            # ── Rule 5 ────────────────────────────────────────────────
            {
                "pattern": r"(?<!\w)(\w+)!\.",
                "title": "Force Unwrap of Optional — Production Crash Risk",
                "description": "Force-unwrapping an Optional with ! crashes the application with EXC_BAD_INSTRUCTION if the value is nil. Force unwraps in network callbacks, Core Data results, view hierarchy lookups, or JSON parsing are frequent sources of unreproducible production crashes.",
                "severity": "Medium",
                "category": "Crash",
                "recommendation": "Replace force unwraps with guard let / if let / nil-coalescing (??). For truly impossible nils, prefer preconditionFailure('...') with an explanatory message over !. Adopt SwiftLint rule force_unwrapping to catch these in CI.",
                "cwe_id": "CWE-476",
                "cvss_score": 5.0,
            },
            # ── Rule 6 ────────────────────────────────────────────────
            {
                "pattern": r"(?:var|let)\s+delegate\s*(?::|=)(?!\s*weak)|protocol\s+\w+Delegate(?!.*AnyObject)",
                "title": "Strong Delegate Reference — Retain Cycle / Memory Leak",
                "description": "Declaring a delegate property as strong (the default) while the delegate also retains the delegating object creates a retain cycle. Both objects are kept alive indefinitely, leaking memory and preventing deallocation for the lifetime of the session.",
                "severity": "Medium",
                "category": "Memory",
                "recommendation": "Always declare delegate properties as `weak var delegate: MyDelegate?` where MyDelegate is class-bound (`protocol MyDelegate: AnyObject`). Add a Memory Graph Debugger check in Instruments to detect retain cycles pre-release.",
                "cwe_id": "CWE-401",
                "cvss_score": 4.3,
            },
            # ── Rule 7 ────────────────────────────────────────────────
            {
                "pattern": r"UIPasteboard\.general\.(string|url|image|items|setValue|setData)\s*=",
                "title": "Sensitive Data Written to System Pasteboard",
                "description": "Writing sensitive values to UIPasteboard.general makes them accessible to all foreground apps without permission. On iOS 16+, a notification banner announces pasteboard access to users. Third-party apps monitoring the pasteboard can silently copy credentials.",
                "severity": "Medium",
                "category": "Security",
                "recommendation": "Avoid placing passwords or tokens on the general pasteboard. If copy is required for UX, clear the pasteboard after 60 seconds. Use a private named pasteboard for in-app clipboard operations. For credentials, use AutoFill framework instead.",
                "cwe_id": "CWE-200",
                "cvss_score": 4.3,
            },
            # ── Rule 8 ────────────────────────────────────────────────
            {
                "pattern": r"UIWebView|WKWebView.*loadHTMLString\s*\(.*(?:userInput|input|data|param|request)|webView.*loadRequest",
                "title": "WebView Loading Untrusted or User-Controlled Content",
                "description": "Loading HTML constructed from user-controlled data in UIWebView or WKWebView without a Content Security Policy enables XSS. UIWebView is also deprecated since iOS 8 and has known security issues. Combined with messageHandlers, attackers can bridge JS to native Swift code.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Migrate all UIWebView to WKWebView. Set a strict Content Security Policy. Sanitize all dynamic HTML content with an allowlisted parser. Restrict WKScriptMessageHandler registration. Use decidePolicyFor navigationAction to allowlist URLs.",
                "cwe_id": "CWE-79",
                "cvss_score": 7.5,
            },
            # ── Rule 9 ────────────────────────────────────────────────
            {
                "pattern": r"arc4random(?!_uniform)|\.random\(in:\)|Int\.random\(|Double\.random\(",
                "title": "Non-Cryptographic Randomness Used in Security Context",
                "description": "Swift's arc4random() without _uniform, and Int/Double.random(in:), use the system random number generator that, while reasonable for UI randomness, should not be used as the sole entropy source for security tokens, nonces, or IVs without verification.",
                "severity": "Low",
                "category": "Crypto",
                "recommendation": "For all security-sensitive random values (tokens, nonces, IVs, salts), use SecRandomCopyBytes(kSecRandomDefault, count, &buffer). In Swift, use the CryptoKit framework's SymmetricKey or AES.GCM.Nonce which uses secure entropy internally.",
                "cwe_id": "CWE-338",
                "cvss_score": 3.7,
            },
            # ── Rule 10 ───────────────────────────────────────────────
            {
                "pattern": r"URLSession\.shared\.(?:dataTask|downloadTask|uploadTask)",
                "title": "URLSession.shared Without Certificate Pinning",
                "description": "URLSession.shared uses default configuration with no certificate pinning. An attacker who compromises a Certificate Authority (or performs a MITM with a fraudulently issued cert) can intercept all HTTPS traffic from this session without detection.",
                "severity": "Low",
                "category": "Network",
                "recommendation": "Create a dedicated URLSession with a custom URLSessionDelegate implementing urlSession(_:didReceive:completionHandler:) for certificate pinning. Use CryptoKit to verify public key hashes. Alternatively use TrustKit for managed pinning with bypass protection.",
                "cwe_id": "CWE-295",
                "cvss_score": 3.1,
            },
            # ── Rule 11 ───────────────────────────────────────────────
            {
                "pattern": r"NSTemporaryDirectory\s*\(\s*\)|FileManager\.default\.temporaryDirectory|tmp/",
                "title": "Sensitive File Written to Temporary Directory",
                "description": "The temporary directory is not encrypted and may survive across reboots on some iOS versions. Files written there are excluded from NSFileProtection and can be accessed by other processes on jailbroken devices or extracted via iTunes backups if protection is not set.",
                "severity": "Medium",
                "category": "Security",
                "recommendation": "Set NSFileProtectionComplete on any sensitive files: try FileManager.default.setAttributes([.protectionKey: FileProtectionType.complete], ofItemAtPath: path). Delete temporary files immediately after use rather than letting them linger.",
                "cwe_id": "CWE-312",
                "cvss_score": 5.3,
            },
            # ── Rule 12 ───────────────────────────────────────────────
            {
                "pattern": r"LAContext\(\)\.evaluatePolicy|localAuthentication|biometricType",
                "title": "Biometric Authentication Without Fallback Validation",
                "description": "LAContext.evaluatePolicy() can fall back to device passcode if biometrics fail or are unavailable. If the caller does not check whether authentication succeeded via Keychain-bound operations (rather than just the callback boolean), an attacker with device passcode knowledge bypasses biometric intent.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Do not use LAContext biometric success as the sole gate for sensitive operations. Instead, protect the sensitive key or data in the Keychain with kSecAccessControlBiometryCurrentSet or kSecAccessControlUserPresence — the OS enforces biometric binding at the Keychain level.",
                "cwe_id": "CWE-287",
                "cvss_score": 7.0,
            },
            # ── Rule 13 ───────────────────────────────────────────────
            {
                "pattern": r"SCNetworkReachability|Reachability\.forInternetConnection|reachabilityForLocalWiFi",
                "title": "Network Reachability Used as Security Gate",
                "description": "Using SCNetworkReachability to decide whether to validate SSL or skip security checks is a security anti-pattern. Network state can change between the check and the actual connection, and this pattern is frequently exploited to bypass TLS validation logic in poor implementations.",
                "severity": "Low",
                "category": "Network",
                "recommendation": "Never use reachability as a condition to skip security checks. Apply security measures (TLS, certificate validation) unconditionally. Use reachability only for UX purposes (showing offline banners) and let URLSession handle actual connectivity gracefully.",
                "cwe_id": "CWE-362",
                "cvss_score": 3.1,
            },
            # ── Rule 14 ───────────────────────────────────────────────
            {
                "pattern": r"try!\s+|try!\s+\w|= try!",
                "title": "Force Try (try!) — Unhandled Error Causes Crash",
                "description": "Using try! forces execution of a throwing expression and crashes with EXC_BAD_INSTRUCTION if an error is thrown. In production code, especially around I/O, decryption, JSON parsing, or database operations, unexpected errors are inevitable and will bring down the app.",
                "severity": "Medium",
                "category": "Crash",
                "recommendation": "Replace try! with do { try ... } catch { handle(error) } or try? where nil on failure is acceptable. Reserve try! only for truly infallible operations (loading a bundled resource that ship with the app) and document why the throw is impossible.",
                "cwe_id": "CWE-755",
                "cvss_score": 5.0,
            },
            # ── Rule 15 ───────────────────────────────────────────────
            {
                "pattern": r"addObserver\s*\(.*selector:|NotificationCenter\.default\.addObserver",
                "title": "NotificationCenter Observer Not Removed — Memory Leak",
                "description": "Adding a NotificationCenter observer without removing it in deinit or viewDidDisappear causes the observer to remain registered after the observed object is deallocated. On iOS < 9, receiving a notification on a deallocated observer crashes with EXC_BAD_ACCESS.",
                "severity": "Medium",
                "category": "Memory",
                "recommendation": "Store the observation token from the closure-based addObserver(forName:) and invalidate it in deinit. For selector-based registration, call NotificationCenter.default.removeObserver(self) in deinit. Prefer the token-based API on iOS 9+ — it auto-removes on token deallocation.",
                "cwe_id": "CWE-401",
                "cvss_score": 4.3,
            },
            # ── Rule 16 ───────────────────────────────────────────────
            {
                "pattern": r"performSelector|perform\s*\(\s*#selector|performSelector\s*\(onMainThread",
                "title": "performSelector — Bypasses ARC Memory Management",
                "description": "performSelector: is a dynamic dispatch mechanism that bypasses ARC's retain/release tracking. The compiler cannot determine the return type of the called method, so the return value is not retained. This causes dangling pointers and memory corruption when the result is used.",
                "severity": "Medium",
                "category": "Memory",
                "recommendation": "Replace performSelector with direct method calls, closures, or protocol-based dispatch. For delayed execution use DispatchQueue.main.asyncAfter(). For cross-thread calls use DispatchQueue or OperationQueue with explicit retain semantics.",
                "cwe_id": "CWE-119",
                "cvss_score": 4.9,
            },
            # ── Rule 17 ───────────────────────────────────────────────
            {
                "pattern": r"NSURLConnection\.sendSynchronousRequest|URLSession.*\.data\(for:.*\)\s*//.*sync|DispatchSemaphore.*wait.*URLSession",
                "title": "Synchronous Network Request on Main Thread — UI Freeze",
                "description": "Making synchronous network requests on the main thread blocks the run loop, freezing the UI for the duration of the request. iOS watchdog kills apps that block the main thread for more than ~8 seconds, causing user-visible crashes with no error dialog.",
                "severity": "High",
                "category": "Performance",
                "recommendation": "Use async/await (iOS 15+) or completion handler-based URLSession.dataTask(with:completionHandler:). Never use DispatchSemaphore.wait() to synchronize network calls on the main thread. NSURLConnection is deprecated — migrate to URLSession.",
                "cwe_id": "CWE-400",
                "cvss_score": 6.5,
            },
            # ── Rule 18 ───────────────────────────────────────────────
            {
                "pattern": r"\.write\s*\(to:.*isExcludedFromBackup|excludedFromBackup\s*=\s*false|isExcludedFromBackup\s*=\s*false",
                "title": "Sensitive File Not Excluded from iCloud / iTunes Backup",
                "description": "Files stored in the app's Documents directory are included in iCloud and iTunes backups by default. Sensitive data (databases, cached tokens, encryption keys) backed up to iCloud can be accessed by anyone with access to the user's Apple ID or who extracts a local iTunes backup.",
                "severity": "Medium",
                "category": "Security",
                "recommendation": "Exclude sensitive files from backup: var resourceValues = URLResourceValues(); resourceValues.isExcludedFromBackup = true; try fileURL.setResourceValues(resourceValues). Store sensitive data in Library/Application Support and set excluded from backup.",
                "cwe_id": "CWE-312",
                "cvss_score": 5.5,
            },
            # ── Rule 19 ───────────────────────────────────────────────
            {
                "pattern": r"UNNotificationRequest|UNMutableNotificationContent|userInfo\[.*(?:token|secret|key|password|auth)",
                "title": "Sensitive Data in Push Notification Payload",
                "description": "Push notification payloads are visible on the lock screen, in Notification Center, and are stored by APNs. Embedding sensitive data (tokens, account numbers, health data) in notification payloads exposes it to shoulder surfers, and to anyone with access to the device's lock screen.",
                "severity": "Medium",
                "category": "Security",
                "recommendation": "Never include sensitive data in notification payloads. Send a notification ID and fetch the full data securely when the user opens the app. Use NSE (Notification Service Extension) to decrypt payloads on-device if end-to-end encryption is required.",
                "cwe_id": "CWE-200",
                "cvss_score": 5.3,
            },
            # ── Rule 20 ───────────────────────────────────────────────
            {
                "pattern": r"MD5|CommonCrypto.*kCCAlgorithmDES|CCKeyDerivationPBKDF.*kCCPRFHmacAlgSHA1",
                "title": "Weak or Broken Cryptographic Primitive",
                "description": "MD5 is broken for collision resistance, DES has a 56-bit key space brutable in hours with modern hardware, and PBKDF2 with SHA-1 provides weaker key stretching than with SHA-256. Using these in security-critical operations (password storage, session token generation) is cryptographically unsound.",
                "severity": "High",
                "category": "Crypto",
                "recommendation": "Use CryptoKit: AES.GCM for authenticated encryption, SHA256 or SHA512 for hashing, HKDF for key derivation. For password hashing use PBKDF2 with SHA-256 and >= 100,000 iterations. Avoid DES, 3DES, RC4, and MD5 entirely.",
                "cwe_id": "CWE-327",
                "cvss_score": 7.4,
            },
            # ── Rule 21 ───────────────────────────────────────────────
            {
                "pattern": r"\.allowsCellularAccess\s*=\s*false|allowsCellularAccess",
                "title": "Network Access Restriction May Create Unexpected App Behavior",
                "description": "Setting allowsCellularAccess = false on URLSessionConfiguration silently fails all requests when only cellular is available, with no error message to the user. This can cause data loss or silent operation failures that are difficult to debug in production.",
                "severity": "Low",
                "category": "Network",
                "recommendation": "Handle network availability via URLError.notConnectedToInternet and URLError.networkConnectionLost error cases. Show user-visible feedback rather than relying on session-level cellular restrictions. Use NWPathMonitor for explicit connectivity status.",
                "cwe_id": "CWE-400",
                "cvss_score": 3.1,
            },
            # ── Rule 22 ───────────────────────────────────────────────
            {
                "pattern": r"isJailbroken|jailbreak|cydia|substrate|saurik|MobileSubstrate",
                "title": "Jailbreak Detection — Verify Implementation Completeness",
                "description": "Jailbreak detection routines are security theatre if implemented naively (checking for Cydia.app path, writability of /private). Attackers use Liberty Lite, Shadow, or tsProtector to bypass these checks. Incomplete detection gives false confidence while not deterring determined attackers.",
                "severity": "Low",
                "category": "Security",
                "recommendation": "Implement multi-layered jailbreak detection: check for suspicious files AND suspicious directory writability AND environment variable injection (DYLD_INSERT_LIBRARIES) AND process detection. Use IOSSecuritySuite or commercial solutions (Appdome, Guardsquare) for comprehensive coverage.",
                "cwe_id": "CWE-693",
                "cvss_score": 3.7,
            },
            # ── Rule 23 ───────────────────────────────────────────────
            {
                "pattern": r"DispatchQueue\.main\.sync\s*\{|CFRunLoopRun\s*\(\s*\)|RunLoop\.main\.run\s*\(",
                "title": "Potential Main Thread Deadlock",
                "description": "Calling DispatchQueue.main.sync{} from the main thread deadlocks immediately — the main thread waits for itself to drain the queue. CFRunLoopRun called inside a sync block on the main queue can similarly produce an unrecoverable freeze.",
                "severity": "High",
                "category": "Performance",
                "recommendation": "Never use DispatchQueue.main.sync from code that may execute on the main thread. Use DispatchQueue.main.async for UI updates from background threads. If you need to check the current queue, use dispatchPrecondition(condition: .onQueue(.main)).",
                "cwe_id": "CWE-833",
                "cvss_score": 6.5,
            },
            # ── Rule 24 ───────────────────────────────────────────────
            {
                "pattern": r"openURL\s*\(|application\s*\(.*open\s+url|UIApplication\.shared\.open\s*\(",
                "title": "Unvalidated URL Scheme Redirect",
                "description": "Opening external URLs or custom scheme URLs without validation allows attackers to craft deep links that open phishing pages in Safari, trigger sensitive URL scheme actions in other apps, or redirect the user away from trusted content unexpectedly.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Validate URL scheme and host before calling openURL. Allowlist accepted schemes (https, mailto, tel) and hosts. For deep links, use Apple's Universal Links (HTTPS with server-side verification) instead of custom URL schemes. Display a confirmation dialog for external URLs.",
                "cwe_id": "CWE-601",
                "cvss_score": 7.4,
            },
            # ── Rule 25 ───────────────────────────────────────────────
            {
                "pattern": r"String\s*\(format:\s*[\"'][^\"']*%[^\"']*[\"'],.*(?:input|userInput|param|data|request)",
                "title": "Format String with User-Controlled Input",
                "description": "Passing user-controlled strings as format arguments to String(format:) can cause unexpected output, crashes, or — when bridged to C/Objective-C sprintf functions — format string vulnerabilities. Attackers can use %n, %x, %s specifiers to read memory or crash the process.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Never pass user input as a format string argument. Use String interpolation (\"\\(value)\") which is always safe. If format strings are necessary, use a fixed format string with typed %@ placeholders and pass user data as arguments, not as the format itself.",
                "cwe_id": "CWE-134",
                "cvss_score": 7.5,
            },
        ]
