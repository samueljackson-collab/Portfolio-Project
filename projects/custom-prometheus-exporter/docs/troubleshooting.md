# Troubleshooting

## Prometheus cannot scrape

- Verify the exporter is running: `curl http://localhost:9108/healthz`.
- Check firewall rules and service ports.
- Ensure Prometheus scrape config targets the correct address.

## Metrics missing

- Confirm collector feature flags are enabled.
- Review `metric_filter.disabled` for excluded metrics.
- Inspect logs for errors (`EXPORTER_LOG_LEVEL=debug`).

## API collector errors

- Validate API credentials in `headers`.
- Confirm `value_path` matches the JSON response.
- Adjust `timeout` for slower APIs.

## SQL collector errors

- Validate `driver`, `dsn`, and `query`.
- Ensure the database is reachable from the exporter host.

