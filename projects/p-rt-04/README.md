# Web App Exploitation Playbook

- **Role Category:** Red Team
- **Status:** Planned

## Executive Summary
Curated repeatable exploit chains for a legacy Java web stack, focusing on deserialization and SSRF risks.

## Scenario & Scope
Internal bug bounty mirror environment with outdated app server and S3-compatible storage.

## Responsibilities
- Catalog CVE coverage and detection gaps
- Develop SSRF-to-RCE chain with metadata abuse
- Package exploits into safe, repeatable scripts

## Tools & Technologies
- Burp Suite
- ysoserial
- ffuf
- Go
- Docker

## Architecture Notes
Isolated testing network with replayable fixtures; S3 bucket emulated via MinIO to avoid production access.

## Process Walkthrough
- Set up vulnerable app via docker-compose
- Enumerate endpoints and test deserialization gadgets
- Craft SSRF payloads targeting instance metadata
- Automate exploit chain with safety toggles

## Outcomes & Metrics
- Documented four exploit playbooks with mitigations
- Provided developer-safe repro scripts
- Enabled CI security gate for deserialization payload detection

## Evidence Links
- playbooks/p-rt-04/web-exploit-playbook.md

## Reproduction Steps
- Start the vulnerable stack with docker-compose
- Run the exploit scripts with sandbox credentials
- Capture logs for S3 access and metadata calls

## Interview Points
- Tradeoffs between patching and virtual patching
- Safe exploitation practices in shared labs
- How SSRF escalates in cloud environments
