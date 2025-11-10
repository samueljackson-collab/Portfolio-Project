# Kuiper System/Network Administrator - Hands-On Lab Index

**Purpose:** Practical exercises to build muscle memory and demonstrate skills
**Goal:** Complete 15 core labs before interview + 5 optional advanced labs
**Timeline:** 2 weeks (see learning path)
**Last Updated:** 2025-11-10

---

## How to Use This Lab Index

1. **Labs are ordered by difficulty** - start with Foundation, progress to Advanced
2. **Each lab has clear objectives** - know what you're building before you start
3. **Document everything** - screenshots, configs, results
4. **Map to your portfolio** - create evidence in your Portfolio-Project repository
5. **Reference in interview** - "I built this in my homelab..." is gold

---

## Lab Status Key

- 🔴 **Not Started** - Haven't begun this lab yet
- 🟡 **In Progress** - Currently working on it
- 🟢 **Completed** - Finished with evidence documented
- ⭐ **Critical** - Must complete before interview
- 🎯 **Interview Showcase** - Plan to discuss in interview

---

## Foundation Labs (Week 1)

### Lab 01: TC Netem Satellite Link Simulation ⭐🎯
**Difficulty:** 🟢 Beginner
**Time:** 2-3 hours
**Technologies:** Linux tc netem, iperf3, bash scripting
**Risk:** 🟢 LOW (safe to run on test VM)
**Objective:** Simulate satellite link conditions (latency, jitter, packet loss) and measure impact

**What You'll Build:**
- Script to apply netem rules (30ms delay, 10ms jitter, 0.5% loss)
- Script to revert to normal
- Baseline performance test with iperf3
- Satellite simulation test with iperf3
- CSV results comparing before/after
- Grafana dashboard (if possible) showing metrics

**Success Criteria:**
- ✅ Can apply and revert netem rules without breaking network
- ✅ Measured latency increase (~30ms), jitter (~10ms), packet loss (~0.5%)
- ✅ Documented results with screenshots
- ✅ Understand why this matters for satellite operations

**Portfolio Location:**
`projects/06-homelab/PRJ-HOME-002/experiments/satellite-link-simulation/`

**Files to Create:**
```
apply-satellite-profile.sh
revert-to-normal.sh
baseline-test.sh
satellite-test.sh
results/
  baseline.csv
  satellite.csv
  comparison.png
README.md (methodology, findings, lessons learned)
```

**Learning Resources:**
- `man tc-netem`
- https://netbeez.net/blog/how-to-use-the-linux-traffic-control/
- https://www.excentis.com/blog/use-linux-traffic-control-impairment-node-test-environment-part-1

---

### Lab 02: AWS VPC with Public/Private Subnets ⭐
**Difficulty:** 🟢 Beginner
**Time:** 2-3 hours
**Technologies:** Terraform, AWS VPC, NAT Gateway, Internet Gateway
**Risk:** 🟡 MEDIUM (costs $1-2/day if left running)
**Objective:** Build foundational VPC architecture using Infrastructure as Code

**What You'll Build:**
- VPC with CIDR 10.1.0.0/16
- 2 public subnets (10.1.1.0/24, 10.1.2.0/24) in different AZs
- 2 private subnets (10.1.10.0/24, 10.1.11.0/24) in different AZs
- Internet Gateway for public subnets
- NAT Gateway in public subnet for private subnet egress
- Route tables properly configured
- Security groups (bastion, app, database tiers)

**Success Criteria:**
- ✅ EC2 in public subnet can reach internet directly
- ✅ EC2 in private subnet can reach internet via NAT Gateway
- ✅ `terraform plan` shows no drift
- ✅ Can destroy and recreate identically

**Portfolio Location:**
`projects/p01-aws-infra/` or `terraform/aws-vpc-foundation/`

**Files to Create:**
```
vpc.tf
subnets.tf
route_tables.tf
security_groups.tf
outputs.tf
variables.tf
terraform.tfvars.example
README.md
```

**Learning Resources:**
- https://docs.aws.amazon.com/vpc/latest/userguide/
- https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/vpc

---

