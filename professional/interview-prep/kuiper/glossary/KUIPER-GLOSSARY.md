# Kuiper System/Network Administrator - Complete Glossary

**Purpose:** Master glossary of all acronyms, terms, and concepts for Kuiper ground infrastructure role
**Usage:** Reference during study, interview prep, and daily operations
**Last Updated:** 2025-11-10

---

## Table of Contents

1. [AWS Services & Components](#aws-services--components)
2. [Networking Protocols & Technologies](#networking-protocols--technologies)
3. [Satellite & RF Terms](#satellite--rf-terms)
4. [Security & PKI](#security--pki)
5. [Monitoring & Observability](#monitoring--observability)
6. [Automation & Infrastructure as Code](#automation--infrastructure-as-code)
7. [SRE & Operations](#sre--operations)
8. [General IT & Computing](#general-it--computing)

---

## AWS Services & Components

### ACM (AWS Certificate Manager)
Service for provisioning, managing, and deploying SSL/TLS certificates for AWS services.
**Example:** Using ACM to issue certificates for Application Load Balancers

### ACM PCA (AWS Certificate Manager Private Certificate Authority)
Managed private CA service for issuing internal certificates (not publicly trusted).
**Example:** Issuing mTLS certificates for Kuiper ground gateway control planes

### ALB (Application Load Balancer)
Layer 7 (HTTP/HTTPS) load balancer with advanced routing capabilities.
**Example:** Routing API traffic based on URL path to different backend services

### AWS Organizations
Multi-account management service for centrally governing multiple AWS accounts.
**Example:** Managing 50 AWS accounts with consolidated billing and SCPs

### CloudTrail
Service that logs all AWS API calls for auditing and compliance.
**Example:** Investigating who deleted a VPC by reviewing CloudTrail logs

### CloudWatch
AWS monitoring service for metrics, logs, alarms, and dashboards.
**Example:** Setting alarm when VPN tunnel goes down

### CloudWatch Logs
Centralized log collection and storage service within CloudWatch.
**Example:** Shipping application logs to CloudWatch Logs for search and analysis

### CloudWatch Synthetics
Service for creating canaries (synthetic monitors) that test APIs and websites.
**Example:** Running a synthetic HTTP check every 5 minutes to test gateway health endpoint

### DX (Direct Connect)
Dedicated private network connection from on-premises to AWS (1, 10, or 100 Gbps).
**Example:** 10 Gbps Direct Connect from ground gateway to AWS for high-bandwidth, low-latency connectivity

### EC2 (Elastic Compute Cloud)
Virtual machine service in AWS.
**Example:** Running application servers on EC2 instances

### IAM (Identity and Access Management)
AWS service for managing users, roles, and permissions.
**Example:** Creating least-privilege IAM role for Lambda function to read from S3

### KMS (Key Management Service)
Managed service for creating and controlling encryption keys.
**Example:** Encrypting secrets in Parameter Store using KMS customer-managed key

### Lambda
Serverless compute service that runs code in response to events.
**Example:** Running Python function every 5 minutes to check gateway health

### PrivateLink
Service for private connectivity between VPCs and AWS services without traversing public internet.
**Example:** Accessing S3 from VPC without internet gateway

### RAM (Resource Access Manager)
Service for sharing AWS resources across accounts in AWS Organizations.
**Example:** Sharing Transit Gateway with all accounts in the organization

### Route 53
AWS DNS service with advanced routing policies and health checks.
**Named after:** DNS port 53
**Example:** Using latency-based routing to send users to nearest gateway

### SCP (Service Control Policy)
IAM policy applied at AWS Organizations level to restrict permissions across accounts.
**Example:** SCP preventing deletion of CloudTrail logs in all accounts

### SNS (Simple Notification Service)
Pub/sub messaging service for sending notifications.
**Example:** Sending alarm notifications to PagerDuty via SNS

### SSM (Systems Manager)
Service for managing EC2 instances, patching, configuration, and remote access.
**Example:** Using SSM Session Manager for secure shell access without SSH keys

### TGW (Transit Gateway)
Regional cloud router that connects VPCs, VPN connections, and Direct Connect gateways.
**Think of it as:** Central hub for all your networks in a region
**Example:** Connecting 10 VPCs and 2 on-premises locations through single TGW

### VGW (Virtual Private Gateway)
Older VPN endpoint attached to a single VPC (mostly replaced by Transit Gateway for new deployments).
**Example:** Legacy VPN connection to a single VPC

### VPC (Virtual Private Cloud)
Isolated virtual network in AWS where you launch resources.
**Example:** Creating a VPC with public and private subnets for web application

### VPC Flow Logs
Capture information about IP traffic going to and from network interfaces in VPC.
**Example:** Investigating connection issues by analyzing Flow Logs

---

## Networking Protocols & Technologies

### ARP (Address Resolution Protocol)
Protocol that maps IP addresses to MAC addresses on local network.
**Example:** Your computer uses ARP to find the MAC address of the default gateway

### AS (Autonomous System)
Collection of IP networks under control of a single organization that presents a common routing policy.
**Example:** Amazon's AS16509 contains all Amazon IP ranges

### ASN (Autonomous System Number)
Unique identifier for an Autonomous System (public: 1-64511, private: 64512-65534).
**Example:** Using ASN 65001 for your on-premises network in BGP config

### AS-PATH
BGP attribute listing all ASNs a route has passed through (used for loop prevention and path selection).
**Example:** Route with AS-PATH "65001 65002 65003" passed through 3 networks

### AS-PATH Prepending
BGP technique of artificially lengthening AS-PATH to make a route less preferred (traffic engineering).
**Example:** Prepending your ASN twice to make backup VPN tunnel less preferred

### BGP (Border Gateway Protocol)
Exterior routing protocol that connects different autonomous systems (the protocol that runs the internet).
**Example:** Using BGP to exchange routes between ground gateway and AWS over VPN

### BGP Community
32-bit tag attached to BGP routes for signaling and policy control (format: ASN:value).
**Example:** Tagging backup routes with community 65000:100 to signal lower priority

### BGP Flap
BGP session or route going up and down repeatedly (sign of instability).
**Example:** Monitoring BGP flap count—alert if session flaps 3+ times in 10 minutes

### CIDR (Classless Inter-Domain Routing)
Method for allocating IP addresses and routing (format: x.x.x.x/prefix-length).
**Example:** 10.0.0.0/16 represents 65,536 IP addresses (10.0.0.0 to 10.0.255.255)

### DHCP (Dynamic Host Configuration Protocol)
Protocol for automatically assigning IP addresses and network config to devices.
**Example:** Your laptop gets an IP address from DHCP server when joining Wi-Fi

### DNS (Domain Name System)
Service that translates domain names to IP addresses.
**Example:** DNS resolves "gateway.kuiper.aws.com" to "1.2.3.4"

### Doppler Shift
Frequency change in signal due to relative motion between transmitter and receiver.
**Example:** Satellite moving toward ground station causes upward frequency shift requiring compensation

### DSCP (Differentiated Services Code Point)
6-bit field in IP header for marking packet priority (0-63, part of QoS).
**Example:** Marking BGP packets with DSCP 48 (CS6) for high priority treatment

### ECMP (Equal-Cost Multi-Path)
Load balancing traffic across multiple equal-cost routes.
**Example:** Using both VPN tunnels simultaneously with ECMP for 2x throughput

### FQDN (Fully Qualified Domain Name)
Complete domain name including hostname and all parent domains.
**Example:** "gateway-a.us-east-1.kuiper.aws.com" (vs just "gateway-a")

### HTTP (Hypertext Transfer Protocol)
Application protocol for web traffic (port 80, unencrypted).
**Example:** Accessing http://example.com

### HTTPS (HTTP Secure)
HTTP over TLS (port 443, encrypted).
**Example:** Accessing https://example.com with browser showing lock icon

### ICMP (Internet Control Message Protocol)
Network layer protocol for error messages and diagnostics (ping uses ICMP).
**Example:** Ping sends ICMP Echo Request, expects ICMP Echo Reply

### IP (Internet Protocol)
Core protocol for addressing and routing packets across networks.
**Example:** Every device on the internet has an IP address

### IPsec (Internet Protocol Security)
Suite of protocols for securing IP communications through encryption and authentication.
**Example:** Site-to-Site VPN uses IPsec to encrypt traffic over public internet

### IS-IS (Intermediate System to Intermediate System)
Link-state routing protocol commonly used in ISP networks (alternative to OSPF).
**Example:** Large ISPs often prefer IS-IS over OSPF for core routing

### Jitter
Variation in packet latency over time (inconsistent delays).
**Example:** Latency varies between 30ms and 50ms—jitter is 20ms

### Latency
Time delay for data to travel from source to destination (usually measured in milliseconds).
**Example:** LEO satellite round-trip latency typically 20-40ms

### Link-Local Address
IP addresses in 169.254.0.0/16 range used only on local network segment (not routable).
**Example:** AWS VPN BGP peering uses 169.254.x.x addresses for tunnel endpoints

### Local Preference
BGP attribute to prefer routes within your AS (higher value = more preferred, range 0-4,294,967,295, default 100).
**Example:** Set local-pref 200 on primary path, 100 on backup

### MACsec (Media Access Control Security)
IEEE standard for Layer 2 encryption on point-to-point links.
**Example:** Encrypting Direct Connect connection using MACsec (as DX is not encrypted by default)

### MPLS (Multiprotocol Label Switching)
High-performance packet forwarding using labels instead of IP lookups (used in ISP core networks).
**Example:** ISP uses MPLS L3VPN to provide isolated connectivity for enterprise customers

### MTU (Maximum Transmission Unit)
Largest packet size allowed on a network (standard Ethernet: 1500 bytes, jumbo frames: 9000 bytes).
**Example:** VPN overhead reduces MTU to ~1400 bytes, must tune application or use MSS clamping

### NAT (Network Address Translation)
Technique for remapping one IP address space to another by modifying packet headers.
**Example:** Home router NATs private IPs (192.168.x.x) to public ISP-provided IP

### NTP (Network Time Protocol)
Protocol for synchronizing computer clocks over networks.
**Example:** All servers sync time to NTP server to ensure accurate timestamps in logs

### OSPF (Open Shortest Path First)
Link-state interior routing protocol for enterprise networks.
**Example:** Enterprise campus network uses OSPF for dynamic routing between buildings

### QoS (Quality of Service)
Techniques for prioritizing certain traffic types over others.
**Example:** Prioritizing BGP control-plane traffic over user data to ensure routing stability during congestion

### RD (Route Distinguisher)
MPLS VPN identifier that makes VPN routes unique (format: ASN:number).
**Example:** RD 65000:1 for customer A's VPN, RD 65000:2 for customer B's VPN

### Route Map
BGP policy tool for filtering and modifying routes based on match conditions and actions.
**Example:** Route-map to prepend AS-PATH for routes received from backup VPN tunnel

### RT (Route Target)
MPLS VPN attribute controlling which VPN routes are imported/exported (format: ASN:number).
**Example:** Export RT 65000:100, import RT 65000:200

### SAN (Subject Alternative Name)
Field in X.509 certificate listing all names (DNS, IP) the certificate is valid for.
**Example:** Certificate with SAN: gateway-a.kuiper.com, 10.1.2.3, gateway-a.internal

### SSH (Secure Shell)
Protocol for secure remote terminal access (port 22).
**Example:** ssh user@gateway-a.kuiper.com

### TCP (Transmission Control Protocol)
Reliable, connection-oriented transport protocol with error correction and flow control.
**Example:** Web browsing, SSH, database connections use TCP

### TLS (Transport Layer Security)
Cryptographic protocol for secure communication over networks (successor to SSL).
**Example:** HTTPS uses TLS to encrypt web traffic

### TTL (Time To Live)
**In DNS:** Seconds to cache DNS record before re-querying.
**Example:** TTL 60 means cache DNS answer for 60 seconds
**In IP:** Hop count limit before packet is discarded.
**Example:** Packet with TTL 64 can traverse 64 routers before being dropped

### UDP (User Datagram Protocol)
Connectionless transport protocol without reliability guarantees (faster but less reliable than TCP).
**Example:** DNS, NTP, streaming video use UDP

### VLAN (Virtual Local Area Network)
Logical network segmentation at Layer 2 (tag: 1-4094).
**Example:** VLAN 10 for management, VLAN 20 for user traffic, VLAN 30 for guest Wi-Fi

### VPN (Virtual Private Network)
Encrypted tunnel over public or private networks for secure communication.
**Example:** Site-to-Site VPN connecting ground gateway to AWS

### VRF (Virtual Routing and Forwarding)
Network virtualization technique creating multiple routing tables on single router/switch.
**Example:** Separate VRF for management traffic vs user traffic on same physical router

### WebSocket
Protocol providing full-duplex communication over single TCP connection (port 80/443).
**Example:** Real-time chat application using WebSocket for instant message delivery

---

## Satellite & RF Terms

### Doppler Shift
Frequency change due to relative motion between satellite and ground station.
**Example:** Moving satellite causes frequency to increase (approaching) or decrease (receding)

### Ground Gateway / Ground Station / POP (Point of Presence)
Physical facility with RF equipment receiving satellite signals and converting to terrestrial network.
**Example:** Kuiper ground gateway in Oregon receiving Ka-band signals from LEO satellites and routing to AWS us-west-2

### Ka-band
Satellite frequency range (26.5-40 GHz) used for high-throughput communication.
**Why Ka-band:** Higher frequency = more bandwidth, but more susceptible to rain fade
**Example:** Kuiper terminals use Ka-band for uplink/downlink

### LEO (Low Earth Orbit)
Orbit altitude 340-1,200 km above Earth (lower than traditional GEO satellites).
**Benefits:** Lower latency (~20-40ms vs 600ms for GEO), less transmit power needed
**Challenges:** Satellites move quickly (need frequent handoffs), requires large constellation
**Example:** Kuiper, Starlink, OneWeb use LEO constellations

### OISL (Optical Inter-Satellite Link)
Laser-based communication links between satellites (space-to-space, not ground-to-space).
**Benefits:** High bandwidth (10+ Gbps), no ground infrastructure needed, less latency
**Example:** Kuiper satellite meshes use OISL to route traffic between satellites before downlinking

### Phased Array Antenna
Electronically steerable antenna (no moving parts) using multiple elements with phase shifts.
**Benefits:** Fast beam steering, simultaneous multiple beams, reliable (no motors)
**Example:** Kuiper customer terminals use phased arrays to track moving satellites

### RF (Radio Frequency)
Electromagnetic waves used for wireless communication (3 kHz to 300 GHz).
**Example:** Satellite uplink at 30 GHz (Ka-band RF signal)

### Weather Fade / Rain Fade
Signal attenuation caused by atmospheric conditions (especially rain) at high frequencies.
**Impact:** Higher at Ka-band than Ku-band; must design links with fade margin
**Example:** Heavy rainstorm causes 5 dB signal loss, requiring link budget to account for this

---

## Security & PKI

### CA (Certificate Authority)
Trusted entity that issues digital certificates.
**Example:** AWS ACM Private CA issuing certificates for internal services

### Certificate Pinning
Security technique of hardcoding expected certificate fingerprints in application to prevent MITM attacks.
**Example:** Mobile app pins gateway certificate fingerprint to reject fraudulent certificates

### IAM (Identity and Access Management)
System for controlling who can access what resources.
**Example:** IAM role allowing Lambda function to read S3 but not write

### JWT (JSON Web Token)
Compact token format for securely transmitting claims between parties (common in API auth).
**Example:** User logs in, receives JWT, includes JWT in API requests to prove identity

### Kerberos
Network authentication protocol using tickets to prove identity (common in Active Directory).
**Example:** Windows user logs in, receives Kerberos ticket, accesses file shares without re-entering password

### KMS (Key Management Service)
See AWS Services section

### Least Privilege
Security principle of granting minimum permissions necessary to perform a task.
**Example:** Application needs read-only S3 access—grant GetObject only, not PutObject or DeleteObject

### MFA (Multi-Factor Authentication)
Requiring 2+ authentication factors (something you know + something you have + something you are).
**Example:** Password + YubiKey, Password + SMS code, Password + fingerprint

### MITM (Man-in-the-Middle)
Attack where attacker intercepts and potentially modifies communication between two parties.
**Example:** Attacker on public Wi-Fi intercepts HTTPS if certificate validation is disabled

### mTLS (Mutual TLS)
Two-way TLS authentication where both client and server prove identity with certificates (not just server).
**Example:** Ground gateway and AWS control plane both present certificates to establish mTLS connection

### OIDC (OpenID Connect)
Authentication protocol built on OAuth 2.0 for identity verification.
**Example:** GitHub Actions using OIDC to authenticate to AWS without long-lived credentials

### PKI (Public Key Infrastructure)
Framework for creating, managing, and revoking digital certificates.
**Components:** CA, certificates, CRLs, OCSP, trust stores
**Example:** Corporate PKI for issuing employee laptop certificates

### Private CA
Certificate Authority that issues certificates for internal use (not publicly trusted by browsers).
**Example:** AWS ACM Private CA for Kuiper internal mTLS

### RBAC (Role-Based Access Control)
Access control based on user roles rather than individual permissions.
**Example:** All users in "NetworkAdmin" role can modify VPCs, but not IAM policies

### SAML (Security Assertion Markup Language)
XML-based standard for exchanging authentication and authorization data (common in enterprise SSO).
**Example:** Using SAML to federate corporate Active Directory logins to AWS Console

### SSH-CA (SSH Certificate Authority)
CA that issues SSH certificates instead of managing individual public keys.
**Example:** Issuing short-lived SSH certificates to employees instead of distributing SSH public keys to all servers

### SSSD (System Security Services Daemon)
Linux service for integrating with enterprise identity systems (Active Directory, LDAP).
**Example:** Linux servers using SSSD to authenticate users against Active Directory

### TLS (Transport Layer Security)
See Networking section

### Zero Trust
Security model assuming breach and verifying every request regardless of source location.
**Principles:** Never trust, always verify; least privilege; assume breach
**Example:** Requiring mTLS even for internal service-to-service communication

---

## Monitoring & Observability

### Alertmanager
Component of Prometheus ecosystem for routing, grouping, silencing, and throttling alerts.
**Example:** Routing critical alerts to PagerDuty, warning alerts to Slack

### Blackbox Exporter
Prometheus exporter for probing endpoints over HTTP, HTTPS, DNS, TCP, ICMP (synthetic monitoring).
**Example:** Blackbox exporter probing gateway health endpoint every 30 seconds

### Error Budget
Amount of unreliability permitted before violating SLO (100% - SLO target).
**Example:** 99.9% SLO = 0.1% error budget = 43.8 minutes downtime per month

### Exporter
Service that exposes metrics in Prometheus format for scraping.
**Common exporters:** node_exporter (Linux), windows_exporter, blackbox_exporter, snmp_exporter
**Example:** Node exporter exposing CPU, memory, disk metrics from Linux server

### Grafana
Open-source dashboard and visualization platform supporting multiple data sources.
**Example:** Grafana dashboard showing VPN tunnel status, BGP routes, and synthetic probe results

### Inhibition (Alertmanager)
Suppressing alerts based on presence of other alerts (alert hierarchy).
**Example:** If "GatewayDown" fires, inhibit "VPNTunnelDown" for same gateway (root cause already alerted)

### Label (Prometheus)
Key-value pair for identifying metrics (e.g., job="vpn", instance="gw-a", region="us-east-1").
**Example:** Querying cpu_usage{job="gateway",region="us-east-1"} for specific metrics

### Loki
Log aggregation system by Grafana (like Prometheus but for logs).
**Key difference from ELK:** Indexes labels, not content—cheaper and faster for high volume
**Example:** Shipping all gateway logs to Loki, querying by labels {job="gateway", level="error"}

### MTBF (Mean Time Between Failures)
Average time between failures (reliability metric).
**Example:** MTBF of 8,760 hours = average 1 failure per year

### MTTR (Mean Time To Repair/Resolve)
Average time to fix an issue after detection.
**Example:** MTTR of 15 minutes = on average, incidents are resolved within 15 min of detection

### MTTD (Mean Time To Detect)
Average time to detect an issue after it occurs.
**Example:** MTTD of 2 minutes = alerts typically fire within 2 min of problem starting

### P50 / P95 / P99 (Percentiles)
**P50 (Median):** 50% of measurements are better than this value
**P95:** 95% of measurements are better than this value (5% are worse)
**P99:** 99% of measurements are better than this value (1% are worse)
**Example:** Latency P95 = 45ms means 95% of requests complete in ≤45ms

### Prometheus
Open-source monitoring system and time-series database.
**Model:** Pull-based scraping of metrics from exporters
**Example:** Prometheus scraping VPN metrics every 30 seconds, evaluating alert rules

### PromQL (Prometheus Query Language)
Query language for retrieving and manipulating Prometheus metrics.
**Example:** rate(http_requests_total[5m]) calculates HTTP request rate over 5 minutes

### SLI (Service Level Indicator)
Quantitative measure of service behavior (e.g., latency, availability, error rate).
**Example:** SLI = successful synthetic probes / total synthetic probes

### SLO (Service Level Objective)
Target value or range for an SLI (internal goal).
**Example:** SLO = 99.9% availability (43.8 min downtime allowed per month)

### SLA (Service Level Agreement)
Contractual commitment with consequences for violation (customer-facing).
**Example:** SLA = 99.5% uptime, violation triggers service credits

### Synthetic Monitoring / Synthetic Probe
Automated test simulating user behavior to validate system functionality.
**Example:** HTTP probe every minute checking gateway API responds with 200 OK

### TSDB (Time-Series Database)
Database optimized for timestamp + value data (e.g., Prometheus, InfluxDB).
**Example:** Prometheus TSDB storing cpu_usage value with timestamp every 15 seconds

---

## Automation & Infrastructure as Code

### Ansible
Configuration management and orchestration tool using YAML playbooks (agentless, SSH-based).
**Example:** Ansible playbook deploying VPN config to 50 routers

### Configuration Drift
Divergence between intended configuration and actual deployed state.
**Example:** Engineer manually changed firewall rule—now differs from Terraform state (drift)

### HEREDOC (Here Document)
Multi-line string input method in shell scripting.
**Example:**
```bash
cat <<EOF
Line 1
Line 2
EOF
```

### IaC (Infrastructure as Code)
Managing infrastructure through code and version control instead of manual processes.
**Benefits:** Repeatable, auditable, testable, documented
**Example:** Terraform code defining VPCs, subnets, VPN connections

### Idempotent
Operation that produces same result regardless of how many times it's executed.
**Example:** terraform apply is idempotent—running twice doesn't create duplicate resources

### Jinja2
Templating engine used by Ansible and other tools.
**Example:** Jinja template generating router configs from YAML variables

### Module (Terraform)
Reusable Terraform configuration component.
**Example:** Transit Gateway module defining TGW, route tables, attachments—reused across regions

### NAPALM (Network Automation and Programmability Abstraction Layer with Multivendor support)
Python library providing unified API for network device automation.
**Example:** Using NAPALM to get interface status from Cisco, Juniper, Arista with same code

### Netmiko
Python library for SSH automation to network devices.
**Example:** Python script using Netmiko to run show commands on 100 routers

### Playbook (Ansible)
YAML file defining automation tasks.
**Example:** Playbook deploying VPN config, running validation tests, rolling back on failure

### State File (Terraform)
JSON file tracking resources Terraform manages (critical for updates/deletes).
**Example:** terraform.tfstate stores ID of every VPC, subnet, route table created

### Terraform
Infrastructure as Code tool using declarative HCL (HashiCorp Configuration Language).
**Example:** Terraform creating AWS VPC, subnets, Transit Gateway, VPN connections

### YAML (YAML Ain't Markup Language)
Human-readable data serialization language (used by Ansible, Kubernetes, CI/CD).
**Example:**
```yaml
users:
  - name: alice
    role: admin
  - name: bob
    role: viewer
```

---

## SRE & Operations

### Blameless Postmortem
Incident review focused on learning and improving systems, not blaming individuals.
**Example:** Postmortem identifies monitoring gap that allowed incident, results in improved alerting

### Blast Radius
Scope of potential impact from a change or failure.
**Example:** Change to Transit Gateway has blast radius of 50 VPCs and all on-prem connectivity

### CAB (Change Advisory Board)
Group reviewing and approving high-risk changes.
**Example:** CAB reviews network change plan before approving execution

### Chaos Engineering
Deliberately injecting failures to test system resilience and uncover weaknesses.
**Example:** Randomly terminating EC2 instances to test auto-scaling and failover

### Error Budget
See Monitoring & Observability section

### Game Day
Scheduled exercise simulating failures to practice incident response.
**Example:** Monthly Game Day simulating region failure to test runbooks

### Incident
Unplanned disruption or degradation of service.
**Severity levels:** P0/Critical (total outage), P1/High (major degradation), P2/Medium, P3/Low
**Example:** VPN tunnel down affecting 50% of users = P1 incident

### On-Call
Being available to respond to incidents outside normal work hours.
**Rotation:** Primary, secondary, escalation
**Example:** Weekly on-call rotation for network team

### Postmortem / Post-Incident Review / RCA (Root Cause Analysis)
Detailed analysis after an incident documenting what happened, why, and how to prevent recurrence.
**Sections:** Timeline, impact, root cause, action items
**Example:** Postmortem after BGP outage identifies BGP timer misconfiguration

### RFO (Reason for Outage)
Report explaining why an outage occurred (usually customer-facing summary).
**Example:** RFO sent to customers explaining 2-hour outage was due to fiber cut

### Runbook
Step-by-step operational procedure for common tasks or incident response.
**Example:** VPN Tunnel Down runbook: check tunnel state, check BGP, check firewall, escalate if still down

### Soak Period / Soak Time
Monitoring period after a change before declaring success.
**Typical:** 15-30 minutes
**Example:** After VPN config change, monitoring for 30 min to catch delayed issues

### Toil
Repetitive, automatable operational work with no lasting value.
**Goal:** Reduce toil through automation
**Example:** Manually updating firewall rules (toil) → Automated via Terraform (reduced toil)

---

## General IT & Computing

### AD (Active Directory)
Microsoft's directory service for Windows domain networks (user/computer management, authentication).
**Example:** Corporate employees log in to Windows PCs using Active Directory credentials

### API (Application Programming Interface)
Interface allowing software to communicate with other software.
**Example:** REST API for querying gateway status via HTTP GET /api/v1/status

### Automation
Using code/tools to perform tasks without human intervention.
**Example:** Automated certificate rotation every 60 days

### Bash
Unix shell and command language (Bourne Again Shell).
**Example:** Bash script to backup configs nightly

### CICD (Continuous Integration / Continuous Deployment)
Automated pipeline for testing and deploying code changes.
**Example:** Git push → automated tests → automated deploy to production

### CLI (Command Line Interface)
Text-based interface for interacting with systems (opposite of GUI).
**Example:** AWS CLI command: aws ec2 describe-instances

### Containerization
Packaging application with dependencies into portable container image (Docker, Kubernetes).
**Example:** Running Prometheus in Docker container

### Cron / Crontab
Unix time-based job scheduler.
**Example:** Cron job running backup script every night at 2 AM

### CSV (Comma-Separated Values)
Simple file format for tabular data.
**Example:** Exporting VPN metrics to CSV for analysis in Excel

### Docker
Platform for building, shipping, and running containers.
**Example:** Docker image containing application + OS dependencies

### ENV (Environment Variable)
Variable set in operating system environment, accessible by running processes.
**Example:** export AWS_REGION=us-east-1

### Git
Distributed version control system for tracking code changes.
**Example:** Git repository tracking Terraform code with branches for features

### GPO (Group Policy Object)
Windows policy configuration applied to users/computers in Active Directory.
**Example:** GPO enforcing screen lock after 15 minutes of inactivity

### GUI (Graphical User Interface)
Visual interface using windows, icons, buttons (opposite of CLI).
**Example:** AWS Console vs AWS CLI

### JSON (JavaScript Object Notation)
Lightweight data interchange format (human-readable, machine-parseable).
**Example:**
```json
{"name": "gateway-a", "status": "healthy", "tunnels": 2}
```

### Kubernetes / K8s
Container orchestration platform for automating deployment, scaling, and management.
**Example:** Kubernetes cluster running 100 microservice containers

### LDAP (Lightweight Directory Access Protocol)
Protocol for accessing and maintaining directory services (user/group info).
**Example:** Applications authenticating users against corporate LDAP server

### Load Balancer
Device/service distributing traffic across multiple backend servers.
**Example:** ALB distributing HTTP requests across 5 EC2 instances

### Log Aggregation
Centrally collecting logs from distributed systems for search and analysis.
**Tools:** Elasticsearch, Loki, Splunk, CloudWatch Logs
**Example:** All gateway logs shipped to Loki for centralized search

### Python
High-level programming language commonly used for automation and data processing.
**Example:** Python script using Boto3 to query AWS API

### REST (Representational State Transfer)
Architectural style for APIs using HTTP methods (GET, POST, PUT, DELETE).
**Example:** REST API: GET /gateways returns list of gateways

### SNMP (Simple Network Management Protocol)
Protocol for monitoring and managing network devices (routers, switches, firewalls).
**Example:** Polling router via SNMP to get interface utilization metrics

### SQL (Structured Query Language)
Language for managing relational databases.
**Example:** SELECT * FROM users WHERE role='admin'

### ZFS
Advanced filesystem with features like snapshots, replication, checksums (common in NAS/storage).
**Example:** TrueNAS using ZFS for data integrity and snapshot-based backups

---

## Kuiper-Specific Terminology

### Control Plane (Kuiper Context)
Management and configuration traffic (terminal registration, software updates, telemetry, admin APIs).
**Security:** Must use mTLS, isolated VLANs, MFA
**Example:** Terminal sending telemetry to ground gateway control plane API

### Customer Terminal
User equipment (phased array antenna + modem) receiving satellite broadband service.
**Example:** Residential customer installing terminal on roof to get Kuiper internet

### Data Plane (Kuiper Context)
User traffic (web browsing, video streaming, downloads).
**Example:** User watching Netflix via Kuiper satellite → data plane traffic

### Ground Gateway Operator / Sys/NetAdmin (Kuiper Role)
Engineer responsible for operating ground gateways, AWS connectivity, monitoring, automation, and incident response.
**Responsibilities:** VPN/BGP management, PKI/mTLS, observability, change control, on-call
**Example:** You, preparing for this interview!

---

## Usage Tips

1. **Print this glossary** and review it daily
2. **Create flashcards** for terms you struggle with
3. **Use it during study** - when you see an acronym, look it up immediately
4. **Reference during labs** - helps reinforce learning
5. **Practice explaining terms** using Feynman method (teach someone else)

---

## Related Documents

- **Cheat Sheets:** `/professional/interview-prep/kuiper/cheat-sheets/`
- **Learning Path:** `/professional/interview-prep/kuiper/learning-paths/`
- **Demo Index:** `/professional/interview-prep/kuiper/demos/`
- **Warm-Up Questions:** `/professional/interview-prep/kuiper/warm-ups/`

---

**Total Terms:** 200+
**Last Updated:** 2025-11-10
**Maintained By:** Sam Jackson
