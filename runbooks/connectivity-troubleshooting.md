# Connectivity Troubleshooting Decision Tree

Use this decision flow to isolate networking and service reachability issues.

## Decision tree
1. **Is DNS resolving?**
   - No: check `/etc/resolv.conf`, CoreDNS/Route53 health; flush local cache.
   - Yes: continue.
2. **Is the host reachable (ping/TCP)?**
   - No: validate security groups/NSGs, NACLs, and route tables for the source subnet. Check IGW/NAT attachment and AZ route propagation.
   - Yes: continue.
3. **Is TLS/HTTP responding?**
   - No: confirm load balancer listener/target group health; inspect cert expiration; verify inbound security group rules for 80/443.
   - Yes: continue.
4. **Is the application healthy?**
   - No: review application logs, pod status, and liveness/readiness probes. Roll back recent deploy if probes failing.
   - Yes: continue.
5. **Is downstream dependency available?**
   - No: check database endpoint connectivity, SGs, and subnet ACLs; retry with bastion from same subnet. Validate RDS subnet group spans correct AZs.
   - Yes: open incident with evidence (traces, metrics, curl outputs).

## Quick checks
- `dig <host>` for DNS; `curl -v https://<host>/healthz` for HTTP.
- `aws ec2 describe-route-tables --filters Name=vpc-id,Values=<vpc>` to confirm routes.
- `kubectl describe endpoints <svc>` to ensure pods are registered.

## Escalation
- If P1/P2: page on-call, capture traceroute, curl with `--trace-ascii`, and ArgoCD rollout history. Attach screenshots of Grafana dashboards and Jaeger traces.
