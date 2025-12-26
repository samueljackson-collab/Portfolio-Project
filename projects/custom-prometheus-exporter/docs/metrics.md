# Metrics Reference

## Exporter health

| Metric | Type | Description |
| --- | --- | --- |
| `custom_exporter_up` | Gauge | Whether the last scrape succeeded. |
| `custom_exporter_last_scrape_timestamp` | Gauge | Unix timestamp of last scrape. |
| `custom_exporter_scrape_duration_seconds` | Histogram | Total scrape duration. |
| `custom_exporter_scrape_errors_total` | Counter | Total scrape errors. |

## API collection

| Metric | Type | Description |
| --- | --- | --- |
| `custom_exporter_api_requests_total` | Counter | API requests executed. |
| `custom_exporter_api_request_duration_seconds` | Histogram | API request latency. |
| `custom_exporter_api_response_size_bytes` | Summary | API response size. |
| `custom_exporter_api_value` | Gauge | Value extracted from API response. |
| `custom_exporter_api_value_histogram` | Histogram | Distribution of API values. |
| `custom_exporter_api_value_summary` | Summary | Summary of API values. |

## File collection

| Metric | Type | Description |
| --- | --- | --- |
| `custom_exporter_file_value` | Gauge | Value parsed from file content. |
| `custom_exporter_file_read_errors_total` | Counter | File read errors. |

## SQL collection

| Metric | Type | Description |
| --- | --- | --- |
| `custom_exporter_sql_value` | Gauge | Value returned from SQL query. |
| `custom_exporter_sql_query_errors_total` | Counter | SQL query errors. |