### Lab 03: Transit Gateway with Two VPCs ⭐🎯
**Difficulty:** 🟡 Intermediate
**Time:** 3-4 hours
**Technologies:** Terraform, AWS Transit Gateway, VPC attachments, routing
**Risk:** 🟡 MEDIUM (costs ~$2/day for TGW)
**Objective:** Build hub-and-spoke network with Transit Gateway

**What You'll Build:**
- Transit Gateway in us-east-1
- VPC A (10.1.0.0/16) attached to TGW
- VPC B (10.2.0.0/16) attached to TGW
- TGW route table configured for transitive routing
- VPC route tables pointing to TGW for cross-VPC traffic
- Test: EC2 in VPC A can ping EC2 in VPC B

**Success Criteria:**
- ✅ TGW has 2 VPC attachments in "available" state
- ✅ TGW route table shows both VPC CIDRs
- ✅ VPC A → VPC B connectivity verified with ping/curl
- ✅ VPC Flow Logs showing TGW traffic
- ✅ Can explain when to use TGW vs VPC peering

**Portfolio Location:**
`projects/p03-hybrid-network/tgw-foundation/` or `terraform/aws-tgw-basic/`

**Files to Create:**
```
tgw.tf
vpc_a.tf
vpc_b.tf
tgw_attachments.tf
route_tables.tf
test_instances.tf
outputs.tf
README.md (include decision rationale)
evidence/
  tgw-console-screenshot.png
  ping-test.png
  vpc-flow-logs.png
```

**Learning Resources:**
- https://docs.aws.amazon.com/vpc/latest/tgw/
- https://aws.amazon.com/blogs/networking-and-content-delivery/creating-a-single-internet-exit-point-from-multiple-vpcs-using-aws-transit-gateway/

---

### Lab 04: Site-to-Site VPN with BGP ⭐🎯
**Difficulty:** 🟡 Intermediate-Advanced
**Time:** 4-6 hours
**Technologies:** Terraform, AWS VPN, BGP, customer gateway (pfSense/VyOS VM or cloud router)
**Risk:** 🟡 MEDIUM (complexity, costs ~$1/day)
**Objective:** Build production-grade VPN with dynamic routing

**What You'll Build:**
- Customer Gateway (CGW) resource representing your on-prem router
- Site-to-Site VPN connection to Transit Gateway with BGP enabled
- On-prem router config (pfSense, VyOS, or simulated with EC2 + StrongSwan)
- BGP peering established (169.254.x.x link-local addresses)
- Route advertisement from both sides
- CloudWatch dashboard for tunnel state, BGP state, throughput

**Success Criteria:**
- ✅ Both VPN tunnels UP
- ✅ BGP session ESTABLISHED (show ip bgp summary)
- ✅ Routes exchanged (show ip bgp, show ip route)
- ✅ Traffic flowing through tunnel (ping, curl)
- ✅ CloudWatch metrics showing healthy tunnels
- ✅ Can failover between tunnels (test ECMP or active/standby)

**Portfolio Location:**
`projects/p03-hybrid-network/vpn-bgp/` or `terraform/aws-vpn-bgp/`

**Files to Create:**
```
cgw.tf
vpn_connection.tf
tgw_attachment.tf
cloudwatch_dashboard.json
on_prem_router_config/
  strongswan.conf (or vyos-config.txt, or pfsense-backup.xml)
  bgp-config.txt
test_results/
  show-ip-bgp-summary.txt
  show-ip-route.txt
  tunnel-state-screenshot.png
  cloudwatch-dashboard.png
failover_test/
  scenario-1-tunnel-1-down.md
  scenario-2-both-tunnels-up-ecmp.md
README.md
docs/ADR-bgp-over-vpn.md
```

**Learning Resources:**
- https://docs.aws.amazon.com/vpn/latest/s2svpn/VPNTunnels.html
- https://docs.aws.amazon.com/vpn/latest/s2svpn/SetUpVPNConnections.html
- BGP basics: https://www.cloudflare.com/learning/security/glossary/what-is-bgp/

---

