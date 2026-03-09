from app.scanner import scan_page


def test_scan_detects_insecure_patterns():
    url = "http://example.com/page?id=1&debug=true&token=abc"
    findings = scan_page(url)
    rule_names = [finding.rule for finding in findings]

    assert "PLAIN_HTTP" in rule_names
    assert "DEBUG_FLAG" in rule_names
    assert "IDENTIFIER_PARAM" in rule_names
    assert "TOKEN_IN_QUERY" in rule_names


def test_scan_ignores_clean_https_urls():
    url = "https://secure.example.com/dashboard"
    findings = scan_page(url)

    assert findings == []
