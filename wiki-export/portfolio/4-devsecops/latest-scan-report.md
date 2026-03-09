---
title: 🛡️ Trivy Security Scan Report
description: **Date:** December 19, 2025 **Target:** production-api:v2.4.1 **Scanner:** Trivy v0.48.0 **Package:** `libsqlite3` (3.34.0) **Fixed Version:** 3.34.1 **Description:** Heap-based buffer overflow in SQL
tags: [documentation, portfolio]
path: portfolio/4-devsecops/latest-scan-report
created: 2026-03-08T22:19:13.365425+00:00
updated: 2026-03-08T22:04:38.734902+00:00
---

# 🛡️ Trivy Security Scan Report
**Date:** December 19, 2025  
**Target:** production-api:v2.4.1  
**Scanner:** Trivy v0.48.0

## 📊 Summary
| Severity | Count | Status |
|----------|-------|--------|
| CRITICAL | 0     | ✅ PASS |
| HIGH     | 0     | ✅ PASS |
| MEDIUM   | 2     | ⚠️ WARN |
| LOW      | 5     | ℹ️ INFO |

## 🔍 Detailed Findings

### 🟠 MEDIUM: CVE-2025-1048 (libsqlite3)
**Package:** `libsqlite3` (3.34.0)  
**Fixed Version:** 3.34.1  
**Description:** Heap-based buffer overflow in SQLite prior to 3.34.1 allows attacker to execute arbitrary code.  
**Remediation:** `apt-get update && apt-get upgrade libsqlite3`

### 🔵 LOW: CVE-2024-8821 (zlib)
**Package:** `zlib` (1.2.11)  
**Description:** Out-of-bounds access in inflation method.  
**Status:** Patched in base image build #452.

---
**Pipeline Action:** Build PASSED (No Critical/High vulnerabilities found).