### Lab 05: Route 53 Latency-Based Routing with Health Checks ⭐🎯
**Difficulty:** 🟡 Intermediate
**Time:** 3-4 hours
**Technologies:** Terraform, Route 53, health checks, multi-region (or simulated)
**Risk:** 🟢 LOW (costs pennies)
**Objective:** Build global traffic steering with automatic failover

**What You'll Build:**
- Route 53 Hosted Zone
- 3 A records with same name, different IPs (simulating 3 gateways/regions)
- Latency-based routing policy
- Health checks for each endpoint (HTTP or TCP)
- Low TTL (60s) for fast failover
- CloudWatch alarm on health check status
- Test from different geographic locations

**Success Criteria:**
- ✅ DNS returns different IP based on query source location
- ✅ Health check fails when endpoint is down → DNS stops returning that IP
- ✅ Health check recovers when endpoint restored → DNS adds it back
- ✅ Tested from at least 3 global locations (use public DNS resolvers)
- ✅ CloudWatch alarm fires when health check unhealthy

**Portfolio Location:**
`projects/p10-multi-region/route53-latency/` or `terraform/aws-route53-latency/`

**Files to Create:**
```
route53_zone.tf
route53_records.tf
health_checks.tf
cloudwatch_alarms.tf
test_endpoints/
  endpoint-1-app.py (simple Flask app returning "Gateway A")
  endpoint-2-app.py
  endpoint-3-app.py
test_results/
  dig-from-us-east.txt
  dig-from-eu-west.txt
  dig-from-ap-south.txt
  health-check-fail-screenshot.png
  dns-failover-screenshot.png
README.md
docs/runbook-health-check-failover-drill.md
```

**Learning Resources:**
- https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-policy-latency.html
- https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-failover.html

---

## Intermediate Labs (Week 1-2)

### Lab 06: Comprehensive VPN/BGP Monitoring Dashboard 🎯
**Difficulty:** 🟡 Intermediate
**Time:** 4-5 hours
**Technologies:** CloudWatch, Grafana (optional), synthetic probes, Lambda
**Risk:** 🟢 LOW
**Objective:** Build production-grade monitoring for network infrastructure

**What You'll Build:**
- CloudWatch dashboard with:
  - VPN tunnel state (UP/DOWN) over time
  - BGP session state
  - Bytes in/out per tunnel (stacked area chart)
  - Packet loss percentage
  - Synthetic probe success rate
  - Latency heatmap (P50/P95/P99)
- Lambda function for synthetic probes (ICMP ping, HTTP check)
- CloudWatch alarms for critical conditions
- SNS topic for alert notifications

**Success Criteria:**
- ✅ Dashboard updates in real-time
- ✅ Synthetic probes run every 1-5 minutes
- ✅ Alarms fire when tunnel down or BGP down
- ✅ Can detect issues before users report them
- ✅ Dashboard is presentation-ready (clean, labeled, professional)

**Portfolio Location:**
`projects/p04-ops-monitoring/vpn-bgp-monitoring/` or `dashboards/cloudwatch/`

**Files to Create:**
```
dashboard.json
synthetic_probe/
  lambda_function.py
  requirements.txt
terraform/
  cloudwatch_alarms.tf
  lambda.tf
  sns.tf
screenshots/
  dashboard-healthy.png
  dashboard-tunnel-down.png
  alarm-fired.png
README.md
docs/runbook-vpn-monitoring.md
```

**Learning Resources:**
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Dashboards.html
- https://aws.amazon.com/blogs/networking-and-content-delivery/monitor-your-aws-site-to-site-vpn-tunnels-with-amazon-cloudwatch/

---

### Lab 07: mTLS Control Plane with Private CA ⭐
**Difficulty:** 🟡 Intermediate-Advanced
**Time:** 5-6 hours
**Technologies:** OpenSSL or AWS ACM Private CA, Nginx or Flask app, certificate management
**Risk:** 🟢 LOW
**Objective:** Implement mutual TLS authentication for secure control plane

**What You'll Build:**
- Private Certificate Authority (easy-rsa or AWS ACM PCA)
- Server certificate for control plane API (with SANs)
- Client certificates for 2-3 simulated devices
- Sample control plane API (Flask/FastAPI) requiring mTLS
- Certificate rotation script
- Monitoring for certificate expiration

