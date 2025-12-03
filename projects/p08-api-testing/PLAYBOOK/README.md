# Incident Playbook — P08

## Playbook: 5xx Errors in Payment API
1. **Detect:** Alert `p08_payment_5xx_rate` firing >2% over 5m.
2. **Triage:** Inspect Newman JUnit for failing requests; identify correlation IDs.
3. **Contain:** Switch environment to mock payment provider by setting `USE_MOCK_PAYMENTS=true` and rerun smoke suite.
4. **Remediate:** Compare response schemas to contracts; engage backend team with failing payloads.
5. **Verify:** Re-run `make test-payment` against staging; ensure error rate alert clears.
6. **Document:** File defect report using template with correlation IDs and curl repro.
