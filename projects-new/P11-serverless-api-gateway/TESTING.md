# Testing Strategy

- Run unit-style checks via the CLI harness in `jobs/demo_job.py` (no external deps).
- Validate the pipeline by executing `python docker/producer/main.py --validate` which ensures producer -> job -> consumer flow works.
- For container smoke tests, build the sample Dockerfile: `docker build -t demo-pipeline .`
