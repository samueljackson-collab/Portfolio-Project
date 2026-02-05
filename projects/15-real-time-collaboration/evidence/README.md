# Evidence Log

## Multi-client session
- `collab_demo.html` includes the two-client WebSocket demo UI.
- `multi_client_demo.log` contains the client-side sync log.
- `server.log` contains server-side sync events.

## Load testing
- `load_test_results.csv` captures concurrent user latency results.
- `generate_load_chart.py` can recreate a chart from the CSV data.

## Scripts
- `run_multi_client_demo.py` reproduces the multi-client session.
- `load_test.py` and `generate_load_chart.py` reproduce the load test and chart.
