# Runbook: Investigate Kafka Consumer Lag
1. Confirm alert source and affected environment.
2. Inspect consumer lag:
   ```sh
   kubectl -n roaming-sim exec deploy/roaming-consumer -- kafka-consumer-groups --bootstrap-server kafka:9092 \
     --describe --group roaming-consumer
   ```
3. If lag increasing:
   - Check CPU/memory on pods: `kubectl top pods -n roaming-sim`.
   - Verify DB latency in metrics `roaming_db_write_seconds`.
4. Mitigations:
   - Scale consumer: `kubectl -n roaming-sim scale deploy/roaming-consumer --replicas=4`.
   - Enable autoscaling if disabled: `kubectl -n roaming-sim apply -f k8s/hpa-consumer.yaml`.
5. Validate recovery: lag trending down within 10 minutes.
6. Update incident report and handoff.
