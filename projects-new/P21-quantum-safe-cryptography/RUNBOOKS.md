# Runbooks

- Handshake failure: check server logs, confirm oqsprovider loaded, rerun client with --verbose
- Benchmark drift: rerun scripts/bench_pqc.sh, compare baselines, adjust CPU pinning
- Certificate refresh: run scripts/gen_certs.sh and restart demo containers
