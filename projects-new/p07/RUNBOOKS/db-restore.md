# Runbook: Restore PostgreSQL
1. Pause consumers to prevent new writes:
   ```sh
   kubectl -n roaming-sim scale deploy/roaming-consumer --replicas=0
   ```
2. Locate latest backup artifact in S3 bucket `roaming-backups`.
3. Run restore job:
   ```sh
   kubectl -n roaming-sim create job --from=cronjob/db-backup db-restore-$(date +%s) \
     --dry-run=client -o yaml | kubectl apply -f -
   ```
4. Monitor job logs until successful completion.
5. Run smoke query:
   ```sh
   kubectl -n roaming-sim exec deploy/roaming-consumer -- psql $POSTGRES_DSN -c "select count(*) from roaming_events limit 1"
   ```
6. Resume consumers: scale back to previous replica count and watch metrics.
