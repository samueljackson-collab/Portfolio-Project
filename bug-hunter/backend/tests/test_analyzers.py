"""Unit tests for the platform analyzers — verifies known vulnerable code produces expected findings."""
from __future__ import annotations
import pytest

from analyzers.android_analyzer import AndroidAnalyzer
from analyzers.ios_analyzer import IOSAnalyzer
from analyzers.windows_analyzer import WindowsAnalyzer
from analyzers.macos_analyzer import MacOSAnalyzer
from analyzers.web_analyzer import WebAnalyzer
from analyzers.base import RawFinding


def _collect(analyzer, code: str, filename: str = "test") -> list[RawFinding]:
    return analyzer.analyze(code, filename)


def _titles(findings: list[RawFinding]) -> set[str]:
    return {f.title for f in findings}


# ── Android ──────────────────────────────────────────────────────────────────

# Triggers "SQL Injection in Android rawQuery()" — pattern: rawQuery\s*\(\s*[\"']?.*\+
ANDROID_SQL = 'db.rawQuery("SELECT * FROM users WHERE id = " + userId, null);'

# Triggers "WebView JavaScript Enabled" — pattern: setJavaScriptEnabled\s*\(\s*true\s*\)
ANDROID_WEBVIEW = "webView.setJavaScriptEnabled(true);"

# Triggers "Sensitive Data Leaked via Android Log" — pattern: Log\.(d|v|e|w|i)\s*\(.*password...
ANDROID_LOG = 'Log.d("Auth", "password=" + pass);'


def test_android_sql_injection_detected():
    findings = _collect(AndroidAnalyzer(), ANDROID_SQL, "UserDao.java")
    assert any("SQL" in t or "rawQuery" in t for t in _titles(findings)), \
        f"Expected SQL injection finding, got: {_titles(findings)}"


def test_android_webview_js_enabled_detected():
    findings = _collect(AndroidAnalyzer(), ANDROID_WEBVIEW, "MyActivity.java")
    assert any("JavaScript" in t or "WebView" in t for t in _titles(findings)), \
        f"Expected WebView JavaScript finding, got: {_titles(findings)}"


def test_android_log_leak_detected():
    findings = _collect(AndroidAnalyzer(), ANDROID_LOG, "Auth.java")
    assert any("Log" in t or "Sensitive" in t for t in _titles(findings)), \
        f"Expected log leak finding, got: {_titles(findings)}"


def test_android_analyzer_has_25_rules():
    assert len(AndroidAnalyzer().rules()) == 25


# ── iOS ───────────────────────────────────────────────────────────────────────

# Triggers "Sensitive Data Logged in Production Code" — pattern: NSLog\s*\([^)]*(?:password|token...)
IOS_NSLOG = 'NSLog(@"Auth: password=%@ token=%@", password, token);'

# Triggers "Weak or Broken Cryptographic Primitive" — pattern: MD5|...
IOS_MD5 = "let digest = CC_MD5(data, CC_LONG(data.count), &result)"

# Triggers "App Transport Security (ATS) Disabled"
# pattern: NSAllowsArbitraryLoads\s*=\s*(?:YES|true|1)
IOS_ATS = "NSAllowsArbitraryLoads = YES"


def test_ios_nslog_detected():
    findings = _collect(IOSAnalyzer(), IOS_NSLOG, "AuthController.m")
    assert len(findings) > 0, f"Expected NSLog finding, got nothing"


def test_ios_weak_crypto_md5_detected():
    findings = _collect(IOSAnalyzer(), IOS_MD5, "Crypto.m")
    assert any("MD5" in t or "Weak" in t or "Crypto" in t or "Broken" in t for t in _titles(findings)), \
        f"Expected weak crypto finding, got: {_titles(findings)}"


def test_ios_ats_disabled_detected():
    findings = _collect(IOSAnalyzer(), IOS_ATS, "Info.plist")
    assert any("ATS" in t or "Transport" in t or "Arbitrary" in t for t in _titles(findings)), \
        f"Expected ATS finding, got: {_titles(findings)}"