**Success Criteria:**
- ✅ Client with valid certificate can connect to API
- ✅ Client without certificate is rejected (connection refused)
- ✅ Client with expired/invalid certificate is rejected
- ✅ Can rotate server certificate without downtime
- ✅ Can revoke client certificate and verify access denied
- ✅ Expiration monitoring alerts 30 days before expiry

**Portfolio Location:**
`projects/06-homelab/PRJ-HOME-002/pki-lab/` or `projects/p16-zero-trust/mtls-demo/`

**Files to Create:**
```
ca/
  setup-ca.sh
  ca.crt
  ca.key (keep secure!)
server/
  generate-server-cert.sh
  server.crt
  server.key
  server-config.yaml (SANs list)
clients/
  generate-client-cert.sh
  device-001.crt
  device-001.key
  device-002.crt
  device-002.key
api/
  app.py (Flask app enforcing mTLS)
  requirements.txt
rotation/
  rotate-server-cert.sh
  rotate-client-cert.sh
monitoring/
  check-cert-expiration.py
test_results/
  valid-client-success.log
  no-client-cert-failure.log
  expired-cert-failure.log
README.md
docs/pki-design.md
docs/rotation-policy.md
```

**Learning Resources:**
- https://docs.aws.amazon.com/privateca/latest/userguide/
- https://jamielinux.com/docs/openssl-certificate-authority/
- https://medium.com/@awkwardferny/getting-started-with-mutual-tls-mtls-3b2b4e6d2e66

---

### Lab 08: Dual-Gateway Failover Architecture 🎯
**Difficulty:** 🔴 Advanced
**Time:** 6-8 hours
**Technologies:** Terraform, Transit Gateway, multiple VPNs, Route 53, BGP TE
**Risk:** 🟡 MEDIUM (complexity + cost ~$5/day)
**Objective:** Build production-grade multi-site HA architecture

**What You'll Build:**
- 2 simulated ground gateways (CGWs in different "locations")
- Each gateway has DX (simulated with VPN) + VPN backup
- Both connect to same Transit Gateway
- BGP traffic engineering (communities, local-pref) for path preference
- Route 53 latency routing with health checks to both gateways
- Comprehensive monitoring dashboard
- Failover drill runbook + execution evidence

**Success Criteria:**
- ✅ Both gateways operational simultaneously (50/50 or 70/30 traffic split)
- ✅ Gateway A failure → all traffic to Gateway B (< 2 min)
- ✅ BGP automatically converges without manual intervention
- ✅ DNS health checks detect failure and stop routing to failed gateway
- ✅ Gateway A recovery → traffic automatically rebalances
- ✅ Documented failover test with screenshots at each step

**Portfolio Location:**
`projects/p10-multi-region/dual-gateway/` or `terraform/kuiper-dual-gateway/`

**Files to Create:**
```
gateway_a/
  cgw.tf
  vpn_primary.tf
  vpn_backup.tf
  bgp_config.txt
gateway_b/
  cgw.tf
  vpn_primary.tf
  vpn_backup.tf
  bgp_config.txt
tgw/
  tgw.tf
  route_tables.tf
  attachments.tf
route53/
  records.tf
  health_checks.tf
monitoring/
  dashboard.json
  alarms.tf
docs/
  architecture-diagram.mmd
  bgp-traffic-engineering.md
  ADR-dual-gateway-design.md
  runbook-gateway-failover.md
test_results/
  baseline-both-gateways-up.md
  scenario-1-gateway-a-failure.md
  scenario-2-gateway-a-recovery.md
  screenshots/
    bgp-routes-before.png
    bgp-routes-during-failure.png
    bgp-routes-after-recovery.png
    dns-queries-failover.png
    traffic-dashboard-failover.png
README.md
```

**Learning Resources:**
- AWS reference architecture: https://aws.amazon.com/answers/networking/aws-multiple-data-center-ha-network-connectivity/
- BGP traffic engineering: https://www.cisco.com/c/en/us/support/docs/ip/border-gateway-protocol-bgp/13753-25.html

---

## Advanced Labs (Week 2, Optional)

