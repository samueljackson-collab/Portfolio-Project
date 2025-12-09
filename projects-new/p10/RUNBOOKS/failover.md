# Runbook: Trigger Failover
1. Confirm alert source and impacted region.
2. Run router script to switch traffic:
   ```sh
   python docker/router/failover.py --target region-b
   ```
3. Validate /health on region-b returns 200.
4. Post update in status channel every 15 minutes.
