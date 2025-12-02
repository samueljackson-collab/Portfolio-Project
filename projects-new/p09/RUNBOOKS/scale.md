# Runbook: Scale Consumer
1. Check metrics `poc_consumer_lag`.
2. Scale deployment: `kubectl -n cloud-poc scale deploy/poc-consumer --replicas=3`.
3. Verify lag decrease within 5 minutes.