### Lab 09: Prometheus + Alertmanager + Blackbox Exporter 🎯
**Difficulty:** 🟡 Intermediate
**Time:** 4-5 hours
**Technologies:** Prometheus, Alertmanager, Blackbox Exporter, Docker/Kubernetes
**Risk:** 🟢 LOW
**Objective:** Build open-source monitoring stack with intelligent alerting

**What You'll Build:**
- Prometheus server scraping metrics
- Blackbox Exporter for synthetic probes (HTTP, ICMP, TCP)
- Alerting rules (VPN down, BGP down, high latency)
- Alertmanager with routing, grouping, inhibition
- Grafana dashboards
- Test alert pipeline end-to-end

**Success Criteria:**
- ✅ Prometheus scraping metrics every 15-30s
- ✅ Blackbox Exporter probing VPN endpoint every 30s
- ✅ Alert fires when probe fails
- ✅ Alertmanager groups related alerts
- ✅ Inhibition rules prevent alert storm
- ✅ Alerts route to correct destination (critical → PagerDuty simulation, warning → Slack simulation)

**Portfolio Location:**
`projects/06-homelab/PRJ-HOME-002/monitoring/` or `observability/prometheus/`

**Files to Create:**
```
prometheus/
  prometheus.yml
  rules/
    kuiper-gateway.yml
    recording-rules.yml
alertmanager/
  alertmanager.yml
blackbox_exporter/
  blackbox.yml
docker-compose.yml
grafana/
  dashboards/
    vpn-overview.json
    bgp-status.json
test_results/
  alert-fires-screenshot.png
  alertmanager-grouping-screenshot.png
  grafana-dashboard-screenshot.png
docs/
  alerting-design.md
  runbook-prometheus-alerts.md
README.md
```

**Learning Resources:**
- https://prometheus.io/docs/prometheus/latest/getting_started/
- https://prometheus.io/docs/alerting/latest/alertmanager/
- https://github.com/prometheus/blackbox_exporter

---

### Lab 10: Terraform Modules for Reusable Components
**Difficulty:** 🟡 Intermediate
**Time:** 3-4 hours
**Technologies:** Terraform, module design, best practices
**Risk:** 🟢 LOW
**Objective:** Create reusable Terraform modules for Kuiper infrastructure patterns

**What You'll Build:**
- Module: `tgw-hub` (Transit Gateway + route tables + outputs)
- Module: `vpn-bgp-attachment` (CGW + VPN + TGW attachment + CloudWatch alarms)
- Module: `route53-latency` (hosted zone + latency records + health checks)
- Example usage of each module
- Module documentation

**Success Criteria:**
- ✅ Each module has inputs, outputs, README
- ✅ Modules are reusable (no hardcoded values)
- ✅ Example creates working infrastructure using modules
- ✅ `terraform validate` passes
- ✅ Can create 3 VPN connections using same module with different inputs

**Portfolio Location:**
`terraform/modules/` and `terraform/examples/`

**Files to Create:**
```
modules/
  tgw-hub/
    main.tf
    variables.tf
    outputs.tf
    README.md
  vpn-bgp-attachment/
    main.tf
    variables.tf
    outputs.tf
    README.md
  route53-latency/
    main.tf
    variables.tf
    outputs.tf
    README.md
examples/
  kuiper-dual-gateway-modular/
    main.tf (uses modules above)
    variables.tf
    outputs.tf
    README.md
docs/
  terraform-module-standards.md
README.md
```

**Learning Resources:**
- https://developer.hashicorp.com/terraform/language/modules
- https://developer.hashicorp.com/terraform/language/modules/develop

---

### Lab 11: Network Automation with Ansible + NAPALM
**Difficulty:** 🔴 Advanced
**Time:** 4-5 hours
**Technologies:** Ansible, NAPALM, network devices (GNS3/EVE-NG or real lab)
**Risk:** 🟡 MEDIUM (can break lab network if misconfigured)
**Objective:** Automate network device configuration and validation

**What You'll Build:**
- Ansible inventory with 2-3 routers/switches
- Playbook to deploy BGP configuration from YAML variables
- Playbook to collect device facts and validate state
- Playbook to generate compliance report
- Use NAPALM for device abstraction (works across vendors)

