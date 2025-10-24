# End-to-End Test Suite

This package contains resources for exercising the portfolio application from the outside: API validation, load testing, and security scanning.

## Structure
- `postman/collection.json` – Postman collection for REST workflows.
- `k6/` – Load testing scripts with ramping scenarios.
- `security/zap-scan.py` – Automates OWASP ZAP spider and active scan.
- `tests/test_api_flows.py` – Pytest suite that orchestrates full API flows.

## Usage
Install dependencies:
```bash
pip install -r requirements.txt
```

Run pytest flows:
```bash
pytest tests/test_api_flows.py
```

Run load tests:
```bash
k6 run k6/scenarios.js
```

Run security scan:
```bash
python security/zap-scan.py --target http://localhost:8000
```
