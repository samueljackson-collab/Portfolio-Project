# Scheduled jobs for `p09-cloud-native-poc`

This folder contains runnable maintenance and validation jobs that mirror the
lightweight patterns used across the prompt packs. Jobs are designed to run as
standalone scripts that can be scheduled by cron, Kubernetes CronJobs, or CI
pipelines.

## Available jobs

### `health_probe.py`
Minimal HTTP probe that emits a JSON line containing the endpoint tested,
latency, and whether the response matched the expected status code. It has no
external dependencies, making it safe to run in constrained environments.

**Run once (manual verification):**
```bash
python3 health_probe.py --url https://example.com/health --expected-status 200
```

**Cron example (every 5 minutes):**
```
*/5 * * * * cd /workspace/Portfolio-Project/projects-new/p09-cloud-native-poc/jobs && /usr/bin/python3 health_probe.py --url "https://api.example.com/health" --logfile /var/log/p09-health-probe.jsonl
```

**Kubernetes CronJob snippet:**
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: p09-health-probe
spec:
  schedule: "*/10 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: health-probe
              image: python:3.12-slim
              command: ["python", "health_probe.py"]
              args: ["--url", "http://app-svc:8080/health", "--logfile", "/var/log/health-probe.jsonl"]
              volumeMounts:
                - name: probe-log
                  mountPath: /var/log
          volumes:
            - name: probe-log
              emptyDir: {}
```

**Exit codes:**
- `0` when the probe matches the expected status code.
- `1` when the probe fails or returns an unexpected status.