**Success Criteria:**
- ✅ Ansible can connect to all devices
- ✅ BGP config deployed successfully from YAML source-of-truth
- ✅ Configuration drift detected (manual change → Ansible reports difference)
- ✅ Compliance report generated (JSON or HTML)
- ✅ Rollback tested (deploy bad config, detect, rollback)

**Portfolio Location:**
`automation/ansible/network-automation/` or `projects/05-networking-datacenter/ansible/`

**Files to Create:**
```
inventory.yml
group_vars/
  all.yml
  routers.yml
host_vars/
  router-1.yml
  router-2.yml
playbooks/
  deploy-bgp-config.yml
  collect-facts.yml
  compliance-check.yml
  rollback.yml
templates/
  bgp-config.j2 (Jinja2 template)
test_results/
  before-deployment.txt
  after-deployment.txt
  compliance-report.json
  drift-detection.txt
README.md
docs/
  network-automation-design.md
  runbook-ansible-deployment.md
```

**Learning Resources:**
- https://docs.ansible.com/ansible/latest/network/index.html
- https://napalm.readthedocs.io/en/latest/
- https://github.com/networktocode/awesome-network-automation

---

### Lab 12: Multi-Region Architecture with TGW Peering
**Difficulty:** 🔴 Advanced
**Time:** 6-8 hours
**Technologies:** Terraform, multi-region TGW, inter-region routing, Route 53
**Risk:** 🟡 MEDIUM-HIGH (cost ~$10/day, complexity)
**Objective:** Build global-scale multi-region Kuiper architecture

**What You'll Build:**
- TGW in us-east-1 with 2 VPCs + 2 VPN gateways
- TGW in us-west-2 with 2 VPCs + 2 VPN gateways
- TGW peering attachment between regions
- Regional routing (prefer local, use remote as backup)
- Route 53 latency routing to nearest region
- Regional monitoring (no cross-region dependencies)
- Chaos test: Simulate full region failure