def test_ios_analyzer_has_25_rules():
    assert len(IOSAnalyzer().rules()) == 25


# ── Windows ───────────────────────────────────────────────────────────────────

# Triggers "Hardcoded Database Connection String with Credentials"
# pattern: (?:ConnectionString|connectionString)\s*=\s*[\"'][^\"']*(?:Password|pwd|User ID|UID)=
WINDOWS_CONN = 'string ConnectionString = "Server=sql;Database=app;User ID=sa;Password=secret123;";'

# Triggers "Process Execution with Variable Path — DLL Hijacking Risk"
# pattern: Process\.Start\s*\(\s*(?:[a-zA-Z_]\w*)\s*\)
WINDOWS_PROC = "Process.Start(command);"


def test_windows_hardcoded_connection_detected():
    findings = _collect(WindowsAnalyzer(), WINDOWS_CONN, "Database.cs")
    assert any("Connection" in t or "Credential" in t or "Hardcoded" in t for t in _titles(findings)), \
        f"Expected hardcoded connection finding, got: {_titles(findings)}"


def test_windows_process_variable_path_detected():
    findings = _collect(WindowsAnalyzer(), WINDOWS_PROC, "Shell.cs")
    assert any("Process" in t or "DLL" in t or "Execution" in t for t in _titles(findings)), \
        f"Expected process injection finding, got: {_titles(findings)}"


def test_windows_analyzer_has_25_rules():
    assert len(WindowsAnalyzer().rules()) == 25


# ── macOS ─────────────────────────────────────────────────────────────────────

# Triggers "NSTask Shell Injection Risk" or similar
MACOS_SHELL = "system([NSString stringWithFormat:@\"ls %@\", userInput].UTF8String);"


def test_macos_shell_injection_detected():
    findings = _collect(MacOSAnalyzer(), MACOS_SHELL, "Runner.m")
    assert len(findings) > 0, f"Expected at least one finding, got nothing"


def test_macos_analyzer_has_25_rules():
    assert len(MacOSAnalyzer().rules()) == 25


# ── Web ───────────────────────────────────────────────────────────────────────

# Triggers "eval() — Arbitrary JavaScript Execution"
WEB_EVAL = "eval(userInput);"


def test_web_eval_detected():
    findings = _collect(WebAnalyzer(), WEB_EVAL, "server.js")
    assert any("eval" in t.lower() for t in _titles(findings)), \
        f"Expected eval finding, got: {_titles(findings)}"


def test_web_analyzer_has_25_rules():
    assert len(WebAnalyzer().rules()) == 25


# ── Clean code ────────────────────────────────────────────────────────────────

CLEAN_JAVA = """
public class Hello {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
"""


def test_clean_code_has_no_critical_findings():
    findings = _collect(AndroidAnalyzer(), CLEAN_JAVA, "Hello.java")
    critical = [f for f in findings if f.severity == "Critical"]
    assert len(critical) == 0, f"Clean code should not have Critical findings: {[f.title for f in critical]}"


# ── Risk score ────────────────────────────────────────────────────────────────

def test_risk_score_computation():
    from services.scan_service import compute_risk_score

    findings = [
        RawFinding("A", "", "Critical", "", "web", 1, "", "", None, None, ""),
        RawFinding("B", "", "High", "", "web", 2, "", "", None, None, ""),
        RawFinding("C", "", "Medium", "", "web", 3, "", "", None, None, ""),
        RawFinding("D", "", "Low", "", "web", 4, "", "", None, None, ""),
    ]
    # 1*25 + 1*10 + 1*4 + 1*1 = 40
    assert compute_risk_score(findings) == 40.0


def test_risk_score_capped_at_100():
    from services.scan_service import compute_risk_score

    findings = [RawFinding("X", "", "Critical", "", "web", i, "", "", None, None, "") for i in range(10)]
    assert compute_risk_score(findings) == 100.0
