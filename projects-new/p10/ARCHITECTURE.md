# Architecture
- Two region services (region-a, region-b) exposing health and metrics.
- Simple traffic router script to emulate failover.
- K8s manifests provide Deployments per region and a failover Job.