**Success Criteria:**
- ✅ Intra-region traffic stays in-region
- ✅ Cross-region traffic flows through TGW peering when needed
- ✅ Regional failure isolated (us-west-2 failure doesn't impact us-east-1)
- ✅ Route 53 automatically routes users to healthy region
- ✅ Documented region failover test with metrics

**Portfolio Location:**
`projects/p10-multi-region/tgw-peering/` or `terraform/kuiper-multi-region/`

**Files to Create:**
```
us-east-1/
  tgw.tf
  vpcs.tf
  vpn_gateways.tf
  route_tables.tf
  monitoring.tf
us-west-2/
  tgw.tf
  vpcs.tf
  vpn_gateways.tf
  route_tables.tf
  monitoring.tf
global/
  tgw_peering.tf
  route53.tf
  iam_roles.tf
docs/
  architecture-diagram.mmd
  regional-isolation-design.md
  ADR-multi-region-strategy.md
  runbook-region-failover-drill.md
test_results/
  baseline-both-regions-healthy.md
  scenario-us-east-1-failure.md
  dns-region-failover.png
  traffic-shift-metrics.png
README.md
```

**Learning Resources:**
- https://aws.amazon.com/blogs/networking-and-content-delivery/simplify-inter-region-traffic-management-with-aws-transit-gateway-inter-region-peering/
- https://docs.aws.amazon.com/vpc/latest/tgw/tgw-peering.html

---

### Lab 13: Chaos Engineering - Gateway Failure Drill 🎯
**Difficulty:** 🔴 Advanced
**Time:** 4-6 hours
**Technologies:** Chaos engineering, failure injection, monitoring, incident response
**Risk:** 🟡 MEDIUM (intentional breaking of systems)
**Objective:** Validate system resilience and incident response procedures

**What You'll Build:**
- Baseline monitoring dashboard (all systems healthy)
- Chaos scenario 1: VPN tunnel failure (manually down tunnel)
- Chaos scenario 2: BGP session down (firewall block TCP 179)
- Chaos scenario 3: Gateway application failure (health endpoint returns 503)
- Chaos scenario 4: Full gateway failure (shut down all connectivity)
- Incident response execution (detect, escalate, mitigate, recover)
- Post-drill report with findings and improvements

**Success Criteria:**
- ✅ Monitoring detects each failure within defined MTTD (2-5 min)
- ✅ Alerts fire correctly and route to right team
- ✅ Automatic failover occurs (BGP convergence, DNS failover)
- ✅ User impact measured and within SLO error budget
- ✅ Systems automatically recover when failure resolved
- ✅ Identified at least 3 improvements (monitoring gaps, runbook updates, etc.)

**Portfolio Location:**
`projects/p04-ops-monitoring/chaos-engineering/` or `docs/chaos-tests/`

**Files to Create:**
```
scenarios/
  01-vpn-tunnel-down/
    plan.md
    inject-failure.sh
    resolve-failure.sh
    timeline.md
    impact-analysis.md
    screenshots/
      monitoring-before.png
      alert-fired.png
      bgp-convergence.png
      monitoring-after.png
  02-bgp-session-down/
    ... (same structure)
  03-gateway-app-failure/
    ... (same structure)
  04-full-gateway-failure/
    ... (same structure)
findings/
  monitoring-gaps.md
  runbook-improvements.md
  automation-opportunities.md
post-drill-report.md
lessons-learned.md
README.md
```

**Learning Resources:**
- https://principlesofchaos.org/
- https://aws.amazon.com/blogs/architecture/chaos-engineering-on-aws/
- https://netflixtechblog.com/tagged/chaos-engineering

---

### Lab 14: BGP Traffic Engineering with Communities
**Difficulty:** 🔴 Advanced
**Time:** 4-5 hours
**Technologies:** BGP, route-maps, communities, traffic engineering
**Risk:** 🟡 MEDIUM (can cause routing issues if misconfigured)
**Objective:** Control traffic paths using BGP policy

**What You'll Build:**
- 2 VPN connections (primary and backup)
- BGP community scheme (65000:100 = primary, 65000:200 = backup)
- Route-maps to:
  - Tag routes with communities on advertisement
  - Set local-preference based on community on receipt
  - AS-PATH prepending for backup path
- Traffic validation showing preferred path
- Failover test showing backup path activation

**Success Criteria:**
- ✅ Traffic normally uses primary path (validated with flow logs)
- ✅ Communities visible in BGP route table
- ✅ Primary path has higher local-preference
- ✅ Backup path has prepended AS-PATH
- ✅ Primary failure → traffic shifts to backup within 60s
- ✅ Primary recovery → traffic shifts back within 60s

**Portfolio Location:**
`projects/p03-hybrid-network/bgp-traffic-engineering/` or `docs/network/bgp-te/`

**Files to Create:**
```
router_configs/
  primary_vpn_config.txt
  backup_vpn_config.txt
  route-map-examples.txt
bgp_policy/
  community-scheme.md
  route-map-design.md
test_results/
  show-ip-bgp-with-communities.txt
  show-ip-route-primary.txt
  traceroute-primary-path.txt
  traceroute-backup-path.txt
failover_test/
  scenario-1-primary-up.md (traffic on primary)
  scenario-2-primary-down.md (traffic shifted to backup)
  scenario-3-primary-restored.md (traffic shifted back)
  screenshots/
    flow-logs-primary.png
    flow-logs-backup.png
README.md
docs/
  bgp-traffic-engineering-guide.md
  ADR-bgp-policy-design.md
```

**Learning Resources:**
- https://www.cisco.com/c/en/us/support/docs/ip/border-gateway-protocol-bgp/26634-bgp-toc.html
- https://www.juniper.net/documentation/us/en/software/junos/bgp/topics/topic-map/bgp-traffic-engineering.html

---

### Lab 15: Comprehensive SLO-Based Monitoring & Alerting 🎯
**Difficulty:** 🔴 Advanced
**Time:** 5-6 hours
**Technologies:** SLI/SLO/SLA concepts, Prometheus, error budgets, burn rate alerts
**Risk:** 🟢 LOW
**Objective:** Implement production SRE monitoring practices

**What You'll Build:**
- SLO document defining targets (availability, latency, error rate)
- SLI measurements (synthetic probes, request success rate)
- Error budget calculation and tracking
- Burn rate alerts (page when burning budget too fast)
- Weekly SLO report generation
- Grafana SLO dashboard

**Success Criteria:**
- ✅ SLOs documented (e.g., 99.9% availability, P95 latency <50ms)
- ✅ SLIs measured accurately via synthetic probes
- ✅ Error budget calculated (0.1% = 43.8 min/month)
- ✅ Alert fires when burn rate exceeds threshold (not just "service down")
- ✅ Dashboard shows current error budget remaining
- ✅ Weekly report generated automatically

**Portfolio Location:**
`projects/p04-ops-monitoring/slo-monitoring/` or `docs/slo/`

**Files to Create:**
```
slo-definitions/
  kuiper-gateway-slos.yml
  calculation-methodology.md
prometheus/
  slo-rules.yml (recording rules for SLI)
  burn-rate-alerts.yml
dashboards/
  slo-overview.json
  error-budget.json
reports/
  weekly-slo-report-template.md
  generate-report.py
test_results/
  slo-dashboard-screenshot.png
  error-budget-tracking.png
  burn-rate-alert-screenshot.png
docs/
  slo-design-principles.md
  burn-rate-calculation.md
  how-to-set-slos.md
README.md
```

**Learning Resources:**
- Google SRE Book: https://sre.google/sre-book/service-level-objectives/
- https://landing.google.com/sre/workbook/chapters/implementing-slos/
- https://www.atlassian.com/incident-management/kpis/sla-vs-slo-vs-sli

---

## Lab Progression Recommendation

### Week 1 Focus (5 labs)
1. Lab 01: TC Netem (Day 1-2) ⭐
2. Lab 02: AWS VPC (Day 2-3) ⭐
3. Lab 03: Transit Gateway (Day 3-4) ⭐🎯
4. Lab 04: VPN with BGP (Day 4-6) ⭐🎯
5. Lab 05: Route 53 (Day 6-7) ⭐🎯

### Week 2 Focus (4-5 labs)
6. Lab 06: Monitoring Dashboard (Day 8-9) 🎯
7. Lab 07: mTLS Control Plane (Day 9-10) ⭐
8. Lab 08: Dual-Gateway Failover (Day 10-12) 🎯
9. Lab 09: Prometheus + Alertmanager (Day 12-13) 🎯
10. Lab 13: Chaos Engineering (Day 13-14) 🎯

### Optional (If Time Permits)
- Lab 10: Terraform Modules
- Lab 11: Ansible Automation
- Lab 12: Multi-Region TGW
- Lab 14: BGP Traffic Engineering
- Lab 15: SLO Monitoring

---

## Evidence Collection Checklist

For each lab, collect:
- ✅ **Architecture diagram** (draw.io, Mermaid, or hand-drawn + scanned)
- ✅ **Terraform/code** (in Git with commits)
- ✅ **Configuration files** (sanitized, no secrets)
- ✅ **Before/after screenshots**
- ✅ **Test results** (command outputs, logs, metrics)
- ✅ **README** explaining what you built and why
- ✅ **Lessons learned** document

---

## Interview Talking Points

Map labs to interview questions:
- **"Tell me about a time you built..."** → Lab 08 (Dual-Gateway Failover)
- **"How would you monitor..."** → Lab 06 (Monitoring Dashboard)
- **"Explain a complex technical concept..."** → Lab 04 (BGP over VPN) + Feynman explanation
- **"How do you handle failures..."** → Lab 13 (Chaos Engineering)
- **"Show me automation you've built..."** → Lab 10 (Terraform Modules) or Lab 11 (Ansible)

---

**Next Steps:**
1. Start with Lab 01 today (quick win, builds confidence)
2. Complete 1-2 labs per day average
3. Document as you go (don't leave documentation for later)
4. Take screenshots of EVERYTHING
5. Practice explaining each lab using Feynman method

Good luck! 🚀

---

**Last Updated:** 2025-11-10
**Document:** professional/interview-prep/kuiper/demos/LAB-INDEX.md
