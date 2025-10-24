# End-to-End Testing Suite

This directory contains automated API, load, and security testing assets.

## Structure
- `postman/collection.json` – Postman collection covering auth and content flows.
- `k6/` – Load and stress test scenarios.
- `security/zap-scan.py` – OWASP ZAP automation script.
- `tests/test_api_flows.py` – Python tests orchestrating API journeys.

## Running

```bash
pip install -r requirements.txt
newman run postman/collection.json
k6 run k6/load-test.js
python security/zap-scan.py --target http://localhost:8000
```

