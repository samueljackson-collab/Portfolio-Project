from .base import BaseAnalyzer


class AndroidAnalyzer(BaseAnalyzer):
    platform = "android"

    def rules(self) -> list[dict]:
        return [
            # ── Rule 1 ────────────────────────────────────────────────
            {
                "pattern": r"Log\.(d|v|e|w|i)\s*\([^)]*(?:password|token|secret|key|auth|credential|ssn|credit|cvv|pin)[^)]*\)",
                "title": "Sensitive Data Leaked via Android Log",
                "description": "Sensitive data such as passwords, tokens, or credentials is being logged using Android's Log API. Log output is accessible to any app with READ_LOGS permission and is visible in ADB logcat, exposing credentials to attackers with physical or ADB access.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Remove all logging of sensitive data. Use ProGuard/R8 rules to strip log calls in release builds (`-assumenosideeffects class android.util.Log { *; }`). Never log passwords, tokens, session IDs, or PII.",
                "cwe_id": "CWE-532",
                "cvss_score": 7.5,
            },
            # ── Rule 2 ────────────────────────────────────────────────
            {
                "pattern": r"getSharedPreferences|SharedPreferences|PreferenceManager\.getDefaultSharedPreferences",
                "title": "Insecure Data Storage in SharedPreferences",
                "description": "SharedPreferences stores data in plaintext XML files on the device filesystem at /data/data/<package>/shared_prefs/. Any data stored here is accessible to root users, through ADB backup on non-encrypted devices, or via backup extraction on unencrypted devices.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Use EncryptedSharedPreferences (Jetpack Security library) for any sensitive values. For cryptographic keys, use Android Keystore exclusively. Never store plaintext passwords, session tokens, or PII in SharedPreferences.",
                "cwe_id": "CWE-312",
                "cvss_score": 7.1,
            },
            # ── Rule 3 ────────────────────────────────────────────────
            {
                "pattern": r"setJavaScriptEnabled\s*\(\s*true\s*\)",
                "title": "WebView JavaScript Enabled — XSS / RCE Risk",
                "description": "Enabling JavaScript in a WebView without strict URL allowlisting opens the app to Cross-Site Scripting attacks. If addJavascriptInterface() is also present, attackers who control the loaded content can invoke Java methods, potentially achieving Remote Code Execution.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Disable JavaScript unless absolutely necessary. If needed, use WebViewClient.shouldOverrideUrlLoading() to allowlist only trusted URLs. Avoid addJavascriptInterface() on API < 17. Consider Chrome Custom Tabs as a safer alternative.",
                "cwe_id": "CWE-79",
                "cvss_score": 9.3,
            },
            # ── Rule 4 ────────────────────────────────────────────────
            {
                "pattern": r"addJavascriptInterface\s*\(",
                "title": "addJavascriptInterface — JavaScript Bridge Exposes Java API",
                "description": "addJavascriptInterface() exposes annotated Java objects to JavaScript running in the WebView. On Android < 4.2 (API 17), all public methods of the registered object can be called by any JavaScript — including injected malicious scripts — enabling full RCE.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Ensure @JavascriptInterface annotation is used and minSdkVersion >= 17. Validate all data passed across the bridge. Load only trusted, HTTPS content. Prefer secure message-passing patterns. Combine with setJavaScriptEnabled checks.",
                "cwe_id": "CWE-749",
                "cvss_score": 9.8,
            },
            # ── Rule 5 ────────────────────────────────────────────────
            {
                "pattern": r"android:exported\s*=\s*\"true\"",
                "title": "Exported Android Component Without Permission Check",
                "description": "A component (Activity, Service, BroadcastReceiver, or ContentProvider) is exported without declaring a permission. Any app on the device can start, bind to, or query this component — potentially triggering privileged actions or reading sensitive data.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Add android:permission to the exported component. For ContentProviders set android:readPermission and android:writePermission. For components that don't need to be public, set android:exported=\"false\".",
                "cwe_id": "CWE-926",
                "cvss_score": 8.1,
            },
            # ── Rule 6 ────────────────────────────────────────────────
            {
                "pattern": r"new\s+X509TrustManager|checkClientTrusted|checkServerTrusted",
                "title": "Custom TrustManager — SSL Certificate Validation Bypassed",
                "description": "A custom X509TrustManager with empty or always-passing checkServerTrusted() bypasses TLS certificate validation, allowing man-in-the-middle attackers to intercept and modify all HTTPS traffic in cleartext. This is one of the most critical Android security vulnerabilities.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Never override certificate validation. Use the system default TrustManager. For certificate pinning use OkHttp's CertificatePinner or network-security-config. For testing, use a proxy with a trusted dev certificate, not a blank TrustManager.",
                "cwe_id": "CWE-295",
                "cvss_score": 9.0,
            },
            # ── Rule 7 ────────────────────────────────────────────────
            {
                "pattern": r"MODE_WORLD_READABLE|MODE_WORLD_WRITEABLE",
                "title": "World-Readable or World-Writable File Storage",
                "description": "Files created with MODE_WORLD_READABLE or MODE_WORLD_WRITEABLE can be read or written by any app on the device. This violates Android's sandbox model and exposes sensitive data to third-party apps.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Use MODE_PRIVATE (the default). To share files with other apps use a FileProvider and content:// URIs with explicit per-call permissions via Intent.FLAG_GRANT_READ_URI_PERMISSION.",
                "cwe_id": "CWE-732",
                "cvss_score": 6.5,
            },
            # ── Rule 8 ────────────────────────────────────────────────
            {
                "pattern": r"Runtime\.getRuntime\(\)\.exec\s*\(|ProcessBuilder\s*\(",
                "title": "Shell Command Execution — Command Injection Risk",
                "description": "Executing shell commands via Runtime.exec() or ProcessBuilder with user-controlled input enables command injection. Attackers append shell metacharacters (;, &&, |, $()) to run arbitrary commands with the app's UID permissions.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Avoid shell execution entirely. If unavoidable, pass arguments as separate array elements to ProcessBuilder — never concatenate user input into a command string. Allowlist and strictly validate all input values before use.",
                "cwe_id": "CWE-78",
                "cvss_score": 9.8,
            },
            # ── Rule 9 ────────────────────────────────────────────────
            {
                "pattern": r"PendingIntent\.get(?:Activity|Service|Broadcast|ForegroundService)\s*\([^)]*\)",
                "title": "PendingIntent Without FLAG_IMMUTABLE — Intent Hijacking",
                "description": "PendingIntents created without FLAG_IMMUTABLE (required on API 31+) can be modified by malicious apps before delivery. Attackers can change the intent's action, data, or component to escalate privileges or trigger unintended behavior in the target app.",
                "severity": "Medium",
                "category": "Security",
                "recommendation": "Always use FLAG_IMMUTABLE when creating PendingIntents unless mutation is strictly required. Use FLAG_MUTABLE only with inline documentation. On API 23+, combine with FLAG_UPDATE_CURRENT for updatable intents.",
                "cwe_id": "CWE-285",
                "cvss_score": 5.9,
            },
            # ── Rule 10 ───────────────────────────────────────────────
            {
                "pattern": r"Cipher\.getInstance\s*\(\s*\"AES\"\s*\)|Cipher\.getInstance\s*\(\s*\"AES/ECB",
                "title": "AES Without Mode (Defaults to ECB) — Weak Encryption",
                "description": "Using AES without specifying a mode defaults to ECB on most Android JCE providers. ECB mode is deterministic: identical plaintext blocks always produce identical ciphertext blocks, revealing data patterns and making the encryption trivially breakable.",
                "severity": "High",
                "category": "Crypto",
                "recommendation": "Use AES/GCM/NoPadding which provides authenticated encryption (AEAD). Generate a unique 96-bit IV for every encryption operation. Store the IV prepended to the ciphertext (IV is not secret but must be unique).",
                "cwe_id": "CWE-327",
                "cvss_score": 7.4,
            },
            # ── Rule 11 ───────────────────────────────────────────────
            {
                "pattern": r"rawQuery\s*\(\s*[\"']?.*\+|rawQuery\s*\(\s*.*(?:input|query|param|search|filter|user)\s*[+,]",
                "title": "SQL Injection in Android rawQuery()",
                "description": "Concatenating user input directly into rawQuery() strings allows SQL injection. Attackers can read or delete all data in the SQLite database, bypass authentication checks, or exfiltrate sensitive app data stored locally.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Use parameterized queries with selection args: db.rawQuery('SELECT * FROM t WHERE id=?', new String[]{userInput}). Better yet, use Room's @Query with parameters which enforces parameterization by design.",
                "cwe_id": "CWE-89",
                "cvss_score": 9.1,
            },
            # ── Rule 12 ───────────────────────────────────────────────
            {
                "pattern": r"new\s+Random\s*\(\s*\)|Math\.random\s*\(\s*\)|java\.util\.Random",
                "title": "java.util.Random Used for Security-Sensitive Operations",
                "description": "java.util.Random is a pseudo-random number generator seeded with a predictable value. Its output can be predicted after observing a small number of values. Using it for token generation, session IDs, nonces, or OTP codes creates guessable security-critical values.",
                "severity": "High",
                "category": "Crypto",
                "recommendation": "Use java.security.SecureRandom for all security-sensitive random value generation. For UUID generation use UUID.randomUUID() which internally uses SecureRandom. Never seed SecureRandom manually.",
                "cwe_id": "CWE-338",
                "cvss_score": 7.4,
            },
            # ── Rule 13 ───────────────────────────────────────────────
            {
                "pattern": r"ObjectInputStream\s*\(|readObject\s*\(\s*\)|deserializ",
                "title": "Unsafe Java Deserialization",
                "description": "Java object deserialization via ObjectInputStream.readObject() on untrusted data enables Remote Code Execution and privilege escalation. Attackers craft malicious serialized payloads using gadget chains from common libraries (Commons Collections, Spring, etc.).",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Never deserialize data from untrusted sources. Use JSON or Protobuf for data exchange. If deserialization is unavoidable, implement a validateObject() method in readObject() or use Apache Commons IO's ValidatingObjectInputStream with an explicit allowlist of trusted classes.",
                "cwe_id": "CWE-502",
                "cvss_score": 9.8,
            },
            # ── Rule 14 ───────────────────────────────────────────────
            {
                "pattern": r"getExternalStorageDirectory|getExternalFilesDir|Environment\.getExternal",
                "title": "Sensitive Data Written to External (World-Readable) Storage",
                "description": "Files written to external storage (SD card, shared storage) are accessible by any app with READ_EXTERNAL_STORAGE permission and visible to users via file managers. Sensitive data stored externally is effectively world-readable on unencrypted devices.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Store sensitive data only in internal storage (getFilesDir(), getCacheDir()). If external storage is required for sharing, use a FileProvider to serve the file via a content URI with scoped permissions rather than a direct path.",
                "cwe_id": "CWE-312",
                "cvss_score": 6.8,
            },
            # ── Rule 15 ───────────────────────────────────────────────
            {
                "pattern": r"sendStickyBroadcast|sendStickyOrderedBroadcast",
                "title": "Sticky Broadcast Exposes Persistent Sensitive Data",
                "description": "Sticky broadcasts persist in the system after being sent and can be retrieved by any app that later registers a receiver. Any sensitive data embedded in the broadcast Intent (tokens, user data, status) remains accessible indefinitely to all apps on the device.",
                "severity": "Medium",
                "category": "Security",
                "recommendation": "Replace sticky broadcasts with LocalBroadcastManager (or LiveData/Flow) for in-process communication. For inter-app communication, use explicit intents with declared permissions. Never embed sensitive data in broadcast Intents.",
                "cwe_id": "CWE-200",
                "cvss_score": 5.3,
            },
            # ── Rule 16 ───────────────────────────────────────────────
            {
                "pattern": r"ClipboardManager|setPrimaryClip|getPrimaryClip",
                "title": "Sensitive Data Written to System Clipboard",
                "description": "Data written to ClipboardManager.setPrimaryClip() is accessible by any foreground app without permission. Password managers, banking apps, or any app that reads the clipboard can silently exfiltrate credentials or tokens placed there.",
                "severity": "Medium",
                "category": "Security",
                "recommendation": "Avoid placing sensitive data (passwords, tokens, card numbers) in the clipboard. If clipboard copy is a UX requirement, clear the clipboard after 60 seconds using a delayed Handler.postDelayed(). In Android 13+ use ClipboardManager.clearPrimaryClip().",
                "cwe_id": "CWE-200",
                "cvss_score": 5.3,
            },
            # ── Rule 17 ───────────────────────────────────────────────
            {
                "pattern": r"android:debuggable\s*=\s*\"true\"",
                "title": "Application Debuggable in Production Build",
                "description": "Setting android:debuggable=\"true\" in the manifest allows anyone with ADB access to attach a debugger, inspect memory, read SharedPreferences, extract the database, and bypass security checks at runtime. This attribute should never be true in release builds.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Remove android:debuggable=\"true\" from the manifest entirely — release builds default to false. The build system (Gradle) sets it automatically based on build variant. Add a lint check to CI to reject any build with debuggable=true.",
                "cwe_id": "CWE-489",
                "cvss_score": 9.1,
            },
            # ── Rule 18 ───────────────────────────────────────────────
            {
                "pattern": r"HttpURLConnection|http://(?!localhost|127\\.0\\.0\\.1)",
                "title": "Cleartext HTTP Network Communication",
                "description": "Communicating over unencrypted HTTP transmits all data — including session tokens, credentials, and user data — in cleartext. Attackers on the same network can intercept and modify traffic via ARP spoofing or rogue WiFi access points.",
                "severity": "High",
                "category": "Network",
                "recommendation": "Upgrade all endpoints to HTTPS. Configure Network Security Config (network_security_config.xml) to deny cleartext traffic: <base-config cleartextTrafficPermitted=\"false\">. For legacy servers, use a TLS-terminating reverse proxy.",
                "cwe_id": "CWE-319",
                "cvss_score": 7.4,
            },
            # ── Rule 19 ───────────────────────────────────────────────
            {
                "pattern": r"HostnameVerifier|ALLOW_ALL_HOSTNAME_VERIFIER|verify\s*\(\s*String\s+hostname",
                "title": "Hostname Verification Disabled — MITM Vulnerability",
                "description": "Overriding HostnameVerifier to return true unconditionally, or using HttpsURLConnection.setHostnameVerifier(SSLSocketFactory.ALLOW_ALL_HOSTNAME_VERIFIER), disables hostname validation. Attackers can present any valid certificate for any domain to intercept traffic.",
                "severity": "Critical",
                "category": "Network",
                "recommendation": "Never override hostname verification in production. Use the default DefaultHostnameVerifier. Implement certificate pinning using network-security-config or OkHttp CertificatePinner for additional protection against CA compromise.",
                "cwe_id": "CWE-297",
                "cvss_score": 9.0,
            },
            # ── Rule 20 ───────────────────────────────────────────────
            {
                "pattern": r"WakeLock|PARTIAL_WAKE_LOCK|acquire\s*\(\s*\)(?![^;]*release)",
                "title": "WakeLock Acquired Without Guaranteed Release",
                "description": "A WakeLock acquired without a corresponding release() call in a finally block keeps the CPU awake indefinitely. This drains battery, can crash the device under low-memory conditions, and causes denial-of-service against the user's device.",
                "severity": "High",
                "category": "Battery",
                "recommendation": "Always release WakeLocks in a finally block: try { wl.acquire(timeout); doWork(); } finally { if (wl.isHeld()) wl.release(); }. Prefer using WorkManager with PowerManager constraints instead of raw WakeLocks.",
                "cwe_id": "CWE-400",
                "cvss_score": 5.9,
            },
            # ── Rule 21 ───────────────────────────────────────────────
            {
                "pattern": r"MessageDigest\.getInstance\s*\(\s*\"MD5\"|MessageDigest\.getInstance\s*\(\s*\"SHA-1\"|MessageDigest\.getInstance\s*\(\s*\"SHA1\"",
                "title": "Broken Hash Algorithm (MD5 / SHA-1) Used for Security",
                "description": "MD5 and SHA-1 are cryptographically broken. MD5 collisions can be generated in seconds on commodity hardware. SHA-1 was practically broken in 2017 (SHAttered attack). Neither should be used for password hashing, file integrity, digital signatures, or security tokens.",
                "severity": "High",
                "category": "Crypto",
                "recommendation": "Use SHA-256 or SHA-3 for general hashing and integrity checks. For password hashing, use BCrypt or Argon2 (available via Bouncy Castle). For HMAC, use HMAC-SHA256. Replace all MD5/SHA-1 usages in security-critical paths immediately.",
                "cwe_id": "CWE-327",
                "cvss_score": 7.5,
            },
            # ── Rule 22 ───────────────────────────────────────────────
            {
                "pattern": r"startActivity\s*\(.*getIntent\(\)\.getData\(\)|Intent\s*\(\s*[^)]*getStringExtra|intent\.getData\(\)\.toString\(\)",
                "title": "Deep Link / Intent Data Used Without Validation",
                "description": "Processing deep link URLs or Intent extras without validation allows attackers to craft malicious Intents that trigger unintended app behavior, bypass authentication screens, access protected data, or perform open redirects within the app.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Validate all Intent data and deep link parameters against an allowlist of expected values and URL patterns. Use the App Links API (digital asset links) to prevent Intent hijacking. Check Intent.resolveActivity() before following external URIs.",
                "cwe_id": "CWE-20",
                "cvss_score": 7.5,
            },
            # ── Rule 23 ───────────────────────────────────────────────
            {
                "pattern": r"loadUrl\s*\(\s*(?!\"https).*\)|loadUrl\s*\(\s*.*(?:input|data|url|param|request)",
                "title": "WebView.loadUrl() with Potentially Untrusted URL",
                "description": "Loading an unvalidated URL in WebView can direct the user to malicious sites, trigger local file:// access (reading device files via XHR), or execute javascript:// URIs as code within the app's context. Combined with JavaScript enabled, this is a critical attack vector.",
                "severity": "Critical",
                "category": "Security",
                "recommendation": "Validate URLs before calling loadUrl(). Enforce HTTPS-only with an allowlisted set of trusted domains. Override shouldOverrideUrlLoading() to block non-HTTPS and non-allowlisted domains. Block file://, javascript://, and data:// schemes explicitly.",
                "cwe_id": "CWE-601",
                "cvss_score": 8.8,
            },
            # ── Rule 24 ───────────────────────────────────────────────
            {
                "pattern": r"BroadcastReceiver(?!.*permission)|registerReceiver\s*\([^)]*\)",
                "title": "Unprotected BroadcastReceiver — Data Interception Risk",
                "description": "A BroadcastReceiver registered without a permission string can receive broadcasts from any app. Malicious apps can send crafted broadcasts to manipulate app behavior, trigger actions, or extract broadcast extras containing sensitive data.",
                "severity": "High",
                "category": "Security",
                "recommendation": "Register receivers with a signature-level permission. For receivers only needed in-process, use LocalBroadcastManager or a reactive pattern (RxJava, Flow). For system broadcasts, validate the sender's action string in onReceive() before processing.",
                "cwe_id": "CWE-925",
                "cvss_score": 6.5,
            },
            # ── Rule 25 ───────────────────────────────────────────────
            {
                "pattern": r"Context\.getDir\s*\(|getDatabasePath\s*\(|openOrCreateDatabase\s*\(",
                "title": "Database File Created Without Encryption",
                "description": "SQLite databases created with standard Android APIs are stored as unencrypted files in the app's data directory. On rooted devices, forensic extraction, or device seizure, all database contents are accessible in plaintext — including chat messages, cached tokens, and user records.",
                "severity": "Medium",
                "category": "Security",
                "recommendation": "Use SQLCipher to create encrypted databases with a user-derived key. For Room, use the Room-SQLCipher integration. Derive the database key from the Android Keystore rather than hardcoding it. Zero the key from memory immediately after opening.",
                "cwe_id": "CWE-311",
                "cvss_score": 5.9,
            },
        ]
