# Incident Playbook — P07

## Playbook: Roaming Attach Failures Spiking
1. **Detect:** Alert `p07_roam_attach_error_rate` fires >5% for 5m.
2. **Triage:**
   - Check Grafana panel `Roaming Success Rate` for visited MCC/MNC hotspots.
   - Tail `logs/audit/audit.log` for `ROAMING_DENIED` reasons.
3. **Contain:**
   - Enable `SAFE_MODE=true` to throttle new attach attempts.
   - Capture PCAP for a failing subscriber using `make capture VISITED=208-01`.
4. **Remediate:**
   - Validate `config/roaming.yaml` agreements list; add missing MCC/MNC if intentional.
   - Restart mock VLR/HLR containers via `docker-compose restart vlr hlr`.
5. **Verify:**
   - Re-run `make test-smoke` and confirm alert clears in 10 minutes.
6. **Postmortem:**
   - File report using `REPORT_TEMPLATES/README.md` guidance with PCAP artifacts.
