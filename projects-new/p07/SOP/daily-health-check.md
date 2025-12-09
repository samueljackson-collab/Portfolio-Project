# SOP: Daily Health Check
- Verify Kafka topic lag < 500 messages.
- Confirm consumer error rate <0.1% via `roaming_errors_total`.
- Check backup CronJob success in last 24h.
- Rotate API keys expiring within 7 days.
- Review WAF logs for geo anomalies.
